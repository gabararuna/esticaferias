import streamlit as st
import pandas as pd
import holidays
from datetime import date, timedelta
import json
import os

# --- Configuração da Página ---
# Mantemos o page_title apenas para a aba do navegador
st.set_page_config(page_title="Estica Férias", page_icon="🏖️", layout="wide")

# --- Estilo Glassmorfismo e Cores ---
st.markdown("""
<style>
    :root {
        --glass-bg: rgba(255, 255, 255, 0.06);
        --glass-border: rgba(255, 255, 255, 0.2);
        --vivid-action: #2E86C1;
        --vivid-hover: #3498DB;
    }
    
    /* Padding reduzido para encostar no topo do seu Iframe */
    .block-container {
        padding-top: 0rem !important;
        padding-bottom: 1rem !important;
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

    .stButton>button[kind="primary"] {
        background-color: var(--vivid-action) !important;
        border-color: var(--vivid-action) !important;
        width: 100%;
        font-weight: 700 !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
    
    /* Esconder o Header padrão do Streamlit para um look mais clean */
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
if 'selected_ops' not in st.session_state:
    st.session_state['selected_ops'] = []
if 'saldo_ferias' not in st.session_state:
    st.session_state['saldo_ferias'] = 0
if 'd_ini' not in st.session_state:
    st.session_state['d_ini'] = date.today()
if 'd_fim' not in st.session_state:
    st.session_state['d_fim'] = date.today() + timedelta(days=365)

# --- Funções de Dados (Cidades e Feriados) ---
@st.cache_data
def load_cities():
    file_path = os.path.join(os.path.dirname(__file__), 'cidades_ordenadas.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {'MA': ['São Luís']}

@st.cache_data
def load_municipal_holidays():
    file_path = os.path.join(os.path.dirname(__file__), 'feriados_municipais.json')
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

STATE_CITIES = load_cities()
MUNICIPAL_HOLS = load_municipal_holidays()

# --- Funções Lógicas (Páscoa e Cálculos) ---
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
            (easter - timedelta(days=48), "Carnaval"),
            (easter - timedelta(days=2), "Sexta-Feira Santa"),
            (easter + timedelta(days=60), "Corpus Christi")
        ]
        for dt, name in moveable:
            if start_date <= dt <= end_date and dt not in history_dates:
                hols_list.append({"Data": dt, "Tipo": "Móvel", "Nome": name})
                history_dates.add(dt)

    city_hols = MUNICIPAL_HOLS.get(state, {}).get(city, {})
    for dt_str, name in city_hols.items():
        try:
            parts = dt_str.split('/')
            day, month = int(parts[0]), int(parts[1])
            for y in years:
                dt = date(y, month, day)
                if start_date <= dt <= end_date and dt not in history_dates:
                    hols_list.append({"Data": dt, "Tipo": "Municipal", "Nome": name})
                    history_dates.add(dt)
        except: pass

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
    # Regra CLT: não iniciar 2 dias antes de folga
    if (dt + timedelta(days=1)) in hols or (dt + timedelta(days=1)) in rests: return False
    if (dt + timedelta(days=2)) in hols or (dt + timedelta(days=2)) in rests: return False
    for r in st.session_state['selected_ops']:
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
    return (actual_end - actual_start).days + 1, actual_start, actual_end

def get_clt_lengths(saldo):
    roteiro = st.session_state['selected_ops']
    has_14 = any(r['length'] >= 14 for r in roteiro)
    opt = []
    if not roteiro:
        opt.extend([saldo] + list(range(14, saldo - 4)) + list(range(5, saldo - 13)))
    else:
        if has_14 or saldo >= 14: opt.append(saldo)
        if has_14: opt.extend(range(5, saldo - 4))
        else: opt.extend(range(14, saldo - 4))
    return sorted(list(set([o for o in opt if 5 <= o <= saldo])))

# --- Interface (Steps) ---

if st.session_state['step'] == 1:
    st.subheader("Configurações do Período")
    d_ini = st.date_input("Início da busca", key="d_ini", format="DD/MM/YYYY")
    d_fim = st.date_input("Fim da busca", key="d_fim", format="DD/MM/YYYY")
    uf = st.selectbox("Estado", list(STATE_CITIES.keys()), index=9)
    cid = st.selectbox("Cidade", STATE_CITIES[uf], index=0)
    total = st.number_input("Saldo de dias de férias", 5, 30, 30)
    
    if st.button("Avançar", type="primary"):
        st.session_state['config_base'] = {'start': d_ini, 'end': d_fim, 'uf': uf, 'city': cid, 'total': total}
        st.session_state['saldo_ferias'] = total
        st.session_state['step'] = 2
        st.rerun()

elif st.session_state['step'] == 2:
    conf = st.session_state['config_base']
    st.subheader("Gerenciar Feriados")
    hols_raw = get_complete_holidays(conf['start'], conf['end'], conf['uf'], conf['city'])
    df_hols = pd.DataFrame(hols_raw)
    if not df_hols.empty:
        df_hols['Ativo'] = True
        df_hols['Data_Exibição'] = df_hols['Data'].apply(lambda x: x.strftime('%d/%m/%y'))
        edited = st.data_editor(df_hols[['Data_Exibição', 'Tipo', 'Nome', 'Ativo']], use_container_width=True, hide_index=True)
        
        st.session_state['feriados_final'] = {
            pd.to_datetime(row['Data_Exibição'], dayfirst=True).date(): row['Nome'] 
            for _, row in edited.iterrows() if row['Ativo']
        }
    
    c1, c2 = st.columns(2)
    if c1.button("Voltar"): st.session_state['step'] = 1; st.rerun()
    if c2.button("Avançar", type="primary"): st.session_state['step'] = 3; st.rerun()

elif st.session_state['step'] == 3:
    conf = st.session_state['config_base']
    saldo = st.session_state['saldo_ferias']
    
    st.metric("Saldo Restante", f"{saldo} dias")

    # Exibir selecionados
    for idx, sel in enumerate(st.session_state['selected_ops']):
        cols = st.columns([5, 1])
        cols[0].write(f"✅ **{sel['length']} dias** em {sel['start'].strftime('%d/%m')} (Ganhando {sel['total']} dias)")
        if cols[1].button("🗑️", key=f"del_{idx}"):
            st.session_state['saldo_ferias'] += sel['length']
            st.session_state['selected_ops'].pop(idx)
            st.rerun()

    if saldo >= 5:
        st.write("---")
        rests = get_rest_days(conf['start'], conf['end'])
        hols = st.session_state['feriados_final']
        lens = get_clt_lengths(saldo)
        
        sugestoes = []
        curr = conf['start']
        while curr <= conf['end']:
            if is_valid_start(curr, hols, rests):
                for l in lens:
                    if curr + timedelta(days=l-1) <= conf['end']:
                        t, vs, ve = calc_gain(curr, l, hols, rests, conf['end'])
                        overlap = any(not (ve < r['v_start'] or vs > r['v_end']) for r in st.session_state['selected_ops'])
                        if not overlap:
                            sugestoes.append({'start': curr, 'end': curr+timedelta(days=l-1), 'length': l, 'total': t, 'gain': t-l, 'v_start': vs, 'v_end': ve})
            curr += timedelta(days=1)
        
        sugestoes.sort(key=lambda x: x['gain'], reverse=True)
        for i, s in enumerate(sugestoes[:8]):
            c = st.columns([5, 1])
            c[0].write(f"📅 **{s['length']} dias** ({s['start'].strftime('%d/%m')}) → Ganhe **{s['total']} dias** de folga")
            if c[1].button("➕", key=f"add_{i}"):
                st.session_state['selected_ops'].append(s)
                st.session_state['saldo_ferias'] -= s['length']
                st.rerun()

    if st.button("Reiniciar Tudo"):
        st.session_state['step'] = 1
        st.session_state['selected_ops'] = []
        st.rerun()
