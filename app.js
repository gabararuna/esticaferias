import * as logic from './logic.js';

// --- Welcome Screen ---
(function setupWelcome() {
    const screen = document.getElementById('welcome-screen');
    const cta = document.getElementById('welcome-cta');
    const orb = document.getElementById('welcome-orb');

    if (!screen || !cta) return;

    document.addEventListener('mousemove', (e) => {
        if (screen.classList.contains('fade-out')) return;
        orb.style.left = `${(e.clientX / window.innerWidth) * 100}%`;
        orb.style.top = `${(e.clientY / window.innerHeight) * 100}%`;
    });

    cta.addEventListener('click', () => {
        screen.classList.add('fade-out');
        setTimeout(() => {
            screen.style.display = 'none';
        }, 500);
    });
})();

// --- Constants ---
const CAPITALS = {
    'AC': 'Rio Branco', 'AL': 'Maceió', 'AP': 'Macapá', 'AM': 'Manaus',
    'BA': 'Salvador', 'CE': 'Fortaleza', 'DF': 'Brasília', 'ES': 'Vitória',
    'GO': 'Goiânia', 'MA': 'São Luís', 'MT': 'Cuiabá', 'MS': 'Campo Grande',
    'MG': 'Belo Horizonte', 'PA': 'Belém', 'PB': 'João Pessoa', 'PR': 'Curitiba',
    'PE': 'Recife', 'PI': 'Teresina', 'RJ': 'Rio de Janeiro', 'RN': 'Natal',
    'RS': 'Porto Alegre', 'RO': 'Porto Velho', 'RR': 'Boa Vista', 'SC': 'Florianópolis',
    'SP': 'São Paulo', 'SE': 'Aracaju', 'TO': 'Palmas'
};

// --- Global State ---
const state = {
    step: 1,
    config: {
        start: null,
        end: null,
        uf: 'MA',
        city: 'São Luís',
        total: 30
    },
    data: {
        cities: {},
        municipalHolidays: {}
    },
    holidays: [],
    activeHolidays: {},
    selectedOps: [],
    saldo: 30
};

// --- Initialization ---
async function init() {
    try {
        const [citiesResp, holsResp] = await Promise.all([
            fetch('cidades.json').then(r => r.json()),
            fetch('feriados_municipais.json').then(r => r.json())
        ]);
        state.data.cities = citiesResp;
        state.data.municipalHolidays = holsResp;

        populateStates();
        setupEventListeners();

        const now = new Date();
        const nextYear = new Date();
        nextYear.setFullYear(now.getFullYear() + 1);

        const startInput = document.getElementById('input-start');
        const endInput = document.getElementById('input-end');
        setYmd(startInput, now);
        setYmd(endInput, nextYear);

        setTimeout(tryGeolocation, 1000);

    } catch (err) {
        console.error("Initialization failed:", err);
    }
}

function parseYmd(str) {
    if (!str) return null;
    const [y, m, d] = str.split('-').map(Number);
    return new Date(y, m - 1, d);
}

function setYmd(input, date) {
    if (!date) {
        input.value = '';
        return;
    }
    input.value = logic.toYmd(date);
}

function toggleHero(visible) {
    const hero = document.getElementById('hero-section');
    if (visible) {
        hero.classList.remove('hidden');
        setTimeout(() => hero.classList.remove('fade-out'), 10);
    } else {
        hero.classList.add('fade-out');
        setTimeout(() => hero.classList.add('hidden'), 600);
    }
}

function populateStates() {
    const selector = document.getElementById('select-state');
    const ufs = Object.keys(state.data.cities).sort();
    ufs.forEach(uf => {
        const opt = document.createElement('option');
        opt.value = uf;
        opt.textContent = uf;
        if (uf === 'MA') opt.selected = true;
        selector.appendChild(opt);
    });
    populateCities('MA', 'São Luís');
}

function populateCities(uf, defaultCity = null) {
    const selector = document.getElementById('select-city');
    selector.innerHTML = '<option value="">Selecione...</option>';
    if (!uf) return;

    const cities = state.data.cities[uf] || [];
    const targetCity = defaultCity || CAPITALS[uf] || cities[0];

    cities.sort().forEach(city => {
        const opt = document.createElement('option');
        opt.value = city;
        opt.textContent = city;
        if (city.toLowerCase() === targetCity.toLowerCase()) opt.selected = true;
        selector.appendChild(opt);
    });
}

async function tryGeolocation() {
    if (!navigator.geolocation) return;

    navigator.geolocation.getCurrentPosition(async (pos) => {
        const { latitude, longitude } = pos.coords;
        try {
            const resp = await fetch(`https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&zoom=10`);
            const data = await resp.json();
            const addr = data.address || {};
            const stateFull = addr.state || '';
            const cityFound = addr.city || addr.town || addr.municipality || '';

            const UF_MAP = {
                'Acre': 'AC', 'Alagoas': 'AL', 'Amapá': 'AP', 'Amazonas': 'AM',
                'Bahia': 'BA', 'Ceará': 'CE', 'Distrito Federal': 'DF', 'Espírito Santo': 'ES',
                'Goiás': 'GO', 'Maranhão': 'MA', 'Mato Grosso': 'MT', 'Mato Grosso do Sul': 'MS',
                'Minas Gerais': 'MG', 'Paraíba': 'PA', 'Paraíba': 'PB', 'Paraná': 'PR',
                'Pernambuco': 'PE', 'Piauí': 'PI', 'Rio de Janeiro': 'RJ', 'Rio Grande do Norte': 'RN',
                'Rio Grande do Sul': 'RS', 'Rondônia': 'RO', 'Roraima': 'RR', 'Santa Catarina': 'SC',
                'São Paulo': 'SP', 'Sergipe': 'SE', 'Tocantins': 'TO'
            };

            const uf = UF_MAP[stateFull];
            if (uf) {
                document.getElementById('select-state').value = uf;
                populateCities(uf, cityFound);
            }
        } catch (e) { console.warn("Geolocation reverse mapping failed", e); }
    });
}

function setupEventListeners() {
    const startInput = document.getElementById('input-start');
    const endInput = document.getElementById('input-end');
    const daysRange = document.getElementById('input-days');
    const daysLabel = document.getElementById('days-value');
    const cltWarning = document.getElementById('clt-warning');
    const partialWarning = document.getElementById('partial-sale-warning');

    startInput.onchange = () => {
        const date = parseYmd(startInput.value);
        if (date) {
            const newEnd = new Date(date);
            newEnd.setFullYear(newEnd.getFullYear() + 1);
            setYmd(endInput, newEnd);
        }
    };

    document.getElementById('select-state').onchange = (e) => populateCities(e.target.value);

    daysRange.oninput = (e) => {
        const val = parseInt(e.target.value);
        daysLabel.textContent = val;

        if (val < 20) {
            cltWarning.classList.remove('hidden');
            partialWarning.classList.add('hidden');
        } else if (val < 30 && val >= 21) {
            cltWarning.classList.add('hidden');
            partialWarning.classList.remove('hidden');
        } else {
            cltWarning.classList.add('hidden');
            partialWarning.classList.add('hidden');
        }
    };

    // Mobile Menu Toggle
    const menuBtn = document.getElementById('mobile-menu-btn');
    const closeBtn = document.getElementById('close-mobile-menu');
    const mobileMenu = document.getElementById('mobile-menu');

    if (menuBtn && mobileMenu) {
        menuBtn.onclick = () => mobileMenu.classList.add('open');
    }
    if (closeBtn && mobileMenu) {
        closeBtn.onclick = () => mobileMenu.classList.remove('open');
    }

    document.getElementById('btn-next-1').onclick = () => goToStep2();
}

// --- Step Transitions ---

async function goToStep2() {
    const startInput = parseYmd(document.getElementById('input-start').value);
    const endInput = parseYmd(document.getElementById('input-end').value);
    const uf = document.getElementById('select-state').value;
    const city = document.getElementById('select-city').value;
    const total = parseInt(document.getElementById('input-days').value);

    if (!startInput || !endInput || !uf || !city) {
        alert("Preencha todos os campos!");
        return;
    }

    state.config = { start: startInput, end: endInput, uf, city, total };
    state.saldo = total;

    const hols = await logic.getCompleteHolidays(
        startInput, endInput, uf, city, state.data.municipalHolidays
    );
    state.holidays = hols.sort((a, b) => a.date - b.date);

    state.step = 2;
    toggleHero(false);
    renderStep2();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderStep2() {
    const container = document.getElementById('step-2');
    container.classList.remove('hidden');
    document.getElementById('step-1').classList.add('hidden');

    container.innerHTML = `
        <div class="flex items-center justify-between mb-8">
            <div class="flex items-center gap-4">
                <div class="w-10 h-10 rounded-full bg-[#00BFA5]/10 flex items-center justify-center text-[#00BFA5] text-sm font-medium">02</div>
                <h3 class="text-xl">Gerenciar Feriados</h3>
            </div>
            <button id="btn-back-2" class="text-[11px] uppercase tracking-widest text-white/40 hover:text-white flex items-center gap-2 transition-colors">
                <i data-lucide="arrow-left" class="w-3 h-3"></i> Voltar
            </button>
        </div>

        <p class="text-sm text-white/40 mb-8 font-light">Desmarque os feriados que você deseja desconsiderar no cálculo.</p>

        <div class="space-y-4 mb-10">
            ${state.holidays.length > 0 ? state.holidays.map((h, i) => `
                <div class="flex items-center justify-between p-5 bg-white/[0.02] border border-white/5 rounded-xl hover:border-[#00BFA5]/20 transition-colors">
                    <div class="flex flex-col gap-1">
                        <span class="text-sm font-medium text-white">${h.name}</span>
                        <span class="text-[10px] text-white/30 uppercase tracking-wider">${h.date.toLocaleDateString('pt-BR')} • ${h.type}</span>
                    </div>
                    <label class="premium-toggle">
                        <input type="checkbox" value="${i}" checked class="hol-toggle">
                        <span class="toggle-slider"></span>
                    </label>
                </div>
            `).join('') : '<p class="text-center py-10 text-white/30 text-sm italic font-light">Nenhum feriado encontrado neste período.</p>'}
        </div>

        <button id="btn-next-2" class="w-full glass-btn btn-primary py-4 text-sm uppercase tracking-widest">
            Avançar
        </button>
    `;

    document.getElementById('btn-back-2').onclick = () => {
        state.step = 1;
        toggleHero(true);
        document.getElementById('step-2').classList.add('hidden');
        document.getElementById('step-1').classList.remove('hidden');
    };

    document.getElementById('btn-next-2').onclick = () => {
        const toggles = document.querySelectorAll('.hol-toggle');
        const activeIdx = Array.from(toggles).filter(t => t.checked).map(t => parseInt(t.value));
        state.activeHolidays = activeIdx.reduce((acc, idx) => {
            const h = state.holidays[idx];
            acc[h.date.toISOString().split('T')[0]] = h.name;
            return acc;
        }, {});

        goToStep3();
    };

    lucide.createIcons();
}

function goToStep3() {
    state.step = 3;
    renderStep3();
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

function renderStep3() {
    const container = document.getElementById('step-3');
    container.classList.remove('hidden');
    document.getElementById('step-2').classList.add('hidden');

    const rests = logic.getRestDays(state.config.start, state.config.end);
    const lengths = logic.getCltLengths(state.saldo, state.selectedOps);

    const options = [];
    let curr = new Date(state.config.start);
    while (curr <= state.config.end) {
        if (logic.isValidStart(curr, state.activeHolidays, rests, state.selectedOps)) {
            for (const l of lengths) {
                const end = new Date(curr);
                end.setDate(end.getDate() + l - 1);

                if (end <= state.config.end) {
                    const { totalDays, actualStart, actualEnd } = logic.calcGain(curr, l, state.activeHolidays, rests, state.config.end);

                    const overlap = state.selectedOps.some(sel => {
                        return !(actualEnd < sel.actualStart || actualStart > sel.actualEnd);
                    });

                    if (!overlap) {
                        options.push({
                            start: new Date(curr),
                            end: new Date(end),
                            length: l,
                            total: totalDays,
                            gain: totalDays - l,
                            efficiency: (totalDays - l) / l,
                            actualStart,
                            actualEnd
                        });
                    }
                }
            }
        }
        const next = new Date(curr);
        next.setDate(next.getDate() + 1);
        curr = next;
    }

    options.sort((a, b) => b.efficiency - a.efficiency || b.gain - a.gain);

    const usedDays = state.config.total - state.saldo;
    const totalFolga = state.selectedOps.reduce((acc, op) => acc + op.total, 0);
    const abonoDays = 30 - state.config.total;
    const requestedDays = state.selectedOps.reduce((acc, op) => acc + op.length, 0);

    const isDone = state.saldo < 0.1;

    let metricsHtml = '';
    if (isDone) {
        metricsHtml = `
            <div class="p-6 bg-white/[0.02] border border-[#00BFA5]/20 rounded-2xl space-y-6 shadow-2xl animate-fade-in">
                <h4 class="text-[10px] font-medium text-[#00BFA5] uppercase tracking-[0.2em] text-center">Planejamento Finalizado</h4>
                <div class="grid grid-cols-3 gap-4 py-2">
                     <div class="text-center">
                         <span class="block text-[10px] uppercase text-white/30 mb-1">Solicitado</span>
                         <span class="text-2xl font-light text-white">${usedDays} <span class="text-[10px] font-light text-white/30">dias</span></span>
                     </div>
                     <div class="text-center">
                         <span class="block text-[10px] uppercase text-white/30 mb-1">Folga Real</span>
                         <span class="text-2xl font-medium text-[#00BFA5]">${totalFolga} <span class="text-[10px] font-light text-[#00BFA5]/50">dias</span></span>
                     </div>
                     <div class="text-center">
                         <span class="block text-[10px] uppercase text-white/30 mb-1">Abono</span>
                         <span class="text-2xl font-light text-white">${abonoDays} <span class="text-[10px] font-light text-white/30">dias</span></span>
                     </div>
                </div>
                <div class="pt-4 border-t border-white/5 text-center">
                    <p class="text-[10px] text-white/30 leading-relaxed font-light italic">
                         Você receberá o Terço Constitucional sobre 30 dias + pagamento dos ${abonoDays} dias de abono.
                    </p>
                </div>
            </div>
        `;
    } else {
        metricsHtml = `
            <div class="p-6 bg-white/[0.02] border border-white/5 rounded-2xl space-y-6">
                <h4 class="text-[10px] font-medium text-white/30 uppercase tracking-[0.2em] text-center">Planejamento Atual</h4>
                <div class="grid grid-cols-2 gap-8 py-2">
                     <div class="text-center">
                         <span class="block text-[10px] uppercase text-white/30 mb-1">Total Solicitado</span>
                         <span class="text-3xl font-light text-white">${usedDays} <span class="text-sm font-light text-white/30">dias</span></span>
                     </div>
                     <div class="text-center">
                         <span class="block text-[10px] uppercase text-white/30 mb-1">Descanso Efetivo</span>
                         <span class="text-3xl font-light text-[#00BFA5]">${totalFolga} <span class="text-sm font-light text-[#00BFA5]/50">dias</span></span>
                     </div>
                </div>
            </div>
        `;
    }

    container.innerHTML = `
        <div class="glass-card rounded-3xl p-10 space-y-8 ${isDone ? 'conclude-card' : ''}">
            <div class="flex justify-between items-center">
                <div class="flex items-center gap-4">
                    <div class="w-10 h-10 rounded-full bg-[#00BFA5]/10 flex items-center justify-center text-[#00BFA5] text-sm font-medium">03</div>
                    <h3 class="text-xl">${isDone ? 'Resultado Final' : 'Definir Períodos'}</h3>
                </div>
                <div class="text-right">
                    <span class="block text-[10px] uppercase tracking-[0.2em] text-white/30 font-medium mb-1">Saldo Remanescente</span>
                    <span class="text-xl font-medium text-white">${state.saldo} / ${state.config.total} dias</span>
                </div>
            </div>

            ${metricsHtml}

            ${state.selectedOps.length > 0 ? `
                <div class="space-y-4">
                    <div class="flex items-center justify-between">
                         <span class="text-[10px] font-medium text-white/30 uppercase tracking-[0.2em]">Roteiro Selecionado</span>
                    </div>
                    ${state.selectedOps.map((op, i) => `
                        <div class="op-card group border-l-2 border-[#00BFA5]/50 bg-white/[0.01]">
                            <div>
                                <p class="text-sm font-medium text-white">${op.length} dias de férias</p>
                                <div class="flex flex-col gap-1 mt-2">
                                    <p class="text-[11px] text-white/30 flex items-center gap-2">
                                        <i data-lucide="building-2" class="w-3 h-3"></i> 
                                        RH: ${op.start.toLocaleDateString('pt-BR')} — ${op.end.toLocaleDateString('pt-BR')}
                                    </p>
                                    <p class="text-[11px] text-white/30 flex items-center gap-2">
                                        <i data-lucide="calendar-heart" class="w-3 h-3"></i> 
                                        Folga real: ${op.actualStart.toLocaleDateString('pt-BR')} — ${op.actualEnd.toLocaleDateString('pt-BR')}
                                    </p>
                                </div>
                            </div>
                            <button class="remove-op p-2 text-white/10 hover:text-red-400 transition-colors" data-idx="${i}">
                                <i data-lucide="trash-2" class="w-4 h-4"></i>
                            </button>
                        </div>
                    `).join('')}
                </div>
            ` : ''}

            ${!isDone ? `
                <div class="space-y-6">
                    <h4 class="text-[10px] font-medium text-white/30 uppercase tracking-[0.2em] text-center">Melhores Sugestões</h4>
                    <div class="grid grid-cols-1 gap-4">
                        ${options.slice(0, 5).map((op, i) => `
                            <button class="select-op text-left op-card glass-card-interactive group relative overflow-hidden" data-idx="${i}">
                                <div class="z-10">
                                    <div class="flex items-center gap-3 mb-2">
                                        <span class="text-sm font-medium text-white">Tire ${op.length} dias e folgue ${op.total}!</span>
                                        <span class="px-2 py-0.5 bg-[#00BFA5]/10 text-[#00BFA5] text-[10px] font-medium rounded-full">+${op.gain} extra</span>
                                    </div>
                                    <div class="flex flex-col gap-1">
                                        <p class="text-[11px] text-white/30 flex items-center gap-2">
                                            <i data-lucide="building-2" class="w-3 h-3"></i>
                                            Sugestão RH: ${op.start.toLocaleDateString('pt-BR')} — ${op.end.toLocaleDateString('pt-BR')}
                                        </p>
                                        <p class="text-[11px] text-white/30 flex items-center gap-2">
                                            <i data-lucide="calendar-heart" class="w-3 h-3"></i>
                                            Período de folga: ${op.actualStart.toLocaleDateString('pt-BR')} — ${op.actualEnd.toLocaleDateString('pt-BR')}
                                        </p>
                                    </div>
                                </div>
                                <i data-lucide="plus-circle" class="w-5 h-5 text-white/10 group-hover:text-[#00BFA5] transition-all"></i>
                            </button>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            <div class="pt-10 border-t border-white/5 flex gap-4">
                <button id="btn-restart" class="flex-1 glass-btn py-3 uppercase tracking-widest text-[11px]">
                    Resetar e Recalcular
                </button>
            </div>
        </div>
    `;

    container.querySelectorAll('.select-op').forEach(btn => {
        btn.onclick = () => {
            const idx = parseInt(btn.dataset.idx);
            const op = options[idx];
            state.selectedOps.push(op);
            state.selectedOps.sort((a, b) => a.start - b.start);
            state.saldo -= op.length;
            renderStep3();
        };
    });

    container.querySelectorAll('.remove-op').forEach(btn => {
        btn.onclick = () => {
            const idx = parseInt(btn.dataset.idx);
            const op = state.selectedOps.splice(idx, 1)[0];
            state.saldo += op.length;
            renderStep3();
        };
    });

    document.getElementById('btn-restart').onclick = () => {
        state.step = 1;
        toggleHero(true);
        state.selectedOps = [];
        state.saldo = 30;
        document.getElementById('step-3').classList.add('hidden');
        document.getElementById('step-1').classList.remove('hidden');
    };

    lucide.createIcons();
}

init();
