# Estica Férias

Tem como objetivo otimizar o seu pedido de férias para que você possa usar os fins de semana e feriados para prolongar o seu descanso.
Versão nativa e modernizada do aplicativo "Estica Férias", otimizada para performance, SEO e AdSense. 

## ✨ Destaques
- **Design Premium**: Interface baseada em glassmorphism, tipografia moderna (Outfit/Inter) e gradientes fluidos.
- **Mobile-First**: Experiência perfeita em dispositivos móveis.
- **Ultra-Leve**: Construído em Vanilla JS/CSS com Tailwind, sem dependências pesadas de framework.
- **Pronto para Cloudflare**: Deploy instantâneo no Cloudflare Pages.
- **AdSense Ready**: Slots estrategicamente posicionados para monetização.

## 🚀 Como Executar
Devido ao uso de módulos JavaScript e `fetch`, você precisará de um servidor local simples:

```bash
# Se tiver npx/node
npx serve .

# Ou usando Python
python -m http.server 8000
```

## 📂 Estrutura do Projeto
- `index.html`: Estrutura principal e SEO.
- `style.css`: Design system e animações.
- `app.js`: Lógica de interface e orquestração.
- `logic.js`: Algoritmo de cálculo de férias (Portado do Python).
- `cidades.json`: Banco de dados de municípios.
- `feriados_municipais.json`: Banco de dados de feriados regionais.
