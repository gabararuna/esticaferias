import streamlit as st
import pandas as pd
import holidays
from datetime import date, timedelta

# --- Configuração da Página ---
st.set_page_config(page_title="Estica Férias", page_icon="🏖️", layout="wide")

# --- Estilo Glassmorfismo e Cores (Vivid/Moderno/Polido) ---
st.markdown("""
<style>
    /* Suporte a Dark/Light Mode dinâmico */
    :root {
        --glass-bg: rgba(255, 255, 255, 0.06);
        --glass-border: rgba(255, 255, 255, 0.2);
        --vivid-action: #2E86C1;
        --vivid-hover: #3498DB;
    }
    
    /* Container Principal */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2rem !important;
        max-width: 1300px !important; /* Aumentado para comportar os banners laterais */
    }

    /* Ocultar banners VERTICAIS em telas menores que 1150px */
    @media (max-width: 1150px) {
        .ad-vertical {
            display: none !important;
            height: 0 !important;
        }
        .ad-horizontal {
            display: block !important;
        }
    }

    /* Esconder banner HORIZONTAL no desktop */
    .ad-horizontal {
        display: none;
    }

    /* Estilo dos containers centralizados */
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

    /* Botões de Ação Vividos e Padronizados */
    .stButton>button[kind="primary"], .stButton>button[kind="secondary"] {
        padding: 0.6rem 1.5rem !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        transition: all 0.2s ease-in-out !important;
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
    }
    
    /* Espaçamento das métricas */
    div[data-testid="stMetricValue"] {
        font-size: 1.1rem !important;
    }
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

# --- Função de Anúncios ---
def render_adsense(ad_id="placeholder", ad_type="vertical"):
    """
    Renderiza o bloco de anúncios do Google Adsense.
    - vertical: Skycraper (160x600)
    - horizontal: Banner (padrão responsivo)
    """
    if ad_type == "vertical":
        w, h = "160px", "600px"
        div_class = "ad-vertical"
        # Skycraper style
        ins_style = f"display:inline-block;width:{w};height:{h};background:rgba(255,255,255,0.05);border-radius:8px;"
        fallback_style = f"width: {w}; height: {h}; background: linear-gradient(180deg, rgba(46,134,193,0.1) 0%, rgba(0,0,0,0) 100%);"
    else:
        w, h = "100%", "100px"
        div_class = "ad-horizontal"
        # horizontal style
        ins_style = f"display:block;width:{w};height:{h};background:rgba(255,255,255,0.05);border-radius:8px;"
        fallback_style = f"width: {w}; height: {h}; background: linear-gradient(90deg, rgba(46,134,193,0.1) 0%, rgba(0,0,0,0) 100%);"

    html_code = f"""
    <div class="{div_class}" style="width: {w}; margin: auto; position: relative; overflow: hidden; border-radius: 8px;">
        <!-- Script Oficial AdSense -->
        <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1234567890123456" crossorigin="anonymous"></script>
        
        <ins class="adsbygoogle"
             style="{ins_style}"
             data-ad-client="ca-pub-1234567890123456"
             data-ad-slot="1234567890"
             data-ad-test="on"></ins>
        
        <script>
             (adsbygoogle = window.adsbygoogle || []).push({{}});
        </script>

        <!-- Fallback Visual -->
        <div style="position: absolute; top:0; left:0; {fallback_style}
                    border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
                    display: flex; flex-direction: column; align-items: center; justify-content: center;
                    color: #aaa; font-family: sans-serif; pointer-events: none; text-align: center;">
            <div style="font-weight: bold; color: #2E86C1; font-size: 13px;">Google Ads</div>
            <div style="font-size: 9px; opacity: 0.6;">{ad_type.upper()} TEST MODE</div>
        </div>
    </div>
    """
    st.components.v1.html(html_code, height=int(h.replace('px','')) + 20)

import json
import os

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
    """Cálculo da Páscoa (Meeus/Jones/Butcher)."""
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
    """Gera lista de feriados classificada."""
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

    # --- Feriados Municipais ---
    city_hols = MUNICIPAL_HOLS.get(state, {}).get(city, {})

    for dt_str, name in city_hols.items():
        try:
            parts = dt_str.split('/')
            if len(parts) == 2:
                day, month = int(parts[0]), int(parts[1])
                for y in years:
                    dt = date(y, month, day)
                    if start_date <= dt <= end_date:
                        if dt not in history_dates:
                            hols_list.append({"Data": dt, "Tipo": "Municipal", "Nome": name})
                            history_dates.add(dt)
                        else:
                            # Update existing holiday type to clarify it's also Municipal
                            for h in hols_list:
                                if h['Data'] == dt:
                                    h['Tipo'] = "Municipal"
            elif len(parts) == 3:
                day, month, y_val = int(parts[0]), int(parts[1]), int(parts[2])
                dt = date(y_val, month, day)
                if start_date <= dt <= end_date:
                    if dt not in history_dates:
                        hols_list.append({"Data": dt, "Tipo": "Municipal", "Nome": name})
                        history_dates.add(dt)
                    else:
                        for h in hols_list:
                            if h['Data'] == dt:
                                h['Tipo'] = "Municipal"
        except Exception as e:
            pass

    # Sort chronological
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
    for r in st.session_state['roteiro']:
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
    roteiro = st.session_state['roteiro']
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

st.title("🏖️ Estica Férias")

if st.session_state['step'] == 1:
    ad_left, main_col, ad_right = st.columns([12, 76, 12])
    with ad_left:
        render_adsense("banner_esq_home", "vertical")
        
    with main_col:
        st.subheader("Configurações do Período")
        # ... (rest of code stays the same)
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
        
        # Banner horizontal mobile (visível apenas abaixo de 1150px via CSS)
        render_adsense("banner_mobile_home", "horizontal")

    with ad_right:
        render_adsense("banner_dir_home", "vertical")

elif st.session_state['step'] == 2:
    conf = st.session_state['config_base']
    ad_left, main_col, ad_right = st.columns([12, 76, 12])
    
    with ad_left:
        render_adsense("banner_esq_step2", "vertical")

    with main_col:
        st.subheader("Gerenciar Feriados")
        # ... (code truncated)
        edited = st.data_editor(disp_df, num_rows="dynamic", use_container_width=True, hide_index=True)
        # ... (logic skip)
        col1, col2 = st.columns(2)
        if col1.button("Voltar", key="btn_voltar_2", use_container_width=True):
            st.session_state['step'] = 1
            st.rerun()
        if col2.button("Avançar Etapa", key="btn_avancar_2", type="primary", use_container_width=True):
            st.session_state['step'] = 3
            st.rerun()
        
        # Banner horizontal mobile
        render_adsense("banner_mobile_step2", "horizontal")

    with ad_right:
        render_adsense("banner_dir_step2", "vertical")

elif st.session_state['step'] == 3:
    # Configurações para a etapa 3
    conf = st.session_state['config_base']
    saldo = st.session_state['saldo_ferias']
    total_days = conf.get('total', saldo)
    used_days = total_days - saldo

    # Inicializar container de roteiro se não existir
    if 'selected_ops' not in st.session_state:
        st.session_state['selected_ops'] = []

    ad_left, main_col, ad_right = st.columns([12, 76, 12])
    
    with ad_left:
        render_adsense("banner_esq_step3", "vertical")

    with main_col:
        st.subheader("Seleção de Períodos")
        # Exibir saldo como usado/total
        st.metric("Saldo Utilizado", f"{used_days}/{total_days} dias")

        # ---- Períodos já selecionados ----
        if st.session_state['selected_ops']:
            st.markdown("### Períodos Escolhidos")
            for idx, sel in enumerate(st.session_state['selected_ops']):
                sel_title = f"**Tirando {sel['length']} dias desde {sel['start'].strftime('%d/%m/%y')} você ganha +{sel['gain']} dias!**"
                sel_ferias = f"Empresa: {sel['start'].strftime('%d/%m/%y')} - {sel['end'].strftime('%d/%m/%y')}"
                sel_real = f"Real: {sel['v_start'].strftime('%d/%m/%y')} - {sel['v_end'].strftime('%d/%m/%y')}"
                
                c_sel, c_del = st.columns([5, 1])
                with c_sel:
                    st.markdown(f"""
                    <div style="line-height: 1.4; margin-top: -5px;">
                        <strong>Tirando {sel['length']} dias desde {sel['start'].strftime('%d/%m/%y')} você ganha +{sel['gain']} dias!</strong><br>
                        <span style="font-size: 0.85rem; opacity: 0.7;">{sel_ferias}<br>{sel_real}</span>
                    </div>
                    """, unsafe_allow_html=True)
                with c_del:
                    if st.button("-", key=f"remove_op_{idx}", use_container_width=True):
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
                                # Evitar sobreposição
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
                        label_title = f"Tirando {op['length']} dias desde {op['start'].strftime('%d/%m/%y')} você ganha +{op['gain']} dias!"
                        label_ferias = f"Empresa: {op['start'].strftime('%d/%m/%y')} a {op['end'].strftime('%d/%m/%y')}"
                        label_real = f"Real: {op['v_start'].strftime('%d/%m/%y')} a {op['v_end'].strftime('%d/%m/%y')}"
                        
                        cols = st.columns([5, 1])
                        with cols[0]:
                            st.markdown(f"""
                            <div style="line-height: 1.4; margin-top: -5px;">
                                <strong>{label_title}</strong><br>
                                <span style="font-size: 0.85rem; opacity: 0.7;">{label_ferias}<br>{label_real}</span>
                            </div>
                            """, unsafe_allow_html=True)
                        with cols[1]:
                            if st.button("+", key=f"sel_btn_{idx}_{op['start']}", use_container_width=True):
                                st.session_state['selected_ops'].append(op)
                                st.session_state['saldo_ferias'] -= op['length']
                                st.rerun()
                        st.write("") 
        
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
            
        if st.button("Reiniciar Planejamento", key="restart_all", use_container_width=True):
            st.session_state['step'] = 1
            st.session_state['selected_ops'] = []
            st.session_state['saldo_ferias'] = total_days
            st.rerun()

        # Banner horizontal mobile
        render_adsense("banner_mobile_step3", "horizontal")

    with ad_right:
        render_adsense("banner_dir_step3", "vertical")

