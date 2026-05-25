/* atmosphere.js — premium ambient layer (performant, shared by all pages)
   - mouse-reactive ambient glow
   - floating particles inside hero (gold/blue embers)
   - subtle parallax on hero orbit/decor
   - card spotlight on hover
   single requestAnimationFrame loop · pauses on hidden tab · respects reduced-motion
   ALSO injects the shared global top chrome (navbar + server ticker) on every page. */

/* ===== shared global top chrome — runs on every page, ignores reduced-motion ===== */
(function () {
  "use strict";
  if (window.__romChrome) return; window.__romChrome = 1;

  var p = location.pathname.replace(/\\/g, "/");
  var CATS = ["monsters", "equipments", "headwears", "cards", "skills", "jobs"];
  var inSub = new RegExp("/(" + CATS.join("|") + ")/[^/]*$").test(p);
  var pre = inSub ? "../" : "";

  var ICON = {
    home: '<path d="M3 10.5 12 3l9 7.5"/><path d="M5 9.5V21h14V9.5"/>',
    monsters: '<path d="M5 21V10a7 7 0 0 1 14 0v11l-2.4-1.8L14.3 21 12 19.2 9.7 21l-2.3-1.8z"/><circle cx="9.5" cy="11.5" r="1.1"/><circle cx="14.5" cy="11.5" r="1.1"/>',
    equipments: '<path d="m13 11 7-7M17 4h3v3"/><path d="M3 21l3-.7L18.3 8.4 15.6 5.7 3.7 18z"/>',
    headwears: '<path d="M3 18h18M4.5 18l-1-9 5 3.5L12 5l3.5 7.5 5-3.5-1 9z"/>',
    jobs: '<circle cx="12" cy="8" r="3.6"/><path d="M5 20a7 7 0 0 1 14 0"/>',
    skills: '<path d="m12 3 2.6 5.3 5.8.9-4.2 4.1 1 5.8L12 16.9 6.8 19.6l1-5.8-4.2-4.1 5.8-.9z"/>',
    cards: '<rect x="3.5" y="6" width="12" height="14" rx="2"/><path d="M8 6V5a2 2 0 0 1 2-2h8a2 2 0 0 1 2 2v12a2 2 0 0 1-2 2h-1.5"/>',
    "6v6": '<path d="M12 3 20 7.5v9L12 21 4 16.5v-9z"/>',
    draft: '<path d="M4 20h16"/><path d="m14.5 4.5 5 5L8 21l-5 1 1-5z"/>',
    search: '<circle cx="11" cy="11" r="7"/><path d="m20 20-3.2-3.2"/>',
    bell: '<path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/>',
    gear: '<circle cx="12" cy="12" r="3"/><path d="M19.4 13a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1V20a2 2 0 0 1-4 0v-.2a1.6 1.6 0 0 0-2.7-1.1l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.6 1.6 0 0 0 4.6 13H4.4a2 2 0 0 1 0-4h.2a1.6 1.6 0 0 0 1.1-2.7l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.6 1.6 0 0 0 11 4.6V4.4a2 2 0 0 1 4 0v.2a1.6 1.6 0 0 0 2.7 1.1l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1A1.6 1.6 0 0 0 19.4 11h.2a2 2 0 0 1 0 4z"/>',
    login: '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4"/><path d="M10 17l5-5-5-5"/><path d="M15 12H3"/>'
  };
  function svg(k) { return '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">' + ICON[k] + '</svg>'; }

  var NAV = [
    ["home", "Home", pre + "home.html"],
    ["monsters", "Monsters", pre + "index.html#monsters"],
    ["equipments", "Equipments", pre + "index.html#equipments"],
    ["headwears", "Headwears", pre + "index.html#headwears"],
    ["jobs", "Jobs", pre + "index.html#jobs"],
    ["skills", "Skills", pre + "index.html#skills"],
    ["cards", "Cards", pre + "index.html#cards"],
    ["6v6", "6v6", pre + "6v6.html"],
    ["draft", "Draft", pre + "6v6.html"]
  ];

  function activeKey() {
    if (/home\.html$/.test(p)) return "home";
    if (/6v6\.html$/.test(p)) return "6v6";
    var m = p.match(new RegExp("/(" + CATS.join("|") + ")/[^/]*$"));
    if (m) return m[1];
    var h = (location.hash || "").replace("#", "");
    if (CATS.indexOf(h) >= 0) return h;
    return "monsters"; // index default view
  }

  var navHTML = NAV.map(function (it) {
    var dot = it[0] === "6v6" ? '<i class="nd"></i>' : "";
    return '<a href="' + it[2] + '" data-navkey="' + it[0] + '">' + svg(it[0]) + it[1] + dot + "</a>";
  }).join("");

  var topbar = document.createElement("div");
  topbar.className = "topbar";
  topbar.innerHTML =
    '<div class="wrap bar">' +
      '<a class="logo" href="' + pre + 'index.html"><span class="dot"></span><span><span class="ro">RO</span>Bugcreammm</span></a>' +
      '<nav class="hnav">' + navHTML + "</nav>" +
      '<div class="top-actions">' +
        '<label class="top-search">' + svg("search") + '<input type="text" placeholder="Search monsters, cards, skills…"><kbd>⌘K</kbd></label>' +
        '<button class="theme-btn" id="themeBtn" type="button" aria-label="Toggle theme">🌙</button>' +
        '<button class="icon-btn" type="button" aria-label="Notifications">' + svg("bell") + '<span class="ndot">3</span></button>' +
        '<a class="btn-admin" href="' + pre + '6v6.html">' + svg("gear") + "Admin</a>" +
        '<a class="btn-admin ghost" href="' + pre + '6v6.html">' + svg("login") + "Admin</a>" +
      "</div>" +
    "</div>";

  var ticker = document.createElement("div");
  ticker.className = "server-ticker";
  ticker.innerHTML =
    '<div class="wrap row">' +
      '<span class="st"><i class="dot ok"></i><b>Prontera</b> Stable</span>' +
      '<span class="st"><i class="dot ok"></i><b>Geffen</b> Stable</span>' +
      '<span class="st"><i class="dot ok"></i><b>Payon</b> Stable</span>' +
      '<span class="st"><i class="dot warn"></i><b>Izlude</b> High Load</span>' +
      '<span class="grow"></span>' +
      '<span class="ti"><b class="tag event">EVENT</b> Slayers × Eternal Love 2.0 Crossover — ends <b>23 Mar</b></span>' +
      '<span class="ti"><b class="tag patch">PATCH</b> Eternal Love 2.0 · Slayer crossover jobs · new costumes</span>' +
      '<span class="ti"><b class="tag dungeon">DUNGEON</b> Invasion</span>' +
    "</div>";

  function applyActive() {
    var k = activeKey();
    [].forEach.call(topbar.querySelectorAll(".hnav a"), function (a) {
      a.classList.toggle("active", a.getAttribute("data-navkey") === k);
    });
  }
  window.ROM_updateNav = applyActive;

  function setThemeIcon() {
    var b = topbar.querySelector("#themeBtn");
    if (b) b.textContent = document.documentElement.getAttribute("data-theme") === "dark" ? "☀️" : "🌙";
  }

  function mount() {
    var body = document.body;
    [].forEach.call(document.querySelectorAll(".topbar, .server-ticker"), function (el) {
      if (el !== topbar && el !== ticker && el.parentNode) el.parentNode.removeChild(el);
    });
    body.insertBefore(ticker, body.firstChild);
    body.insertBefore(topbar, body.firstChild);
    applyActive();
    setThemeIcon();
    topbar.querySelector("#themeBtn").addEventListener("click", function () {
      var d = document.documentElement, dark = d.getAttribute("data-theme") === "dark";
      if (dark) d.removeAttribute("data-theme"); else d.setAttribute("data-theme", "dark");
      try { localStorage.setItem("rom-theme", dark ? "" : "dark"); } catch (e) {}
      setThemeIcon();
    });

    // global search: Enter -> index.html?q=<query> (index auto-applies + scrolls)
    var si = topbar.querySelector(".top-search input");
    if (si) {
      si.addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
          var q = si.value.trim();
          if (q) location.href = pre + "index.html?q=" + encodeURIComponent(q);
        }
      });
      // ⌘K / Ctrl+K focuses the search (matches the kbd hint)
      addEventListener("keydown", function (e) {
        if ((e.metaKey || e.ctrlKey) && (e.key === "k" || e.key === "K")) {
          e.preventDefault(); si.focus();
        }
      });
    }
  }

  if (document.body) mount();
  else document.addEventListener("DOMContentLoaded", mount);
})();

/* ===== ambient atmosphere (particles, glow, parallax) ===== */
(function () {
  "use strict";
  var reduce = false;
  try { reduce = matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (e) {}
  if (reduce) return;

  var body = document.body;

  /* ---- ambient cursor glow (follows pointer, whole page) ---- */
  var glow = document.createElement("div");
  glow.className = "atmo-glow";
  body.appendChild(glow);
  var tx = innerWidth * 0.5, ty = innerHeight * 0.35, gx = tx, gy = ty;

  /* ---- hero particle field (only where a hero/champ exists) ---- */
  var hero = document.querySelector(".champ") || document.querySelector(".hero");
  var canvas, ctx, parts = [], W = 0, H = 0;
  if (hero) {
    if (getComputedStyle(hero).position === "static") hero.style.position = "relative";
    canvas = document.createElement("canvas");
    canvas.className = "atmo-canvas";
    hero.appendChild(canvas);
    ctx = canvas.getContext("2d");
    sizeCanvas();
    var n = Math.min(54, Math.round(innerWidth / 26));
    for (var i = 0; i < n; i++) parts.push(mkPart(true));
    addEventListener("resize", sizeCanvas, { passive: true });
  }
  function sizeCanvas() {
    if (!canvas) return;
    W = canvas.width = hero.clientWidth;
    H = canvas.height = hero.clientHeight;
  }
  function mkPart(spread) {
    var blue = Math.random() < 0.28;
    return {
      x: Math.random() * W,
      y: spread ? Math.random() * H : H + 6,
      r: Math.random() * 1.8 + 0.5,
      vy: Math.random() * 0.5 + 0.12,
      vx: Math.random() * 0.4 - 0.2,
      o: Math.random() * 0.5 + 0.2,
      tw: Math.random() * 6.28,
      blue: blue
    };
  }

  /* ---- parallax targets in hero ---- */
  // parallax the hero container as a whole so child transforms (orbit/character centering) are preserved
  var pxEls = hero ? hero.querySelectorAll(".champ-art, .deco, .feat-card") : [];

  addEventListener("pointermove", function (e) {
    tx = e.clientX; ty = e.clientY;
  }, { passive: true });

  /* ---- card spotlight (event delegation, cheap) ---- */
  addEventListener("pointermove", function (e) {
    var c = e.target.closest && e.target.closest(".card");
    if (!c) return;
    var r = c.getBoundingClientRect();
    c.style.setProperty("--mx", (e.clientX - r.left) + "px");
    c.style.setProperty("--my", (e.clientY - r.top) + "px");
  }, { passive: true });

  /* ---- single rAF loop ---- */
  var running = true;
  document.addEventListener("visibilitychange", function () {
    running = !document.hidden;
    if (running) requestAnimationFrame(loop);
  });

  function loop() {
    if (!running) return;
    // smooth ambient glow
    gx += (tx - gx) * 0.08;
    gy += (ty - gy) * 0.08;
    glow.style.transform = "translate3d(" + (gx - 320) + "px," + (gy - 320) + "px,0)";

    // parallax (relative to viewport center, very subtle)
    var ox = (tx / innerWidth - 0.5), oy = (ty / innerHeight - 0.5);
    for (var k = 0; k < pxEls.length; k++) {
      var depth = (k + 1) * 6;
      pxEls[k].style.transform = "translate3d(" + (-ox * depth) + "px," + (-oy * depth) + "px,0)";
    }

    // particles
    if (ctx) {
      ctx.clearRect(0, 0, W, H);
      for (var i = 0; i < parts.length; i++) {
        var p = parts[i];
        p.y -= p.vy; p.x += p.vx; p.tw += 0.03;
        if (p.y < -6 || p.x < -6 || p.x > W + 6) { parts[i] = mkPart(false); continue; }
        var a = p.o * (0.6 + 0.4 * Math.sin(p.tw));
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, 6.2832);
        ctx.fillStyle = p.blue ? "rgba(143,189,255," + a + ")" : "rgba(244,210,122," + a + ")";
        ctx.shadowBlur = 8;
        ctx.shadowColor = p.blue ? "rgba(143,189,255,.6)" : "rgba(244,210,122,.6)";
        ctx.fill();
      }
      ctx.shadowBlur = 0;
    }
    requestAnimationFrame(loop);
  }
  requestAnimationFrame(loop);
})();
