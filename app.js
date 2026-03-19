import * as logic from './logic.js';

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
        startInput.valueAsDate = now;
        endInput.valueAsDate = nextYear;

        setTimeout(tryGeolocation, 1000);

    } catch (err) {
        console.error("Initialization failed:", err);
    }
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

    // Modal Events (Optional - only if elements exist)
    const helpModal = document.getElementById('help-modal');
    const openHelp = document.getElementById('open-help');
    const closeHelp = document.getElementById('close-help');

    if (openHelp && helpModal) {
        openHelp.onclick = (e) => {
            e.preventDefault();
            helpModal.classList.add('open');
        };
    }

    if (closeHelp && helpModal) {
        closeHelp.onclick = () => helpModal.classList.remove('open');
    }

    if (helpModal) {
        helpModal.onclick = (e) => {
            if (e.target.classList.contains('modal-overlay')) helpModal.classList.remove('open');
        };
    }

    startInput.onchange = () => {
        if (startInput.valueAsDate) {
            const newEnd = new Date(startInput.valueAsDate);
            newEnd.setFullYear(newEnd.getFullYear() + 1);
            endInput.valueAsDate = newEnd;
        }
    };

    document.getElementById('select-state').onchange = (e) => populateCities(e.target.value);

    daysRange.oninput = (e) => {
        const val = parseInt(e.target.value);
        daysLabel.textContent = val;

        if (val < 20) {
            daysRange.classList.add('slider-danger');
            cltWarning.classList.remove('hidden');
        } else {
            daysRange.classList.remove('slider-danger');
            cltWarning.classList.add('hidden');
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
    const startInput = document.getElementById('input-start').valueAsDate;
    const endInput = document.getElementById('input-end').valueAsDate;
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
        <div class="flex items-center justify-between mb-6">
            <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 font-bold">2</div>
                <h3 class="text-xl font-semibold">Gerenciar Feriados</h3>
            </div>
            <button id="btn-back-2" class="text-sm text-slate-400 hover:text-white flex items-center gap-1">
                <i data-lucide="arrow-left" class="w-4 h-4"></i> Voltar
            </button>
        </div>

        <p class="text-sm text-slate-400 mb-6">Desmarque os feriados que você deseja desconsiderar.</p>

        <div class="space-y-3 mb-8">
            ${state.holidays.length > 0 ? state.holidays.map((h, i) => `
                <div class="flex items-center justify-between p-4 bg-slate-900/50 border border-slate-700 rounded-xl">
                    <div class="flex flex-col">
                        <span class="font-medium text-slate-200">${h.name}</span>
                        <span class="text-xs text-slate-500">${h.date.toLocaleDateString('pt-BR')} • ${h.type}</span>
                    </div>
                    <label class="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" value="${i}" checked class="sr-only peer hol-toggle">
                        <div class="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                </div>
            `).join('') : '<p class="text-center py-8 text-slate-500">Nenhum feriado encontrado neste período.</p>'}
        </div>

        <button id="btn-next-2" class="w-full btn-primary py-4 text-lg">
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

    container.innerHTML = `
        <div class="glass-card rounded-2xl p-8 space-y-6">
            <div class="flex justify-between items-center">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-blue-500/20 flex items-center justify-center text-blue-400 font-bold">3</div>
                    <h3 class="text-xl font-semibold">Definir Períodos</h3>
                </div>
                <div class="text-right flex items-center gap-2">
                    <div>
                        <span class="block text-[10px] uppercase tracking-wider text-slate-500 font-bold">Saldo</span>
                        <span class="text-xl font-bold text-white">${usedDays}/${state.config.total} dias</span>
                    </div>
                    ${state.saldo === 0 ? '<div class="w-8 h-8 bg-emerald-500/20 text-emerald-400 rounded-full flex items-center justify-center"><i data-lucide="check" class="w-5 h-5"></i></div>' : ''}
                </div>
            </div>

            ${state.selectedOps.length > 0 ? `
                <div class="space-y-4">
                    <h4 class="text-sm font-semibold text-slate-400 uppercase tracking-widest text-center">Resumo do Planejamento</h4>
                    <div class="grid grid-cols-2 gap-4 bg-blue-500/5 p-4 rounded-xl border border-blue-500/20">
                         <div class="text-center">
                             <span class="block text-[10px] uppercase text-slate-500">Dias de Férias Usados</span>
                             <span class="text-2xl font-bold text-white">${usedDays}</span>
                         </div>
                         <div class="text-center">
                             <span class="block text-[10px] uppercase text-slate-500">Total de Folga Real</span>
                             <span class="text-2xl font-bold text-emerald-400">${totalFolga}</span>
                         </div>
                    </div>
                </div>
            ` : ''}

            ${state.selectedOps.length > 0 ? `
                <div class="space-y-3">
                    <h4 class="text-sm font-semibold text-slate-400 uppercase tracking-widest">Períodos Confirmados</h4>
                    ${state.selectedOps.map((op, i) => `
                        <div class="op-card animate-fade-in group border-l-4 border-l-blue-500">
                            <div>
                                <p class="op-card-text">Você tirou ${op.length} dias e folgou ${op.total} dias!</p>
                                <p class="op-card-subtext">Iniciando em ${op.actualStart.toLocaleDateString('pt-BR')} até ${op.actualEnd.toLocaleDateString('pt-BR')}</p>
                            </div>
                            <button class="remove-op text-slate-600 hover:text-red-400 transition-colors" data-idx="${i}">
                                <i data-lucide="trash-2" class="w-4 h-4"></i>
                            </button>
                        </div>
                    `).join('')}
                </div>
            ` : ''}

            ${state.saldo > 0 ? `
                <div class="space-y-4">
                    <h4 class="text-sm font-semibold text-slate-400 uppercase tracking-widest">Melhores Opções</h4>
                    <div class="grid grid-cols-1 gap-4">
                        ${options.slice(0, 10).map((op, i) => `
                            <button class="select-op text-left op-card hover:border-blue-500/50 transition-all group relative overflow-hidden" data-idx="${i}">
                                <div class="z-10">
                                    <div class="flex items-center gap-2 mb-1">
                                        <span class="op-card-text">Tire ${op.length} dias e folgue ${op.total} dias!</span>
                                        <span class="px-2 py-0.5 bg-emerald-500/20 text-emerald-400 text-[10px] font-bold rounded-full transition-transform group-hover:scale-110">+${op.gain}</span>
                                    </div>
                                    <p class="op-card-subtext">
                                        Iniciando em ${op.actualStart.toLocaleDateString('pt-BR')} até ${op.actualEnd.toLocaleDateString('pt-BR')}
                                    </p>
                                </div>
                                <i data-lucide="plus-circle" class="w-6 h-6 text-slate-600 group-hover:text-blue-500 transition-all group-hover:rotate-90"></i>
                            </button>
                        `).join('')}
                    </div>
                </div>
            ` : ''}

            <div class="pt-6 border-t border-slate-700/50 flex gap-4">
                <button id="btn-restart" class="flex-1 btn-secondary py-3 flex items-center justify-center gap-2">
                    Recomeçar
                </button>
                <button id="btn-share" class="p-3 btn-secondary">
                    <i data-lucide="share-2" class="w-5 h-5"></i>
                </button>
            </div>
        </div>
    `;

    container.querySelectorAll('.select-op').forEach(btn => {
        btn.onclick = () => {
            const idx = parseInt(btn.dataset.idx);
            const op = options[idx];
            state.selectedOps.push(op);
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
