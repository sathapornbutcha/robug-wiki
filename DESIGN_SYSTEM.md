# 🔒 ROBugcreammm — Foundation Lock (Design System v1)

> **STATUS: FROZEN — 2026-05-25.**
> This file is the **single immutable source of truth** for the wiki's UI.
> The values here describe what is *already rendering*. They are not aspirations.
>
> **Before touching ANY page or stylesheet, read this file.**
> **Rule: REUSE ONLY. Do not redesign, re-derive, or "improve" the system without explicit owner approval.**

---

## 0. How to work with this system (read first)

1. **Reuse tokens & components.** Never hardcode a number that a token already covers. If `--space-6` is `24px`, write `var(--space-6)`, not `24px`.
2. **No new variations.** One navbar, one ticker, one hero pattern, one card. If a page needs chrome, it already has it (injected). Do not author a second navbar.
3. **Extend, don't fork.** Need a value the system lacks? Add a **token** to `:root` in `style.css`, document it here, then use it. Do not sprinkle magic numbers.
4. **Changing a locked value = a spec change.** Update this file in the same edit, with a note in the Changelog. If you're not the owner, ask first.
5. **Verify, don't tweak.** After any change, confirm against this spec via the preview server. "Looks a bit off" is not a license to re-proportion the hero.

The system lives in **3 files** (everything else consumes them):

| File | Role |
|---|---|
| [`style.css`](style.css) | Global tokens (`:root`) + global components: topbar, ticker, cards, detail, tier, leaderboard |
| [`pages.css`](pages.css) | Page-specific layout that *consumes* tokens: `.champ` hero, 6v6 — loaded only by `home.html` / `6v6.html` |
| [`atmosphere.js`](atmosphere.js) | **Injects the shared top chrome (navbar + ticker) on every page** + ambient particle/glow layer |

---

## 1. Color system  → `style.css :root` + `html[data-theme="dark"]`

Two themes. **Dark is the default** (set via inline bootstrap script + `localStorage "rom-theme"`).

**Semantic tokens** (use these, not raw hex):
`--bg --surface --ink --ink-2 --muted --border --border-soft`
`--coral --coral-soft --pink --pink-soft --mint --mint-soft --butter --butter-soft --sky --sky-soft --violet --violet-soft`

**Launcher accent (theme-independent):** `--gold #f4d27a` · `--gold-2 #e8b96a` · `--gold-grad`.
Gold = premium/championship/admin/active-nav. Coral = primary brand action on light surfaces.

> Locked dark palette: `--bg #0C0E1A` · `--surface #161A24` · `--ink #F2EFE8`. Do not introduce new base greys.

## 2. Spacing system  → tokens `--space-*`, `--gutter`, `--w-*`

4px base scale: `--space-1 4` `-2 8` `-3 12` `-4 16` `-5 20` `-6 24` `-7 28` `-8 32` `-10 40` `-12 48` `-16 64`.

**Layout widths (locked):**
- `--w-content 1240px` — body content (`.wrap`), padding `--gutter 24px`.
- `--w-nav 1380px` — navbar bar is intentionally wider than content (launcher pattern).
- `--w-hero 1180px` — `.champ` cinematic panel, centered.
- `--w-hero-grid 1100px` — inner hero grid.

## 3. Typography  → tokens `--ff-*`, `--fs-*`, `--fw-*`

- **Body:** `--ff-body` (Inter), line-height 1.55, antialiased.
- **Display/headings:** `--ff-display` (Outfit).
- **Numeric/tier badges:** `--ff-mono` (Space Grotesk).
- **Scale:** `--fs-xs 11` `-sm 13` `-base 15` `-md 17` `-lg 22` `-xl 27`; hero `--fs-h1 clamp(34,5vw,52)`; championship `--fs-champ clamp(30,3.7vw,44)`.
- **Weights:** 400 / 500 / 600 / 700 / 800 (`--fw-*`). Headings = 800.

## 4. Top chrome — Navbar + Server Ticker  → `atmosphere.js` (injector) + `style.css` (styles)

**This is a shared global layout system. There is exactly ONE. It is injected at runtime on every page** (root + all ~18k detail pages) because every page loads `atmosphere.js`. **Never hand-author a navbar in page HTML.**

- **Injector:** first IIFE in `atmosphere.js`. Detects path depth → relative prefix (`../` on detail pages); removes any static `.topbar`/`.server-ticker`; prepends the shared ones; sets active tab; binds theme toggle. Exposes `window.ROM_updateNav()` (used by `index.html` on `hashchange`).
- **Nav items (locked, 9):** Home · Monsters · Equipments · Headwears · Jobs · Skills · Cards · 6v6 · Draft. Category items link `index.html#<cat>`; index reads the hash to switch its in-place grid.
- **Active state:** gold pill — `.hnav a.active` (`rgba(244,210,122,.14)` bg, `--gold` text, inset gold ring). One active item, derived from URL.
- **Right actions:** global search (`⌘K` focuses it; **Enter → `index.html?q=<query>`**, index auto-applies a cross-category search + smooth-scrolls to results), theme toggle, notification bell (badge), gold **Admin**, ghost **Admin**.
- **Styling:** `style.css` "GLOBAL TOP CHROME" section — `.topbar`(glass) `.bar`(max `--w-nav`) `.hnav` `.top-actions` `.top-search` `.icon-btn` `.btn-admin[.ghost]` `.server-ticker`.
- **Ticker tags:** `.event`(coral) `.patch`(blue) `.dungeon`(gold).
- **Responsive (locked breakpoints):** search hides `<1360px`; nav labels collapse to icons `<1140px`; nav hides + ghost-admin hides `<760px`.
- **Glass + sticky:** `.topbar` `position:sticky; z-index:var(--z-topbar 30)`, `backdrop-filter:blur(18px) saturate(1.2)`.

## 5. Atmosphere system  → `atmosphere.js` (2nd IIFE) + `style.css` (ambient layer) + `pages.css` (hero fx)

Respects `prefers-reduced-motion` (ambient disables; **chrome still injects**). Single rAF loop, pauses on hidden tab.

- **Page ambient:** `body::before` aurora gradients (`--z-bg`), `body::after` cinematic vignette (dark corners). Cursor-reactive `.atmo-glow` (`--z-glow`, screen blend).
- **Hero particles:** `.atmo-canvas` — ≤54 gold/blue embers rising, twinkling. Gold default, ~28% blue.
- **Parallax:** subtle, on `.champ-art` (whole hero container), `.deco`, `.feat-card`. **Do not target `.cs-orbit`/`.champ-hero-art` directly** — they rely on their own `transform` for centering/rotation; parallaxing the container preserves those.

## 6. Hero proportions — Championship panel  → `pages.css .champ*` (LOCKED)

Centered cinematic panel, **not** a full-bleed banner.

- `.champ`: `max-width:var(--w-hero 1180)`, `margin:18px auto 0`, `border-radius:var(--r-panel 26)`, 1px `rgba(255,255,255,.07)` border, deep shadow; gold focal glow at **64% 44%** (center-right). Side gutter `20px` `<1224px`.
- `.champ-grid`: `grid-template-columns:1.16fr .84fr`, `gap:28px`, `max-width:var(--w-hero-grid 1100)`, `padding:62px 46px 66px`. Stacks `<860px`.
- `.champ-art`: height `var(--hero-art-h 520)`. Orbit circle + 6 class orbs + rotating magic platform + volumetric halo.
- **Orbit = invisible circle:** `.cs-orbit` is a centered square (`width:100%;aspect-ratio:1;translate(-50%,-50%)`) → perfect circle geometry, but the **ring itself is hidden** (no border / dashed inner / conic glow — `::before`/`::after` `display:none`). 6 orbs sit on it **evenly at 60°, single radius 42%** (tl `13.6%/29%` · tr `13.6%/71%` · l `50%/8%` · r `50%/92%` · bl `86.4%/29%` · br `86.4%/71%`); `.orb` centered on its point via `margin:-32px`.
- **Orbit motion:** icons revolve along the circle — `.cs-orbit` `orbitSpin 44s` + `.orb` `orbCounter 44s` (same period, reverse) keeps icons upright. Halts under reduced-motion.
- **Randomizers (home inline script, every 10s, crossfaded — never a hard blink):**
  - **Orbit icons** → random from **Hero + Collab + 4th-Job** classes (`ORBIT_POOL`, taxonomy from `search-index.js` groups). Crossfade = stacked `<img>` opacity `1.1s`, staggered 150ms.
  - **Center card `.cs-center`** → random **Tier-S** class pulled **live from the 6v6 meta** (`localStorage "rom-rank"`, letter starting `S`; `jf(name)` → icon file); editing the Meta page updates it. Small fallback until Meta saved once. Subtitle shows `S-Tier`.
  - **Main character image stays centered** and is never randomized.
- **Character:** `.champ-hero-art` centered (`left:50%;top:48%;translate(-50%,-50%)`), `height/max-width:48%` (≈half), `object-fit:contain`; drop-shadow halo + gold grounding glow. Name card `.cs-center` `bottom:3%`, `z:var(--z-orbit-core 4)`.
- **Art slots:** `assets/hero-character.png` (transparent centerpiece, owner-provided — source `rom_data/Pictures/Main character.png`, trimmed + downscaled to ≤1300px) + `assets/hero-bg.jpg` (painted backdrop, optional). CSS wired; `onerror` removes if absent. Do not generate substitutes.

## 7. Card system  → `style.css .card*`, `.grid`

- `.grid`: `repeat(auto-fill, minmax(220px,1fr))`, gap `--space-4 16`.
- `.card`: `--surface` bg, 1px `--border`, `--r 16`, `--shadow-sm`. Hover = lift `translateY(-5px)` + coral glow + sprite scale + radial spotlight (`--mx/--my` set by `atmosphere.js`).
- `.card-head` 110px gradient header w/ dotted texture + `#id` badge; `.card-sprite img` 62px.
- Detail pages: `.detail-head` `.section` `.kv` `.statline` `.chips` — reuse as-is.

## 8. Motion language  → tokens `--dur-*`, `--ease-*`

- **Interaction:** `--dur-fast .16` (cards), `--dur .18` (nav/buttons), `--dur-mid .2`, `--dur-slow .25`. Easing `--ease` / `--ease-soft`.
- **Ambient keyframes (named, do not duplicate):** `heroAurora 18s` · `bodyAurora 26s` · `auroraDrift 16s` · `skyDrift 24s` · `halo 7s` · `plat 4s` · `spin` (orbit ring 24s / platform 16s) · `breathe 5s` (orbs, staggered) · `coreGlow 4s` · `pulseDot 1.6s` (live dot) · `sweep 4.5s` (primary button shine).
- **Hover lift** is the universal affordance. No new motion vocabulary without a spec entry.

---

## Locked vs. requires-approval

| Freely allowed (reuse) | Requires owner approval (spec change) |
|---|---|
| New page that composes existing tokens/components | Any new color, font, or base grey |
| Adding a token + documenting it here | Changing a locked width/proportion/breakpoint |
| Content (text, data, icons within existing slots) | New navbar variant / second chrome / new hero layout |
| Wiring the decorative search to real behavior | New motion keyframe or changed durations |

## Changelog
- **v1.3 — 2026-05-25:** Removed the visible orbit ring (border + dashed + conic glow) and the gold magic-platform ring (`.platform` hidden) — icons revolve on the invisible circle. Orbit icons now random from Hero/Collab/4th-Job classes; the `.cs-center` card became the Tier-S meta pick (live from `rom-rank`).
- **v1.2 — 2026-05-25:** Orbit randomizer now crossfades (no blink), runs every 10s, and pulls **Tier-S classes live from the 6v6 meta** (`rom-rank`) — single source, reflects Meta-page edits. Center confirmed as the static Main character.
- **v1.1 — 2026-05-25:** Wired global search (Enter → `index.html?q=`). Real hero character installed (trimmed + downscaled to 1300px). Orbit rebuilt as a true circle with 6 evenly-spaced (60°) orbs; icons now revolve (`orbitSpin`/`orbCounter` 44s) and randomize from a job pool every 5s; character scaled to 48%. Parallax retargeted to `.champ-art` (was clobbering child centering transforms).
- **v1 — 2026-05-25:** Foundation Lock established. Captured navbar/top-chrome (shared injector, 9 items), color, spacing, typography, atmosphere, hero proportions (panel 1180 / grid 1.16:.84 / art 520), card system, motion. Added token layer to `style.css :root`.
