# AdSense Integration — Estica Férias Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Integrar os três slots AdSense (1 horizontal + 2 verticais) em todas as páginas do Estica Férias sem impactar o design glassmorphism dark/minimalista, mantendo os anúncios visíveis em todas as etapas do fluxo, em conformidade com as políticas do Google AdSense.

**Architecture:** CSS Grid de 3 colunas (`160px | 1fr | 160px`) no wrapper do app body para sidebars sticky no desktop. No mobile, um slot horizontal persiste no `#app-header`, acima do badge "Desenvolvido por Numera". O script AdSense é carregado uma única vez no `<head>` de cada página.

**Tech Stack:** HTML5 vanilla, CSS3 (sem framework, sem build tool), AdSense pub-4059018857698196

---

## Arquivos Modificados

| Arquivo | Mudança |
|---|---|
| `style.css` | Adicionar classes de layout de anúncios |
| `index.html` | Script no head, wrapper grid, sidebars, mobile ad |
| `faq.html` | Script no head, horizontal ad após seção hero |
| `metodologia.html` | Script no head, horizontal ad após seção hero |
| `privacidade.html` | Script no head, horizontal ad após seção hero |
| `termos.html` | Script no head, horizontal ad após seção hero |

---

## Slots de Referência

```
Publisher:   ca-pub-4059018857698196
Horizontal:  data-ad-slot="4879447262"  → mobile header + páginas secundárias
Vertical #1: data-ad-slot="6000957242"  → sidebar esquerdo (desktop index.html)
Vertical #2: data-ad-slot="7592856075"  → sidebar direito  (desktop index.html)
```

---

## Task 1: CSS — Classes de Layout de Anúncios

**Files:**
- Modify: `style.css` (append ao final do arquivo)

- [ ] **Step 1: Adicionar bloco CSS ao final de style.css**

Adicionar exatamente este bloco ao final do arquivo `style.css`, após a seção `SCROLLBAR`:

```css
/* ============================================================
   AD LAYOUT
   ============================================================ */

/* Wrapper: coluna única no mobile, grid 3 colunas no desktop */
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

/* Desktop ≥ 1280px: ativa o grid de 3 colunas */
@media (min-width: 1280px) {
  .ads-layout-wrapper {
    display: grid;
    grid-template-columns: 160px 1fr 160px;
    align-items: start;
    gap: 1rem;
    padding: 0 0.5rem;
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

  /* Mobile ad oculto no desktop (sidebars cobrem) */
  .ad-mobile-top {
    display: none;
  }
}

/* Label "Anúncio" — conformidade AdSense, quase invisível */
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

/* Mobile horizontal ad: max-height evita empurrar conteúdo */
.ad-mobile-top {
  max-height: 120px;
  overflow: hidden;
  margin-bottom: 1.5rem;
  display: block;
}

/* Garante que os <ins> verticais tenham largura explícita */
.ad-sidebar .adsbygoogle {
  display: block;
  width: 160px;
  min-height: 300px;
}
```

- [ ] **Step 2: Verificar no browser**

Abrir `index.html` localmente (`python3 -m http.server 8080` → `http://localhost:8080`). Confirmar que não há regressão visual — a página deve ter o mesmo aspecto de antes (nenhuma classe ad foi usada ainda no HTML).

- [ ] **Step 3: Commit**

```bash
git add style.css
git commit -m "feat: add ad layout CSS classes (wrapper, sidebars, label, mobile)"
```

---

## Task 2: index.html — Script AdSense no `<head>`

**Files:**
- Modify: `index.html` (linhas 16–19, dentro do `<head>`)

- [ ] **Step 1: Adicionar script único no `<head>` do index.html**

Localizar o bloco `<!-- Scripts & Styles -->` (linha 16) e adicionar o script AdSense **antes** do script do Tailwind, logo após o comentário. O bloco deve ficar assim:

```html
    <!-- Scripts & Styles -->
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4059018857698196"
         crossorigin="anonymous"></script>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="style.css">
    <script src="https://unpkg.com/lucide@latest"></script>
```

- [ ] **Step 2: Verificar no console do browser**

Abrir `http://localhost:8080`, abrir DevTools → Console. Confirmar que não há erros de carregamento do `adsbygoogle.js`. O script carregará mas não mostrará anúncios ainda (nenhuma `<ins>` no DOM). Isso é esperado.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add single AdSense script to index.html head"
```

---

## Task 3: index.html — Wrapper Grid + Sidebars Verticais

**Files:**
- Modify: `index.html` (linhas 53–156, o bloco `#app-body`)

- [ ] **Step 1: Envolver `<main>` com o wrapper e adicionar os sidebars**

Dentro de `#app-body`, substituir o `<main>` existente (e mantê-lo internamente) adicionando:
1. Um `<div class="ads-layout-wrapper">` que abre logo após `<div id="app-body" class="app-body-hidden">`
2. O sidebar esquerdo antes do `<main>`
3. O sidebar direito depois do `<main>`
4. Fechar o wrapper antes do `<footer>`

O `<div id="app-body" ...>` passa a ter esta estrutura interna:

```html
    <!-- ========== APP (hidden until welcome is dismissed) ========== -->
    <div id="app-body" class="app-body-hidden">
        <!-- Orb Background -->
        <div class="orb-container"></div>

        <div class="ads-layout-wrapper">

            <!-- Sidebar Esquerdo (desktop ≥ 1280px only) -->
            <aside class="ad-sidebar">
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

            <main class="flex-1 max-w-4xl mx-auto w-full px-6 pt-12 pb-20">
                <!-- ... conteúdo existente sem alteração ... -->
            </main>

            <!-- Sidebar Direito (desktop ≥ 1280px only) -->
            <aside class="ad-sidebar">
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

        <footer class="footer-minimalist">
            <!-- ... footer existente sem alteração ... -->
        </footer>
    </div>
```

**Atenção:** O `<div class="orb-container"></div>` fica fora do wrapper (é `position: fixed`, não impacta o layout). O `<footer>` fica fora do wrapper (é sibling de `.ads-layout-wrapper` dentro de `#app-body`).

- [ ] **Step 2: Verificar layout no browser**

Abrir `http://localhost:8080`, clicar "Começar" para entrar no app. Verificar:
- Mobile (< 1280px): layout sem alteração visual, sem sidebars visíveis
- Desktop (≥ 1280px, redimensionar browser): dois blocos de `160px` aparecem dos lados do conteúdo
- Os sidebars ficam sticky ao scrollar (conteúdo passa, sidebars ficam)
- Os steps 1, 2 e 3 continuam funcionando normalmente

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add desktop sidebar ad grid wrapper to index.html"
```

---

## Task 4: index.html — Mobile Horizontal Ad no App Header

**Files:**
- Modify: `index.html` (dentro de `<header class="app-header" id="app-header">`)

- [ ] **Step 1: Adicionar o ad mobile antes do badge**

Dentro de `<header class="app-header" id="app-header">`, adicionar o bloco `.ad-mobile-top` como **primeiro filho**, antes do `<a class="app-author-btn">`:

```html
            <header class="app-header" id="app-header">
                <!-- Mobile horizontal ad (hidden on desktop via CSS) -->
                <div class="ad-mobile-top">
                    <span class="ad-label">Anúncio</span>
                    <ins class="adsbygoogle"
                         style="display:block"
                         data-ad-client="ca-pub-4059018857698196"
                         data-ad-slot="4879447262"
                         data-ad-format="auto"
                         data-full-width-responsive="true"></ins>
                    <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
                </div>

                <a href="https://www.gruponumera.com" target="_blank" rel="noopener noreferrer" class="app-author-btn">
                    Desenvolvido por Numera
                </a>
                <h1 class="shimmer-gray app-title">Estica Férias</h1>
                <p class="app-subtitle">Maximize seus dias de descanso cruzando feriados com seu saldo de férias.</p>
                <div class="app-step-bars">
                    <div class="app-step-bar active" id="bar-1"></div>
                    <div class="app-step-bar" id="bar-2"></div>
                    <div class="app-step-bar" id="bar-3"></div>
                </div>
            </header>
```

- [ ] **Step 2: Verificar no browser (mobile e desktop)**

Abrir `http://localhost:8080`, clicar "Começar":
- **Mobile**: o ad aparece acima do badge "Desenvolvido por Numera", com no máximo 120px de altura. O conteúdo abaixo não sai da tela.
- **Desktop ≥ 1280px**: o `.ad-mobile-top` some completamente (`display: none` via CSS).
- Navegar pelos 3 steps: o header (com o ad mobile) permanece visível o tempo todo.

- [ ] **Step 3: Commit**

```bash
git add index.html
git commit -m "feat: add mobile horizontal ad to app-header in index.html"
```

---

## Task 5: faq.html — Script AdSense + Ad Horizontal

**Files:**
- Modify: `faq.html`

- [ ] **Step 1: Adicionar script no `<head>`**

Em `faq.html`, localizar a linha com `<script src="https://cdn.tailwindcss.com"></script>` (linha 11) e adicionar o script AdSense **antes** dela:

```html
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4059018857698196"
         crossorigin="anonymous"></script>
    <script src="https://cdn.tailwindcss.com"></script>
```

- [ ] **Step 2: Adicionar ad horizontal após a seção hero**

Em `faq.html`, localizar a seção hero (linha 66–74) que termina com `</section>` antes do `<div class="space-y-4">`. Inserir o bloco de ad entre eles:

```html
        <section class="text-center space-y-6">
            <!-- ... h1 e subtitle existentes ... -->
        </section>

        <!-- AdSense Horizontal -->
        <div style="max-width:100%; overflow:hidden;">
            <span class="ad-label" style="display:block; text-align:center;">Anúncio</span>
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-4059018857698196"
                 data-ad-slot="4879447262"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
        </div>

        <div class="space-y-4">
            <!-- acordeões existentes ... -->
```

- [ ] **Step 3: Verificar no browser**

Abrir `http://localhost:8080/faq.html`. Confirmar:
- O ad aparece entre o título e as perguntas
- Sem quebra visual no layout do acordeão
- Console sem erros de AdSense

- [ ] **Step 4: Commit**

```bash
git add faq.html
git commit -m "feat: add AdSense script and horizontal ad to faq.html"
```

---

## Task 6: metodologia.html — Script AdSense + Ad Horizontal

**Files:**
- Modify: `metodologia.html`

- [ ] **Step 1: Adicionar script no `<head>`**

Em `metodologia.html`, localizar `<script src="https://cdn.tailwindcss.com"></script>` (linha 11) e adicionar o script AdSense antes:

```html
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4059018857698196"
         crossorigin="anonymous"></script>
    <script src="https://cdn.tailwindcss.com"></script>
```

- [ ] **Step 2: Adicionar ad horizontal após a seção hero**

Em `metodologia.html`, localizar a seção hero (linhas 46–54) que termina com `</section>` antes do `<article>`. Inserir o bloco de ad entre eles:

```html
        <section class="text-center space-y-6">
            <!-- ... h1 e subtitle existentes ... -->
        </section>

        <!-- AdSense Horizontal -->
        <div style="max-width:100%; overflow:hidden;">
            <span class="ad-label" style="display:block; text-align:center;">Anúncio</span>
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-4059018857698196"
                 data-ad-slot="4879447262"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
        </div>

        <article class="glass-card rounded-3xl p-10 md:p-16 space-y-12 ...">
```

- [ ] **Step 3: Verificar no browser**

Abrir `http://localhost:8080/metodologia.html`. Confirmar:
- O ad aparece entre o título e o artigo de metodologia
- Sem regressão visual
- Console sem erros

- [ ] **Step 4: Commit**

```bash
git add metodologia.html
git commit -m "feat: add AdSense script and horizontal ad to metodologia.html"
```

---

## Task 7: privacidade.html — Script AdSense + Ad Horizontal

**Files:**
- Modify: `privacidade.html`

- [ ] **Step 1: Adicionar script no `<head>`**

Em `privacidade.html`, localizar `<script src="https://cdn.tailwindcss.com"></script>` (linha 9) e adicionar o script AdSense antes:

```html
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4059018857698196"
         crossorigin="anonymous"></script>
    <script src="https://cdn.tailwindcss.com"></script>
```

- [ ] **Step 2: Adicionar ad horizontal após a seção hero**

Em `privacidade.html`, localizar a seção hero (linhas 44–52) que termina com `</section>` antes do `<article>`. Inserir o bloco de ad entre eles:

```html
        <section class="text-center space-y-6">
            <!-- ... h1 e subtitle existentes ... -->
        </section>

        <!-- AdSense Horizontal -->
        <div style="max-width:100%; overflow:hidden;">
            <span class="ad-label" style="display:block; text-align:center;">Anúncio</span>
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-4059018857698196"
                 data-ad-slot="4879447262"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
        </div>

        <article class="glass-card rounded-3xl p-10 md:p-16 space-y-12 ...">
```

- [ ] **Step 3: Verificar no browser**

Abrir `http://localhost:8080/privacidade.html`. Confirmar:
- O ad aparece entre o título e o artigo de privacidade
- Sem regressão visual

- [ ] **Step 4: Commit**

```bash
git add privacidade.html
git commit -m "feat: add AdSense script and horizontal ad to privacidade.html"
```

---

## Task 8: termos.html — Script AdSense + Ad Horizontal

**Files:**
- Modify: `termos.html`

- [ ] **Step 1: Adicionar script no `<head>`**

Em `termos.html`, localizar `<script src="https://cdn.tailwindcss.com"></script>` (linha 9) e adicionar o script AdSense antes:

```html
    <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-4059018857698196"
         crossorigin="anonymous"></script>
    <script src="https://cdn.tailwindcss.com"></script>
```

- [ ] **Step 2: Adicionar ad horizontal após a seção hero**

Em `termos.html`, localizar a seção hero (linhas 44–52) que termina com `</section>` antes do `<article>`. Inserir o bloco de ad entre eles:

```html
        <section class="text-center space-y-6">
            <!-- ... h1 e subtitle existentes ... -->
        </section>

        <!-- AdSense Horizontal -->
        <div style="max-width:100%; overflow:hidden;">
            <span class="ad-label" style="display:block; text-align:center;">Anúncio</span>
            <ins class="adsbygoogle"
                 style="display:block"
                 data-ad-client="ca-pub-4059018857698196"
                 data-ad-slot="4879447262"
                 data-ad-format="auto"
                 data-full-width-responsive="true"></ins>
            <script>(adsbygoogle = window.adsbygoogle || []).push({});</script>
        </div>

        <article class="glass-card rounded-3xl p-10 md:p-16 space-y-12 ...">
```

- [ ] **Step 3: Verificar no browser**

Abrir `http://localhost:8080/termos.html`. Confirmar:
- O ad aparece entre o título e o artigo de termos
- Sem regressão visual

- [ ] **Step 4: Commit final**

```bash
git add termos.html
git commit -m "feat: add AdSense script and horizontal ad to termos.html"
```

---

## Checklist de Conformidade AdSense (verificar após todas as tasks)

- [ ] `ads.txt` em `google.com, pub-4059018857698196, DIRECT, f08c47fec0942fa0` — já presente e correto
- [ ] Script `adsbygoogle.js` carregado **uma única vez** por página — verificar via DevTools Network
- [ ] Nenhum anúncio na welcome screen
- [ ] Label "Anúncio" visível acima de cada slot
- [ ] `data-full-width-responsive="true"` apenas no horizontal (slots `4879447262`)
- [ ] `data-full-width-responsive` **ausente** nos verticais (slots `6000957242` e `7592856075`)
- [ ] Anúncios não se sobrepõem ao conteúdo em nenhuma resolução
- [ ] `.ad-mobile-top` tem `max-height: 120px; overflow: hidden` — conteúdo nunca sai da tela
- [ ] Sidebars são `display: none` abaixo de 1280px — sem cola em mobile/tablet
