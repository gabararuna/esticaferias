# Design: Integração AdSense — Estica Férias
**Data:** 2026-05-12  
**Status:** Aprovado

---

## Objetivo

Integrar os três slots de AdSense já criados no painel Google (1 horizontal + 2 verticais) preservando o design glassmorphism dark/minimalista do Estica Férias, em conformidade com as políticas do AdSense, garantindo que os anúncios permaneçam visíveis durante todas as etapas do fluxo de uso.

---

## Slots AdSense

| Nome                    | Slot ID      | Uso                          |
|-------------------------|--------------|------------------------------|
| EsticaFeriasHorizontal#01 | 4879447262 | Mobile header + páginas secundárias |
| EsticaFériasVertical#01   | 6000957242 | Sidebar esquerdo (desktop)   |
| EsticaFériasVertical#02   | 7592856075 | Sidebar direito (desktop)    |

Publisher ID: `ca-pub-4059018857698196`

---

## Correções de Conformidade AdSense

### Problema 1: Script carregado múltiplas vezes
O snippet original carrega `adsbygoogle.js` uma vez por slot (3x por página). Isso viola as boas práticas e causa erros de renderização.

**Correção:** Uma única tag `<script async src="...adsbygoogle.js?client=ca-pub-4059018857698196">` no `<head>` de cada página. Cada slot usa apenas `<ins>` + `<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>`.

### Problema 2: `data-full-width-responsive="true"` nos verticais
Esse atributo força os slots verticais a se comportarem como banners horizontais responsivos, impedindo a renderização como skyscraper/tall no sidebar.

**Correção:** Remover `data-full-width-responsive="true"` dos dois slots verticais. Manter apenas no slot horizontal.

### Problema 3: Containers sem largura definida nos verticais
AdSense precisa de um container com largura definida para renderizar o formato correto em sidebars.

**Correção:** Container `.ad-sidebar` com `width: 160px` fixo. O `<ins>` herda essa largura.

---

## Arquitetura de Layout

### Desktop (≥ 1280px)

O `#app-body` recebe um wrapper `.ads-layout-wrapper` que se torna um CSS Grid de 3 colunas:

```
[160px] [1fr — conteúdo] [160px]
```

- As colunas de sidebar têm largura fixa `160px`, o conteúdo ocupa o espaço restante.
- Os sidebars usam `position: sticky; top: 2rem` para acompanhar o scroll em todas as etapas.
- Abaixo de 1280px: `.ad-sidebar { display: none }`, o grid colapsa para coluna única.

**Por que isso preserva os anúncios durante as etapas:**  
Os steps 1, 2 e 3 ficam dentro da coluna central (`<main>`). Os sidebars são irmãos do `<main>` no grid, fora do fluxo dos steps. Logo, os anúncios verticais permanecem visíveis durante toda a navegação sem lógica JavaScript adicional.

### Mobile (< 1280px)

O slot horizontal é inserido **dentro do `#app-header`**, antes do badge "Desenvolvido por Numera". O header é renderizado uma vez e persiste em todos os steps.

- Container com `max-height: 120px; overflow: hidden` para garantir que anúncios grandes não empurrem o conteúdo para fora da tela.
- `display: none` em `≥ 1280px` (sidebars cobrem o desktop).

**Welcome Screen:** Não recebe anúncios. É uma splash screen — proibido pelas políticas do AdSense e prejudicial ao visual.

---

## Estrutura HTML (index.html)

```
<head>
  <!-- AdSense script — UMA vez -->
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js
                     ?client=ca-pub-4059018857698196" crossorigin="anonymous"></script>
</head>

<body>
  <!-- Welcome Screen — SEM ads -->
  <div id="welcome-screen">...</div>

  <!-- App Body -->
  <div id="app-body">
    <div class="ads-layout-wrapper">

      <!-- Sidebar Esquerdo (desktop only) -->
      <aside class="ad-sidebar ad-sidebar-left">
        <div class="ad-sidebar-inner">
          <span class="ad-label">Anúncio</span>
          <ins class="adsbygoogle"
               data-ad-client="ca-pub-4059018857698196"
               data-ad-slot="6000957242"
               data-ad-format="auto"
               style="display:block; width:160px;"></ins>
          <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
        </div>
      </aside>

      <!-- Conteúdo Principal -->
      <main>
        <header id="app-header">
          <!-- Mobile horizontal ad (hidden on desktop) -->
          <div class="ad-mobile-top">
            <span class="ad-label">Anúncio</span>
            <ins class="adsbygoogle"
                 data-ad-client="ca-pub-4059018857698196"
                 data-ad-slot="4879447262"
                 data-ad-format="auto"
                 data-full-width-responsive="true"
                 style="display:block;"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
          </div>

          <a class="app-author-btn">Desenvolvido por Numera</a>
          <h1>Estica Férias</h1>
          ...step bars...
        </header>

        <!-- Steps 1, 2, 3 — sem alteração -->
        <div id="app-container">...</div>
      </main>

      <!-- Sidebar Direito (desktop only) -->
      <aside class="ad-sidebar ad-sidebar-right">
        <div class="ad-sidebar-inner">
          <span class="ad-label">Anúncio</span>
          <ins class="adsbygoogle"
               data-ad-client="ca-pub-4059018857698196"
               data-ad-slot="7592856075"
               data-ad-format="auto"
               style="display:block; width:160px;"></ins>
          <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
        </div>
      </aside>

    </div><!-- /.ads-layout-wrapper -->

    <footer>...</footer>
  </div><!-- /#app-body -->
</body>
```

---

## Páginas Secundárias (faq, metodologia, privacidade, termos)

Cada uma recebe:
1. Script único no `<head>`
2. Slot horizontal inserido após o `<h1>` principal da página, antes do conteúdo — sem sidebars verticais

---

## CSS (adições ao style.css)

```css
/* Layout wrapper: single column por padrão (mobile) */
.ads-layout-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  width: 100%;
}

/* Sidebars ocultos no mobile */
.ad-sidebar {
  display: none;
}

/* Desktop: grid 3 colunas */
@media (min-width: 1280px) {
  .ads-layout-wrapper {
    display: grid;
    grid-template-columns: 160px 1fr 160px;
    align-items: start;
    gap: 1rem;
  }

  .ad-sidebar {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding-top: 3rem;
  }

  .ad-sidebar-inner {
    position: sticky;
    top: 2rem;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0.5rem;
    width: 160px;
  }

  /* Mobile ad oculto no desktop */
  .ad-mobile-top {
    display: none;
  }
}

/* Label "Anúncio" — quase invisível, só para conformidade */
.ad-label {
  display: block;
  font-size: 0.5rem;
  font-family: 'Inter', sans-serif;
  text-transform: uppercase;
  letter-spacing: 0.2em;
  color: rgba(255, 255, 255, 0.12);
  text-align: center;
  margin-bottom: 0.375rem;
}

/* Mobile ad: max-height para evitar empurrar conteúdo para fora */
.ad-mobile-top {
  max-height: 120px;
  overflow: hidden;
  margin-bottom: 1.5rem;
  display: block;
}
```

---

## Checklist de Conformidade AdSense

- [x] `ads.txt` presente e correto (`pub-4059018857698196`)
- [x] Script carregado uma única vez por página
- [x] Nenhum anúncio na welcome screen (splash)
- [x] Labels "Anúncio" visíveis (política de transparência)
- [x] Anúncios não sobrepostos ao conteúdo
- [x] `data-full-width-responsive` removido dos verticais
- [x] Containers com largura definida para verticais
- [x] `max-height` no mobile impede overflow para fora da tela

---

## Arquivos Modificados

| Arquivo           | Mudança                                                                 |
|-------------------|-------------------------------------------------------------------------|
| `index.html`      | Script no head, wrapper grid, sidebars, mobile ad no header             |
| `style.css`       | `.ads-layout-wrapper`, `.ad-sidebar`, `.ad-label`, `.ad-mobile-top`     |
| `faq.html`        | Script no head, horizontal ad após h1                                   |
| `metodologia.html`| Script no head, horizontal ad após h1                                   |
| `privacidade.html`| Script no head, horizontal ad após h1                                   |
| `termos.html`     | Script no head, horizontal ad após h1                                   |
