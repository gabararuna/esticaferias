/**
 * Core Logic for Estica Férias
 * Ported from Python/Streamlit implementation
 */

export const getEaster = (year) => {
  const a = year % 19;
  const b = Math.floor(year / 100);
  const c = year % 100;
  const d = Math.floor(b / 4);
  const e = b % 4;
  const f = Math.floor((b + 8) / 25);
  const g = Math.floor((b - f + 1) / 3);
  const h = (19 * a + b - d - g + 15) % 30;
  const i = Math.floor(c / 4);
  const k = c % 4;
  const l = (32 + 2 * e + 2 * i - h - k) % 7;
  const m = Math.floor((a + 11 * h + 22 * l) / 451);
  const month = Math.floor((h + l - 7 * m + 114) / 31);
  const day = ((h + l - 7 * m + 114) % 31) + 1;
  return new Date(year, month - 1, day);
};

export const getMoveableHolidays = (year) => {
  const easter = getEaster(year);
  const addDays = (date, days) => {
    const d = new Date(date);
    d.setDate(d.getDate() + days);
    return d;
  };

  return [
    { date: addDays(easter, -48), name: "Carnaval (Segunda)" },
    { date: addDays(easter, -47), name: "Carnaval (Terça)" },
    { date: addDays(easter, -46), name: "Quarta-Feira de Cinzas" },
    { date: addDays(easter, -2), name: "Sexta-Feira Santa" },
    { date: easter, name: "Páscoa" },
    { date: addDays(easter, 60), name: "Corpus Christi" },
  ];
};

export const getFixedHolidays = (year) => {
  return [
    { m: 1, d: 1, name: "Confraternização Universal" },
    { m: 4, d: 21, name: "Tiradentes" },
    { m: 5, d: 1, name: "Dia do Trabalho" },
    { m: 9, d: 7, name: "Independência do Brasil" },
    { m: 10, d: 12, name: "Nossa Senhora Aparecida" },
    { m: 11, d: 2, name: "Finados" },
    { m: 11, d: 15, name: "Proclamação da República" },
    { m: 11, d: 20, name: "Dia da Consciência Negra" },
    { m: 12, d: 25, name: "Natal" },
  ].map(h => ({
    date: new Date(year, h.m - 1, h.d),
    name: h.name
  }));
};

export const getCompleteHolidays = async (startDate, endDate, state, city, municipalHols) => {
  const hols = [];
  const years = [];
  for (let y = startDate.getFullYear(); y <= endDate.getFullYear(); y++) {
    years.push(y);
  }

  const seen = new Set();
  const addHol = (date, name, type) => {
    const key = date.toISOString().split('T')[0];
    if (date >= startDate && date <= endDate && !seen.has(key)) {
      hols.push({ date: new Date(date), name, type });
      seen.add(key);
    }
  };

  years.forEach(year => {
    getFixedHolidays(year).forEach(h => addHol(h.date, h.name, "Nacional"));
    getMoveableHolidays(year).forEach(h => addHol(h.date, h.name, "Nacional (Móvel)"));
    
    // Add municipal holidays if available
    const cityData = municipalHols[state]?.[city] || {};
    Object.entries(cityData).forEach(([dtStr, name]) => {
      const parts = dtStr.split('/');
      if (parts.length === 2) {
        const d = parseInt(parts[0]);
        const m = parseInt(parts[1]);
        addHol(new Date(year, m - 1, d), name, "Municipal");
      } else if (parts.length === 3) {
        const d = parseInt(parts[0]);
        const m = parseInt(parts[1]);
        const y = parseInt(parts[2]);
        if (y === year) addHol(new Date(y, m - 1, d), name, "Municipal");
      }
    });
  });

  return hols.sort((a, b) => a.date - b.date);
};

export const getRestDays = (start, end) => {
  const rests = new Set();
  let curr = new Date(start);
  while (curr <= end) {
    if (curr.getDay() === 0 || curr.getDay() === 6) { // 0=Sun, 6=Sat
      rests.add(curr.toISOString().split('T')[0]);
    }
    const next = new Date(curr);
    next.setDate(next.getDate() + 1);
    curr = next;
  }
  return rests;
};

export const isValidStart = (date, hols, rests, selectedOps = []) => {
  const dStr = (d, offset = 0) => {
    const date = new Date(d);
    date.setDate(date.getDate() + offset);
    return date.toISOString().split('T')[0];
  };

  const isHolidayOrRest = (d) => hols[d] || rests.has(d);

  // Can't start on holiday/rest day
  if (isHolidayOrRest(dStr(date))) return false;
  // Can't start 1 or 2 days before holiday/rest day (CLT rule)
  if (isHolidayOrRest(dStr(date, 1))) return false;
  if (isHolidayOrRest(dStr(date, 2))) return false;

  // Check overlap with selected
  for (const op of selectedOps) {
    if (date >= op.start && date <= op.end) return false;
  }
  return true;
};

export const calcGain = (start, length, hols, rests, maxDate) => {
  const officialEnd = new Date(start);
  officialEnd.setDate(officialEnd.getDate() + length - 1);

  const isNonWork = (d) => hols[d.toISOString().split('T')[0]] || rests.has(d.toISOString().split('T')[0]);

  let actualStart = new Date(start);
  while (true) {
    const prev = new Date(actualStart);
    prev.setDate(prev.getDate() - 1);
    if (isNonWork(prev)) {
      actualStart = prev;
    } else {
      break;
    }
  }

  let actualEnd = new Date(officialEnd);
  while (actualEnd < maxDate) {
    const next = new Date(actualEnd);
    next.setDate(next.getDate() + 1);
    if (isNonWork(next)) {
      actualEnd = next;
    } else {
      break;
    }
  }

  const totalDays = Math.round((actualEnd - actualStart) / (1000 * 60 * 60 * 24)) + 1;
  return { totalDays, actualStart, actualEnd };
};

export const getCltLengths = (saldo, selectedOps = []) => {
  const has14 = selectedOps.some(op => op.length >= 14);
  const count = selectedOps.length;
  const opts = new Set();

  if (count === 0) {
    opts.add(saldo);
    for (let i = 14; i <= saldo - 5; i++) opts.add(i);
    for (let i = 5; i <= saldo - 14; i++) opts.add(i);
  } else if (count === 1) {
    if (has14 || saldo >= 14) opts.add(saldo);
    if (has14) {
      for (let i = 5; i <= saldo - 5; i++) opts.add(i);
    } else {
      for (let i = 14; i <= saldo - 5; i++) opts.add(i);
      for (let i = 5; i <= saldo - 14; i++) opts.add(i);
    }
  } else if (count === 2) {
    if (has14 || saldo >= 14) opts.add(saldo);
  }

  return Array.from(opts).sort((a, b) => a - b);
};
