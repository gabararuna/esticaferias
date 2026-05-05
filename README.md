# Estica Férias

Calculadora web que indica os melhores períodos para tirar férias com base nos feriados nacionais, estaduais e municipais e nos fins de semana — maximizando os dias de descanso real.

**Demo:** [esticaferias.com.br](https://esticaferias.com.br)

## Funcionalidades

- Seleção por estado e município com base de feriados municipais completa
- Cálculo automático dos períodos que rendem mais dias de folga
- Suporte a múltiplos idiomas (Português, Inglês, Espanhol)
- Páginas explicativas de metodologia e FAQ
- Sem dependências externas — 100% vanilla HTML/CSS/JS
- Compatível com Google AdSense
- Design glassmorphism mobile-first

## Stack

- HTML5 + CSS3 + JavaScript puro (sem framework, sem build tool)
- Dados: `cidades.json` + `feriados_municipais.json`

## Como rodar

Projeto estático — basta servir com qualquer servidor HTTP:

```bash
# Com Python
python3 -m http.server 8080

# Com Node.js (npx)
npx serve .
```

## Estrutura de arquivos

| Arquivo | Descrição |
|---------|-----------|
| `index.html` | Calculadora principal |
| `faq.html` | Perguntas frequentes |
| `metodologia.html` | Como o cálculo funciona |
| `privacidade.html` | Política de privacidade |
| `termos.html` | Termos de uso |
| `app.js` | Lógica de interface e orquestração |
| `logic.js` | Algoritmo de cálculo de férias |
| `cidades.json` | Base de dados de municípios brasileiros |
| `feriados_municipais.json` | Base de dados de feriados regionais |

## SEO

Inclui `robots.txt` e `sitemap.xml`. Submeta o sitemap no [Google Search Console](https://search.google.com/search-console) após publicar. Atualize o domínio no `sitemap.xml` antes do deploy.

## Licença

MIT
