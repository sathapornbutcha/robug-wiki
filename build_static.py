# -*- coding: utf-8 -*-
"""
build_static.py — สร้างเว็บแบบ Static Wiki (index SPA เบา + หน้า detail static ต่อ record)

อ่าน normalizer จาก ../site/build_data.py (ใช้ logic เดียวกัน) แล้ว generate:
  wiki/
    index.html          ← SPA เบา: search / filter / grid (ลิงก์ไปหน้า detail)
    search-index.js      ← window.ROM_INDEX (ข้อมูลเบาๆ ต่อ record + url)
    style.css            ← (มีอยู่แล้ว)
    <cat>/<id>.html      ← static page ต่อ record (baked ทุก field, ไม่ render runtime)
    assets/icons/jobs/   ← ไอคอนอาชีพ

รัน:  python build_static.py            # ทุกหมวด (18k+ ไฟล์)
      python build_static.py jobs       # เฉพาะบางหมวด (ทดสอบ)
"""
import os, sys, html, json, shutil, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SITE = os.path.normpath(os.path.join(HERE, "..", "site"))

# import builders จาก ../site/build_data.py
spec = importlib.util.spec_from_file_location("build_data", os.path.join(SITE, "build_data.py"))
B = importlib.util.module_from_spec(spec); spec.loader.exec_module(B)

OUT = HERE
CAT_EMOJI = {"monsters":"👾","equipments":"🗡️","headwears":"🎩","cards":"🃏","skills":"✨","jobs":"⚔️"}
EL_EMOJI = {"Water":"💧","Fire":"🔥","Earth":"🪨","Wind":"🌪️","Holy":"✨","Shadow":"🌑",
            "Dark":"🌑","Undead":"🧟","Poison":"☠️","Ghost":"👻","Neutral":"⚪","Demon":"😈","Formless":"🌀"}
CAT_LABEL = {"monsters":"Monsters","equipments":"Equipments","headwears":"Headwears",
             "cards":"Cards","skills":"Skills","jobs":"Jobs"}
JOB_GROUP_ORDER = ["Hero Classes","Collab Classes","4th Job Classes","Expanded Classes","Other Classes"]

# คืนธีมจาก localStorage ก่อน render (กันจอกระพริบ)
THEME_HEAD = ('<script>try{var t=localStorage.getItem("rom-theme");if(t===null)t="dark";'
              'if(t)document.documentElement.setAttribute("data-theme",t)}catch(e){document.documentElement.setAttribute("data-theme","dark")}</script>')
THEME_FN = ('function toggleTheme(){var d=document.documentElement;'
            'var dark=d.getAttribute("data-theme")==="dark";'
            'if(dark){d.removeAttribute("data-theme")}else{d.setAttribute("data-theme","dark")}'
            'try{localStorage.setItem("rom-theme",dark?"":"dark")}catch(e){}setThemeIcon()}'
            'function setThemeIcon(){var b=document.getElementById("themeBtn");'
            'if(b)b.textContent=document.documentElement.getAttribute("data-theme")==="dark"?"☀️":"\U0001F319"}'
            'setThemeIcon();')

def e(s): return html.escape("" if s is None else str(s))

def sprite_html(cat, rec, big=False):
    if cat == "jobs":
        f = B._job_norm(rec.get("n",""))
        emoji = CAT_EMOJI["jobs"]
        # ../assets (จากหน้า detail) — index ใช้ assets/ ตรงๆ จึงส่ง prefix ผ่านพารามิเตอร์ตอนเรียก
        return ('<img src="{p}assets/icons/jobs/{f}.png" alt="{a}" loading="lazy" '
                'onerror="this.outerHTML=\'{em}\'">').format(
                    p="", f=e(f), a=e(rec.get("n","")), em=emoji)  # prefix เติมภายหลัง
    if cat == "monsters":
        return EL_EMOJI.get(rec.get("e"), CAT_EMOJI["monsters"])
    return CAT_EMOJI.get(cat, "❓")

def fmt_v(v):
    if isinstance(v, (int, float)):
        return f"{v:,}" if isinstance(v, int) else str(v)
    return str(v)

def kv_block(pairs):
    items = []
    for p in pairs or []:
        if not p or p[1] in (None, "", []):
            continue
        items.append(f'<div class="item"><div class="k">{e(p[0])}</div><div class="v">{e(fmt_v(p[1]))}</div></div>')
    return '<div class="kv">' + "".join(items) + "</div>" if items else ""

def stat_lines(pairs):
    rows = []
    for p in pairs or []:
        if not p or p[1] in (None, ""): continue
        rows.append(f'<div class="statline"><span>{e(p[0])}</span><span class="v">{e(fmt_v(p[1]))}</span></div>')
    return "".join(rows)

def chips(pairs):
    out = []
    for p in pairs or []:
        if p and p[1]:
            out.append(f'<span class="tag">{e(p[0])}: {e(p[1])}</span>')
    return "".join(out)

def ty_class(t):
    t = (t or "").lower()
    for key in ("passive","buff","active","attack","magic","toggle"):
        if key in t:
            return "ty-" + key
    return "ty-x"

def sk_item(name):
    ini = e((name or "?").strip()[:1].upper())
    return f'<span class="sk"><span class="sk-ico">{ini}</span>{e(name)}</span>'

def job_body(d):
    cls = d.get("class_skills") or []
    runes = d.get("runes") or []
    others = d.get("other_skills") or []
    details = d.get("skill_details") or []

    left = '<div class="section"><h3>Skills</h3><div class="sk-grid">' + \
           "".join(sk_item(n) for n in cls) + "</div>"
    if others:
        left += '<h3 class="sub">Other Skills</h3><div class="sk-grid">' + \
                "".join(sk_item(n) for n in others) + "</div>"
    left += "</div>"
    right = ""
    if runes:
        right = '<div class="section"><h3>Runes</h3><div class="sk-grid">' + \
                "".join(sk_item(n) for n in runes) + "</div></div>"
    cols = f'<div class="job-cols">{left}{right}</div>'

    cards = []
    for s in details:
        badges = [f'<span class="b lvl">Lvl: {e(s.get("lvl") or "?")}</span>']
        if s.get("type"):
            badges.append(f'<span class="b ty {ty_class(s["type"])}">{e(s["type"])}</span>')
        for label, key, unit in (("CD","cd"," sec"),("Skill Delay","delay"," sec"),
                                 ("SP","sp",""),("Range","range",""),("Cast Time","cast"," sec")):
            if s.get(key):
                badges.append(f'<span class="b">{label}: {e(s[key])}{unit}</span>')
        ini = e((s.get("name") or "?").strip()[:1].upper())
        cards.append(
            f'<div class="section skill-card">'
            f'<div class="sk-head"><span class="sk-ico {ty_class(s.get("type"))}">{ini}</span>'
            f'<h4>{e(s.get("name"))}</h4></div>'
            f'<div class="badges">{"".join(badges)}</div>'
            f'<div class="desc">{e(s.get("desc"))}</div></div>')
    return cols + "".join(cards)

def detail_page(cat, rid, d, rec):
    # sprite (detail page อยู่ลึก 1 ชั้น → prefix ../)
    if cat == "jobs":
        f = B._job_norm(d.get("name",""))
        sp = ('<img src="../assets/icons/jobs/%s.png" alt="%s" '
              'onerror="this.outerHTML=\'%s\'">') % (e(f), e(d.get("name","")), CAT_EMOJI["jobs"])
    elif cat == "monsters":
        sp = EL_EMOJI.get(rec.get("e"), CAT_EMOJI["monsters"])
    else:
        sp = CAT_EMOJI.get(cat, "❓")

    secs = []
    if d.get("desc"):
        secs.append(f'<div class="section"><h3>Description</h3><div class="desc">{e(d["desc"])}</div></div>')
    if d.get("base"):
        secs.append(f'<div class="section"><h3>Base Stats</h3>{kv_block(d["base"])}</div>')
    if d.get("stats"):
        title = "Combat Stats" if cat == "monsters" else "Effect"
        secs.append(f'<div class="section"><h3>{title}</h3>{stat_lines(d["stats"])}</div>')
    if d.get("info"):
        secs.append(f'<div class="section"><h3>Details</h3>{kv_block(d["info"])}</div>')
    for title, txt in (d.get("extra") or []):
        if txt:
            secs.append(f'<div class="section"><h3>{e(title)}</h3><div class="desc">{e(txt)}</div></div>')
    if d.get("more"):
        secs.append(f'<div class="section"><h3>All Fields · ข้อมูลทั้งหมด</h3>{kv_block(d["more"])}</div>')
    if d.get("zh"):
        secs.append(f'<div class="section"><h3>CN Name</h3><div class="desc">{e(d["zh"])}</div></div>')

    tag_html = chips(d.get("tags"))
    body = job_body(d) if cat == "jobs" else (
        "".join(secs) if secs else '<div class="section"><div class="desc">ไม่มีข้อมูลเพิ่มเติม</div></div>')
    return f"""<!DOCTYPE html><html lang="th"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>{e(d.get('name',rid))} · ROBugcreammm</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="../style.css">
{THEME_HEAD}
</head><body>
<div class="topbar"><div class="wrap bar">
  <a class="logo" href="../index.html"><span class="dot"></span><span><span class="ro">RO</span>Bugcreammm</span></a>
  <div class="nav"><a href="../home.html">Home</a><a href="../index.html">Database</a><a href="../6v6.html">6v6</a></div>
  <button class="theme-btn" id="themeBtn" onclick="toggleTheme()">🌙</button>
</div></div>
<div class="wrap">
  <a class="back" href="../index.html">← กลับหน้าหลัก</a>
  <div class="detail-head">
    <div class="detail-sprite">{sp}</div>
    <div class="detail-title">
      <h1>{e(d.get('name',rid))}</h1>
      <div class="detail-sub">{e(d.get('sub',''))} · {e(CAT_LABEL.get(cat,cat))} #{e(rid)}</div>
      <div class="chips">{tag_html}</div>
    </div>
  </div>
  {body}
</div>
<script>{THEME_FN}</script>
<script src="../atmosphere.js" defer></script>
</body></html>"""

INDEX_JS_TEMPLATE = r"""<!DOCTYPE html><html lang="th"><head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1.0">
<title>ROBugcreammm · Ragnarok M Database</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Outfit:wght@600;700;800&display=swap" rel="stylesheet">
<link rel="stylesheet" href="style.css">
<script>try{var t=localStorage.getItem("rom-theme");if(t===null)t="dark";if(t)document.documentElement.setAttribute("data-theme",t)}catch(e){document.documentElement.setAttribute("data-theme","dark")}</script>
</head><body>
<div class="topbar"><div class="wrap bar">
  <a class="logo" href="index.html"><span class="dot"></span><span><span class="ro">RO</span>Bugcreammm</span></a>
  <div class="nav" id="nav"></div>
  <button class="theme-btn" id="themeBtn" onclick="toggleTheme()">🌙</button>
</div></div>
<section class="hero"><div class="wrap">
  <span class="deco d1"></span><span class="deco d2"></span><span class="deco d3"></span><span class="deco d4"></span>
  <div class="hero-in">
    <span class="eyebrow">Ragnarok M · Free Database</span>
    <h1>คลังข้อมูล Ragnarok M ครบทุกอย่าง</h1>
    <p>มอนสเตอร์ · ไอเทม · การ์ด · สกิล · อาชีพ — รวมจาก ROM Handbook archive เปิดดูได้ทุกหน้า ไม่ต้องล็อกอิน</p>
    <div class="hstats" id="hstats"></div>
  </div>
</div></section>
<div class="wrap section-wrap">
  <div class="controls">
    <div class="search"><span class="ic">🔍</span><input id="q" type="text" placeholder="ค้นหาชื่อ / ID …"></div>
    <span id="filters"></span>
  </div>
  <div class="count" id="count"></div>
  <div class="grid" id="grid"></div>
</div>
<script>function toggleTheme(){var d=document.documentElement;var dark=d.getAttribute("data-theme")==="dark";if(dark){d.removeAttribute("data-theme")}else{d.setAttribute("data-theme","dark")}try{localStorage.setItem("rom-theme",dark?"":"dark")}catch(e){}setThemeIcon()}function setThemeIcon(){var b=document.getElementById("themeBtn");if(b)b.textContent=document.documentElement.getAttribute("data-theme")==="dark"?"☀️":"🌙"}setThemeIcon();</script>
<script src="search-index.js"></script>
<script>
(function(){
  var DATA = window.ROM_INDEX || [];
  var CATS = ["monsters","equipments","headwears","cards","skills","jobs"];
  var LABEL = {monsters:"Monsters",equipments:"Equipments",headwears:"Headwears",cards:"Cards",skills:"Skills",jobs:"Jobs"};
  var CAT_EMOJI = {monsters:"👾",equipments:"🗡️",headwears:"🎩",cards:"🃏",skills:"✨",jobs:"⚔️"};
  var EL_EMOJI = {Water:"💧",Fire:"🔥",Earth:"🪨",Wind:"🌪️",Holy:"✨",Shadow:"🌑",Dark:"🌑",Undead:"🧟",Poison:"☠️",Ghost:"👻",Neutral:"⚪",Demon:"😈",Formless:"🌀"};
  var GROUP_ORDER = ["Hero Classes","Collab Classes","4th Job Classes","Expanded Classes","Other Classes"];
  var STEP = 120, shown = STEP, cat = "monsters", filters = {};
  var byCat = {}; CATS.forEach(function(c){byCat[c]=[];});
  DATA.forEach(function(r){ if(byCat[r.c]) byCat[r.c].push(r); r._s=((r.n||"")+" "+r.id+" "+(r.e||"")+" "+(r.r||"")+" "+(r.sl||"")+" "+(r.z||"")).toLowerCase(); });

  function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c];});}
  function distinct(c,k){var s={};byCat[c].forEach(function(r){if(r[k]!==undefined&&r[k]!==""&&r[k]!==0)s[r[k]]=1;});return Object.keys(s).sort();}
  function sprite(r){ if(r.c==="jobs") return '<img src="assets/icons/jobs/'+esc(r.f)+'.png" loading="lazy" alt="" onerror="this.outerHTML=\''+CAT_EMOJI.jobs+'\'">'; if(r.c==="monsters") return EL_EMOJI[r.e]||CAT_EMOJI.monsters; return CAT_EMOJI[r.c]||"❓"; }

  function nav(){
    var tabs = CATS.map(function(c){
      return '<a href="#" data-c="'+c+'" class="'+(c===cat?"active":"")+'">'+LABEL[c]+'</a>';
    }).join("");
    document.getElementById("nav").innerHTML = '<a href="home.html">Home</a>'+tabs+'<a href="6v6.html">6v6</a>';
    [].forEach.call(document.querySelectorAll("#nav a[data-c]"),function(a){
      a.onclick=function(ev){ev.preventDefault();cat=a.getAttribute("data-c");filters={};shown=STEP;document.getElementById("q").value="";try{history.replaceState(null,"","#"+cat)}catch(e){}nav();renderFilters();render();};
    });
  }
  function renderFilters(){
    var host=document.getElementById("filters"), defs=[];
    if(cat==="monsters") defs=[["Element","e"],["Race","r"],["Size","sz"],["Type","ty"]];
    else if(cat==="equipments") defs=[["Type","sl"],["Quality","q"]];
    host.innerHTML = defs.map(function(d){
      var opts=distinct(cat,d[1]).map(function(o){return '<option value="'+esc(o)+'"'+(String(filters[d[1]])===String(o)?" selected":"")+'>'+(d[1]==="q"?"★".repeat(+o):esc(o))+'</option>';}).join("");
      return '<select data-f="'+d[1]+'"><option value="">'+d[0]+': ทั้งหมด</option>'+opts+'</select>';
    }).join("");
    [].forEach.call(host.querySelectorAll("select"),function(s){
      s.onchange=function(){var f=s.getAttribute("data-f");if(s.value)filters[f]=s.value;else delete filters[f];shown=STEP;render();};
    });
  }
  function filtered(){
    var q=(document.getElementById("q").value||"").toLowerCase().trim();
    var pool = q ? DATA : byCat[cat];
    return pool.filter(function(r){
      if(q && r._s.indexOf(q)<0) return false;
      if(!q) for(var f in filters){ if(String(r[f]==null?"":r[f])!==String(filters[f])) return false; }
      return true;
    });
  }
  function cardHTML(r){
    var tags="";
    if(r.c==="monsters") tags='<span class="tag">'+esc(r.r||"")+'</span><span class="tag">'+esc(r.e||"")+'</span>';
    else if(r.c==="equipments"||r.c==="headwears") tags='<span class="tag">'+esc(r.sl||"")+'</span>'+(r.q?'<span class="tag">'+"★".repeat(r.q)+'</span>':"");
    else if(r.c==="jobs") tags='<span class="tag">'+esc(r.g||"Job")+'</span>';
    else tags='<span class="tag">'+LABEL[r.c]+'</span>';
    return '<a class="card" href="'+esc(r.u)+'"><div class="card-head"><span class="badge">#'+esc(r.id)+'</span><div class="card-sprite">'+sprite(r)+'</div></div>'
      +'<div class="card-body"><div class="card-name">'+esc(r.n)+'</div><div class="tags">'+tags+'</div></div></a>';
  }
  function render(){
    var out=filtered(), grid=document.getElementById("grid");
    var q=(document.getElementById("q").value||"").trim();
    document.getElementById("count").textContent = out.length.toLocaleString()+" รายการ"+(q?" · ทุกหมวด":"");
    if(!out.length){grid.innerHTML='<div class="empty">ไม่พบรายการ</div>';return;}
    // jobs grouped (เฉพาะ browse ไม่ค้นหา)
    if(cat==="jobs" && !q){
      var by={}; out.forEach(function(r){(by[r.g]||(by[r.g]=[])).push(r);});
      var html="";
      GROUP_ORDER.forEach(function(g){
        var arr=by[g]; if(!arr||!arr.length)return;
        arr.sort(function(a,b){return g==="Other Classes"?(a.n||"").localeCompare(b.n||""):(a.gi||0)-(b.gi||0);});
        html+='<div class="group-head"><h2>'+esc(g)+'</h2><span class="gc">'+arr.length+'</span><span class="ln"></span></div>'+arr.map(cardHTML).join("");
      });
      grid.innerHTML=html; return;
    }
    out.sort(function(a,b){return (a.n||"").localeCompare(b.n||"");});
    var slice=out.slice(0,shown);
    var html=slice.map(cardHTML).join("");
    if(out.length>shown) html+='<button class="more-btn" id="more">โหลดเพิ่ม ('+(out.length-shown).toLocaleString()+')</button>';
    grid.innerHTML=html;
    var mb=document.getElementById("more"); if(mb) mb.onclick=function(){shown+=STEP*3;render();};
  }
  function hstats(){
    var el=document.getElementById("hstats"); if(!el) return;
    el.innerHTML=[[DATA.length.toLocaleString(),"รายการ"],[CATS.length,"หมวด"],["ฟรี","ไม่ต้องล็อกอิน"]]
      .map(function(s){return '<div class="hstat"><div class="n">'+s[0]+'</div><div class="l">'+s[1]+'</div></div>';}).join("");
  }
  document.getElementById("q").addEventListener("input",function(){shown=STEP;render();});
  var hc=(location.hash||"").replace("#",""); if(byCat[hc]) cat=hc;   // เปิดหมวดตาม #cat
  hstats(); nav(); renderFilters(); render();
})();
</script>
<script src="atmosphere.js" defer></script>
</body></html>"""

def write(path, content):
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def main():
    only = set(a.lower() for a in sys.argv[1:]) or None
    builders = {
        "monsters":   lambda: B.build_monsters(),
        "equipments": lambda: B.build_items("equipments", "Equipment"),
        "headwears":  lambda: B.build_items("headwears", "Headgear"),
        "cards":      lambda: B.build_items("cards", "Card"),
        "skills":     lambda: B.build_skills(),
        "jobs":       lambda: B.build_jobs(),
    }
    # ต้องรันทุก builder เพื่อให้ B.index (search index) ครบ — แต่จะเขียนหน้า detail เฉพาะที่เลือก
    details = {}
    for cat, fn in builders.items():
        details[cat] = fn()

    # search-index.js (ทุก record, เบา) — เติม url + ชื่อไฟล์ไอคอน(จ๊อบ)
    slim = []
    for r in B.index:
        o = {"id": r["id"], "n": r["n"], "c": r["c"], "u": f'{r["c"]}/{r["id"]}.html'}
        for k in ("e","r","sz","ty","sl","q","g","gi","z"):
            if r.get(k) not in (None, "", 0):
                o[k] = r[k]
        if r["c"] == "jobs":
            o["f"] = B._job_norm(r["n"])
        slim.append(o)
    write(os.path.join(OUT, "search-index.js"),
          "window.ROM_INDEX=" + json.dumps(slim, ensure_ascii=False, separators=(",", ":")) + ";")
    write(os.path.join(OUT, "index.html"), INDEX_JS_TEMPLATE)

    # คัดลอกไอคอน
    src_icons = os.path.join(SITE, "assets", "icons", "jobs")
    dst_icons = os.path.join(OUT, "assets", "icons", "jobs")
    if os.path.isdir(src_icons):
        os.makedirs(dst_icons, exist_ok=True)
        for fn in os.listdir(src_icons):
            shutil.copyfile(os.path.join(src_icons, fn), os.path.join(dst_icons, fn))

    # หน้า detail
    idx_by_id = {}
    for r in B.index:
        idx_by_id[(r["c"], r["id"])] = r
    total = 0
    for cat in builders:
        if only and cat not in only:
            continue
        d_map = details[cat]
        cdir = os.path.join(OUT, cat)
        os.makedirs(cdir, exist_ok=True)
        for rid, d in d_map.items():
            rec = idx_by_id.get((cat, rid), {})
            write(os.path.join(cdir, f"{rid}.html"), detail_page(cat, rid, d, rec))
        total += len(d_map)
        print(f"  {cat:12s} {len(d_map):6d} pages")
    print(f"index records: {len(slim)} | detail pages written: {total}")
    if only:
        print(f"(เขียน detail เฉพาะหมวด: {', '.join(only)} — หมวดอื่นมีใน search-index แต่หน้ายังไม่ถูกสร้าง)")

if __name__ == "__main__":
    main()
