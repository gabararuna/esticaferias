import streamlit as st
import pandas as pd
import holidays
from datetime import date, timedelta
import json
import os

# --- Configuração da Página ---
st.set_page_config(page_title="Estica Férias", page_icon="🏖️", layout="wide")

# --- Estilo Glassmorfismo e Cores (Vivid/Moderno/Polido) ---
st.markdown("""
<style>
    :root {
        --glass-bg: rgba(255, 255, 255, 0.06);
        --glass-border: rgba(255, 255, 255, 0.2);
        --vivid-action: #2E86C1;
        --vivid-hover: #3498DB;
    }
    
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1000px !important;
    }

    div[data-testid="stVerticalBlock"] > div > div.stBox, 
    div.stExpander, div[data-testid="stMetric"], .stDataEditor {
        background-color: var(--glass-bg) !important;
        backdrop-filter: blur(12px) !important;
        -webkit-backdrop-filter: blur(12px) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        margin-bottom: 0.5rem !important;
    }

    /* Botões de Ação - Ajustados para funcionarem como Cards Limpos */
    .stButton>button[kind="primary"], .stButton>button[kind="secondary"] {
        padding: 0.8rem 1rem !important;
        font-weight: 600 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
        height: auto !important;
    }
    .stButton>button[kind="primary"] {
        background-color: var(--vivid-action) !important;
        border-color: var(--vivid-action) !important;
    }
    .stButton>button[kind="secondary"] {
        background-color: transparent !important;
        border-color: var(--glass-border) !important;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        border-color: var(--vivid-hover) !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
    
    /* Esconder o Header/Footer padrão do Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# --- Inicialização do Session State ---
if 'step' not in st.session_state:
    st.session_state['step'] = 1
if 'config_base' not in st.session_state:
    st.session_state['config_base'] = {}
if 'feriados_final' not in st.session_state:
    st.session_state['feriados_final'] = {}
if 'roteiro' not in st.session_state:
    st.session_state['roteiro'] = []
if 'saldo_ferias' not in st.session_state:
    st.session_state['saldo_ferias'] = 0
if 'manual_end_date' not in st.session_state:
    st.session_state['manual_end_date'] = False
if 'd_ini' not in st.session_state:
    st.session_state['d_ini'] = date.today()
if 'd_fim' not in st.session_state:
    st.session_state['d_fim'] = date.today() + timedelta(days=365)

# --- Cidades (Carregamento Dinâmico) ---
@st.cache_data
def load_cities():
    file_path = os.path.join(os.path.dirname(__file__), 'cidades_ordenadas.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        st.error(f"Erro ao carregar cidades: {e}")
        return {'SP': ['São Paulo']}

@st.cache_data
def load_municipal_holidays_v3():
    file_path = os.path.join(os.path.dirname(__file__), 'feriados_municipais.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        return {}

STATE_CITIES = load_cities()
MUNICIPAL_HOLS = load_municipal_holidays_v3()

# --- Funções Lógicas ---
def get_easter(year):
    a, b = year % 19, year // 100
    c, d, e = year % 100, b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)

def get_complete_holidays(start_date, end_date, state, city):
    hols_list = []
    years = list(range(start_date.year, end_date.year + 1))
    br_hols = holidays.Brazil(years=years, subdiv=state)
    nacional_fixed = holidays.Brazil(years=years)
    
    history_dates = set()
    
    for dt, name in br_hols.items():
        if start_date <= dt <= end_date:
            tipo = "Nacional" if dt in nacional_fixed else "Estadual"
            hols_list.append({"Data": dt, "Tipo": tipo, "Nome": name})
            history_dates.add(dt)
            
    for y in years:
        easter = get_easter(y)
        moveable = [
            (easter - timedelta(days=48), "Carnaval (Segunda)"),
            (easter - timedelta(days=47), "Carnaval (Terça)"),
            (easter - timedelta(days=46), "Quarta-Feira de Cinzas"),
            (easter - timedelta(days=2), "Sexta-Feira Santa"),
            (easter + timedelta(days=60), "Corpus Christi")
        ]
        for dt, name in moveable:
            if start_date <= dt <= end_date and dt not in history_dates:
                hols_list.append({"Data": dt, "Tipo": "Nacional (Móvel)", "Nome": name})
                history_dates.add(dt)

    city_hols = MUNICIPAL_HOLS.get(state, {}).get(city, {})

    for dt_str, name in city_hols.items():
        try:
            parts = dt_str.split('/')
            if len(parts) == 2:
                day, month = int(parts[0]), int(parts[1])
                for y in years:
                    dt = date(y, month, day)
                    if start_date <= dt <= end_date and dt not in history_dates:
                        hols_list.append({"Data": dt, "Tipo": "Municipal", "Nome": name})
                        history_dates.add(dt)
            elif len(parts) == 3:
                day, month, y_val = int(parts[0]), int(parts[1]), int(parts[2])
                dt = date(y_val, month, day)
                if start_date <= dt <= end_date and dt not in history_dates:
                    hols_list.append({"Data": dt, "Tipo": "Municipal", "Nome": name})
                    history_dates.add(dt)
        except Exception:
            pass

    hols_list.sort(key=lambda x: x['Data'])
    return hols_list

def get_rest_days(start_date, end_date):
    rest = set()
    curr = start_date
    while curr <= end_date:
        if curr.weekday() in [5, 6]: rest.add(curr)
        curr += timedelta(days=1)
    return rest

def is_valid_start(dt, hols, rests):
    if dt in hols or dt in rests: return False
    if (dt + timedelta(days=1)) in hols or (dt + timedelta(days=1)) in rests: return False
    if (dt + timedelta(days=2)) in hols or (dt + timedelta(days=2)) in rests: return False
    for r in st.session_state.get('selected_ops', []):
        if r['start'] <= dt <= r['end']: return False
    return True

def calc_gain(start_dt, length, hols, rests, max_date):
    official_end = start_dt + timedelta(days=length - 1)
    all_non_work = set(hols.keys()) | rests
    
    actual_start = start_dt
    while (actual_start - timedelta(days=1)) in all_non_work:
        actual_start -= timedelta(days=1)
        
    actual_end = official_end
    while (actual_end + timedelta(days=1)) in all_non_work and (actual_end + timedelta(days=1)) <= max_date:
        actual_end += timedelta(days=1)
        
    total_days = (actual_end - actual_start).days + 1
    return total_days, actual_start, actual_end

def get_clt_lengths(saldo):
    roteiro = st.session_state.get('selected_ops', [])
    has_14 = any(r['length'] >= 14 for r in roteiro)
    count = len(roteiro)
    opt = []
    if count == 0:
        opt.append(saldo)
        for i in range(14, saldo - 4): opt.append(i)
        for i in range(5, saldo - 13): opt.append(i)
    elif count == 1:
        if has_14 or saldo >= 14: opt.append(saldo)
        if has_14:
            for i in range(5, saldo - 4): opt.append(i)
        else:
            for i in range(14, saldo - 4): opt.append(i)
            for i in range(5, saldo - 13): opt.append(i)
    elif count == 2:
        if has_14 or saldo >= 14: opt.append(saldo)
    return sorted(list(set(opt)))

# --- Interface ---

if st.session_state['step'] == 1:
    st.subheader("Configurações do Período")
    
    def on_change_ini():
        if not st.session_state.get('manual_end_date', False) and st.session_state.get('d_ini') is not None:
            st.session_state['d_fim'] = st.session_state['d_ini'] + timedelta(days=365)

    def on_change_fim():
        st.session_state['manual_end_date'] = True
        
    d_ini = st.date_input("Início da busca", key="d_ini", on_change=on_change_ini, format="DD/MM/YYYY")
    d_fim = st.date_input("Fim da busca", key="d_fim", on_change=on_change_fim, format="DD/MM/YYYY")
    uf = st.selectbox("Estado", list(STATE_CITIES.keys()), index=9)
    cities = STATE_CITIES[uf]
    cid = st.selectbox("Cidade", cities, index=0)
    total = st.number_input("Saldo de dias de férias", 5, 30, 30)
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Avançar Etapa", type="primary", use_container_width=True):
        if d_fim <= d_ini: st.error("Data final deve ser após a inicial.")
        else:
            st.session_state['config_base'] = {'start': d_ini, 'end': d_fim, 'uf': uf, 'city': cid, 'total': total}
            st.session_state['saldo_ferias'] = total
            st.session_state['step'] = 2
            st.rerun()

elif st.session_state['step'] == 2:
    conf = st.session_state['config_base']
    
    st.subheader("Gerenciar Feriados")
    st.write(f"Período: {conf['start'].strftime('%d/%m/%y')} a {conf['end'].strftime('%d/%m/%y')}")
    
    hols_raw = get_complete_holidays(conf['start'], conf['end'], conf['uf'], conf['city'])
    df_hols = pd.DataFrame(hols_raw)
    if not df_hols.empty:
        df_hols['Ativo'] = df_hols['Nome'].apply(lambda x: x != "Feriado Municipal")
        df_hols['Data_Show'] = df_hols['Data'].apply(lambda x: x.strftime('%d/%m/%y'))
        disp_df = df_hols[['Data_Show', 'Tipo', 'Nome', 'Ativo']].copy()
        disp_df.columns = ['Data', 'Tipo', 'Nome', 'Ativo']
    else:
        disp_df = pd.DataFrame(columns=['Data', 'Tipo', 'Nome', 'Ativo'])
        
    edited = st.data_editor(disp_df, num_rows="dynamic", use_container_width=True, hide_index=True)
    
    st.session_state['feriados_final'] = {}
    for i, row in edited.iterrows():
        if row['Ativo']:
            if isinstance(row['Data'], str):
                try: 
                    d_obj = pd.to_datetime(row['Data'], dayfirst=True).date()
                    st.session_state['feriados_final'][d_obj] = row['Nome']
                except: pass
            else: st.session_state['feriados_final'][row['Data']] = row['Nome']
            
    col1, col2 = st.columns(2)
    if col1.button("Voltar", key="btn_voltar_2", use_container_width=True):
        st.session_state['step'] = 1
        st.rerun()
    if col2.button("Avançar Etapa", key="btn_avancar_2", type="primary", use_container_width=True):
        st.session_state['step'] = 3
        st.rerun()

elif st.session_state['step'] == 3:
    conf = st.session_state['config_base']
    saldo = st.session_state['saldo_ferias']
    total_days = conf.get('total', saldo)
    used_days = total_days - saldo

    if 'selected_ops' not in st.session_state:
        st.session_state['selected_ops'] = []

    st.subheader("Seleção de Períodos")
    st.metric("Saldo Utilizado", f"{used_days}/{total_days} dias")

    # ---- Períodos já selecionados (Cards Clicáveis Limpos) ----
    if st.session_state['selected_ops']:
        st.markdown("### Períodos Escolhidos")
        for idx, sel in enumerate(st.session_state['selected_ops']):
            # Texto limpo sem emojis ou quebras
            label_btn = f"Tirando {sel['length']} dias em {sel['start'].strftime('%d/%m/%y')} você folga {sel['total']} dias!"
            
            if st.button(label_btn, key=f"remove_op_{idx}", use_container_width=True):
                op_to_remove = st.session_state['selected_ops'].pop(idx)
                st.session_state['saldo_ferias'] += op_to_remove['length']
                st.rerun()
        st.write("") 

    if saldo > 0:
        with st.spinner("Buscando combinações mais eficientes..."):
            rests = get_rest_days(conf['start'], conf['end'])
            hols = st.session_state['feriados_final']
            lens = get_clt_lengths(saldo)
            
            res = []
            curr = conf['start']
            while curr <= conf['end']:
                if is_valid_start(curr, hols, rests):
                    for l in lens:
                        if curr + timedelta(days=l-1) <= conf['end']:
                            total, v_start, v_end = calc_gain(curr, l, hols, rests, conf['end'])
                            overlap = any(not (v_end < r['v_start'] or v_start > r['v_end']) 
                                         for r in st.session_state['selected_ops'])
                            
                            if not overlap:
                                res.append({
                                    'start': curr, 'end': curr + timedelta(days=l-1),
                                    'length': l, 'total': total, 'gain': total - l,
                                    'efficiency': (total - l) / l,
                                    'v_start': v_start, 'v_end': v_end
                                })
                curr += timedelta(days=1)
            
            res.sort(key=lambda x: (x['efficiency'], x['gain']), reverse=True)
            
            if not res:
                st.warning("Poxa! Nenhuma opção encontrada respeitando as regras da CLT para esse saldo.")
            else:
                st.markdown("### Sugestões para seu saldo restante")
                for idx, op in enumerate(res[:12]):
                    # Texto limpo sem emojis ou quebras
                    label_btn = f"Tirando {op['length']} dias em {op['start'].strftime('%d/%m/%y')} você folga {op['total']} dias!"
                    
                    if st.button(label_btn, key=f"sel_btn_{idx}_{op['start']}", use_container_width=True):
                        st.session_state['selected_ops'].append(op)
                        st.session_state['saldo_ferias'] -= op['length']
                        st.rerun()
                    
    # Resumo Final
    if st.session_state['selected_ops']:
        st.write("") 
        st.write("") 
        st.subheader("🏖️ Itinerário Confirmado")
        
        t_spent = sum(r['length'] for r in st.session_state['selected_ops'])
        t_total = sum(r['total'] for r in st.session_state['selected_ops'])
        
        st.info(f"✨ **Incrível!** Você usou **{t_spent} dias** do seu saldo para garantir **{t_total} dias** de folga real!")
        
        itinerario_data = [{
            "Empresa": f"{r['start'].strftime('%d/%m/%y')} - {r['end'].strftime('%d/%m/%y')}",
            "Férias": f"{r['length']}d",
            "Real": f"{r['v_start'].strftime('%d/%m/%y')} a {r['v_end'].strftime('%d/%m/%y')}",
            "Folga": f"{r['total']}d",
            "Ganho": f"+{r['gain']}d"
        } for r in sorted(st.session_state['selected_ops'], key=lambda k: k['start'])]
        st.table(itinerario_data)
        
    if st.button("Reiniciar Planejamento", key="restart_all", use_container_width=True, type="primary"):
        st.session_state['step'] = 1
        st.session_state['selected_ops'] = []
        st.session_state['saldo_ferias'] = total_days
        st.rerun()
