# -*- coding: utf-8 -*-
"""
build_pages.py — สร้างหน้า home.html + 6v6.html (ธีมเดียวกับ wiki, static)
ดึง LEADERBOARD + RANKINGS จริงจาก ../robugcreammm.html
รัน:  python build_pages.py
"""
import os, re, json, html, importlib.util

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.normpath(os.path.join(HERE, "..", "robugcreammm.html"))
SITE = os.path.normpath(os.path.join(HERE, "..", "site"))

def e(s): return html.escape("" if s is None else str(s))

h = open(SRC, encoding="utf-8").read()

# job pool (ชื่อ + ไฟล์ไอคอน + ป้ายกลุ่ม) สำหรับ autocomplete ของ tier editor
_spec = importlib.util.spec_from_file_location("build_data", os.path.join(SITE, "build_data.py"))
B = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(B)
B.build_jobs()  # เติม B.index ด้วย jobs records
_GA = {"Hero Classes": "Hero", "Collab Classes": "Collab", "4th Job Classes": "4th",
       "Expanded Classes": "Exp", "Other Classes": "Job"}
_jobg = {B._job_norm(r["n"]): _GA.get(r.get("g"), "Job") for r in B.index if r["c"] == "jobs"}
# autocomplete pool = รูปทั้งหมดใน Pictures (รวม Main character ฯลฯ) — ไม่จำกัดแค่ job ใน DB
PIC_DIR = os.path.normpath(os.path.join(HERE, "..", "rom_data", "Pictures"))
_seen = {}
for _fn in os.listdir(PIC_DIR):
    if not _fn.lower().endswith(".png"):
        continue
    _name = os.path.splitext(_fn)[0]
    _f = B._job_norm(_name)
    if _f and _f not in _seen:
        _seen[_f] = {"n": _name, "f": _f, "b": _jobg.get(_f, "Extra")}
JOB_POOL = sorted(_seen.values(), key=lambda x: x["n"])

# ---- LEADERBOARD (600) ----
lb_raw = re.search(r"const LEADERBOARD = \[(.*?)\];", h, re.S).group(1)
LB = [{"rank": int(r), "name": n, "uid": u, "guild": g, "credit": int(c)}
      for r, n, u, g, c in re.findall(
          r'\{ rank: (\d+), name: "(.*?)", uid: "(\d+)", guild: "(.*?)", credit: (\d+) \}', lb_raw)]

# ---- RANKINGS (tiers) ----
RANK = []
for m in re.finditer(r'\{ id: ".*?", tier: "(.*?)", color: "(.*?)",\s*label: "(.*?)",\s*classes: \[(.*?)\] \}', h, re.S):
    tier, color, label, cls = m.groups()
    classes = re.findall(r'"(.*?)"', cls)
    RANK.append({"tier": tier, "color": color, "label": label, "classes": classes})

THEME_INIT = ('<script>try{var t=localStorage.getItem("rom-theme");if(t===null)t="dark";'
              'if(t)document.documentElement.setAttribute("data-theme",t)}catch(e){document.documentElement.setAttribute("data-theme","dark")}</script>')
THEME_JS = ('<script>function toggleTheme(){var d=document.documentElement;var k=d.getAttribute("data-theme")==="dark";'
            'if(k)d.removeAttribute("data-theme");else d.setAttribute("data-theme","dark");'
            'try{localStorage.setItem("rom-theme",k?"":"dark")}catch(e){}ti()}'
            'function ti(){var b=document.getElementById("themeBtn");if(b)b.textContent='
            'document.documentElement.getAttribute("data-theme")==="dark"?"☀️":"\U0001F319"}ti();</script>')

FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Outfit:wght@600;700;800&family=Space+Grotesk:wght@500;600;700&display=swap" rel="stylesheet">')

def nav(active):
    items = [("Home", "home.html"), ("Monsters", "index.html#monsters"),
             ("Jobs", "index.html#jobs"), ("Skills", "index.html#skills"),
             ("Cards", "index.html#cards"), ("6v6", "6v6.html")]
    links = "".join(f'<a href="{u}"{" class=\"active\"" if a==active else ""}>{a}</a>' for a, u in items)
    return (f'<div class="topbar"><div class="wrap bar">'
            f'<a class="logo" href="index.html"><span class="dot"></span><span><span class="ro">RO</span>Bugcreammm</span></a>'
            f'<div class="nav">{links}</div>'
            f'<button class="theme-btn" id="themeBtn" onclick="toggleTheme()">\U0001F319</button>'
            f'</div></div>')

def page(title, active, body, extra_js=""):
    return (f'<!DOCTYPE html><html lang="th"><head><meta charset="UTF-8">'
            f'<meta name="viewport" content="width=device-width,initial-scale=1.0">'
            f'<title>{e(title)} · ROBugcreammm</title>{FONTS}'
            f'<link rel="stylesheet" href="style.css"><link rel="stylesheet" href="pages.css">{THEME_INIT}</head><body>'
            f'{nav(active)}{body}{THEME_JS}{extra_js}<script src="atmosphere.js" defer></script></body></html>')

# ================= HOME =================
ORBS = [("Hela","hela","pos-tl","#b06bff"),("Saint","saint","pos-tr","#4ade80"),
        ("Yamata","yamata","pos-l","#a855f7"),("Khalitzburg","khalitzburg","pos-r","#60a5fa"),
        ("Ancient Artifact User","ancientartifactuser","pos-bl","#f4d27a"),
        ("Spirit Whisperer","spiritwhisperer","pos-br","#fbbf24")]
orb_html = "".join(
    f'<div class="orb {p}" style="--og:{col}"><img src="assets/icons/jobs/{f}.png" alt="{e(n)}" '
    f'onerror="this.parentNode.classList.add(\'noimg\')"><span class="orb-label">{e(n)}</span></div>'
    for n, f, p, col in ORBS)

home_stats = [("148K","PARTICIPANTS"),("32","REWARDS"),("S+","TIER DROP"),("4×","EXP BOOST")]
home_body = f'''
<div class="server-ticker"><div class="wrap row">
  <span class="st"><i class="dot ok"></i><b>Prontera</b> Stable</span>
  <span class="st"><i class="dot ok"></i><b>Geffen</b> Stable</span>
  <span class="st"><i class="dot ok"></i><b>Payon</b> Stable</span>
  <span class="st"><i class="dot warn"></i><b>Izlude</b> High Load</span>
  <span class="grow"></span>
  <span class="ti"><b class="tag event">EVENT</b> Slayers × Eternal Love 2.0 Crossover — ends <b>23 Mar</b></span>
</div></div>
<section class="champ">
  <img class="champ-bg-art" src="assets/hero-bg.jpg" alt="" onerror="this.remove()">
  <div class="champ-sky"></div>
  <div class="champ-city"></div>
  <div class="wrap champ-grid">
  <div class="champ-left">
    <span class="live"><i></i> LIVE NOW</span>
    <div class="eyb">OFFICIAL ESPORTS EVENT · SEASON 3</div>
    <h1>Ragnarok M: <span class="g">Eternal Love</span><br>Championship Season 3</h1>
    <p>การแข่งขัน Ragnarok M ที่ใหญ่ที่สุดแห่งปี — 64 กิลด์ชั้นนำจาก 4 เซิร์ฟเวอร์ ชิง <b>Crown of Midgard</b> และเงินรางวัล <b>1,000,000 zeny</b> ดูสด ส่งกิลด์เข้าแข่ง หรือทายผลสายได้เลย</p>
    <div class="cd" id="cd">
      <div class="u"><div class="n" id="cdD">--</div><div class="l">DAYS</div></div>
      <div class="u"><div class="n" id="cdH">--</div><div class="l">HOURS</div></div>
      <div class="u"><div class="n" id="cdM">--</div><div class="l">MINUTES</div></div>
      <div class="u"><div class="n" id="cdS">--</div><div class="l">SECONDS</div></div>
    </div>
    <div class="champ-btns">
      <a class="btn-primary" href="6v6.html">Explore Championship →</a>
      <a class="btn-ghost" href="6v6.html">🏆 View Rewards</a>
    </div>
    <div class="hstats">{"".join(f'<div class="hstat"><div class="n">{e(v)}</div><div class="l">{e(l)}</div></div>' for v,l in home_stats)}</div>
  </div>
  <div class="champ-art">
    <div class="cs-orbit">{orb_html}</div>
    <div class="platform"></div>
    <img class="champ-hero-art" src="assets/hero-character.png" alt="" onerror="this.remove()">
    <div class="cs-center"><img src="assets/icons/jobs/hela.png" alt="Hela" onerror="this.style.display='none'"><div><div class="cn">Hela</div><div class="cc">1st Class</div></div></div>
  </div>
</div></section>'''
home_js = '''<script>
(function(){var t=new Date();t.setDate(t.getDate()+10);t.setHours(t.getHours()+19);var T=t.getTime();
function p(n){return(n<10?"0":"")+n}
function tick(){var d=Math.max(0,T-Date.now()),s=Math.floor(d/1000);
document.getElementById("cdD").textContent=p(Math.floor(s/86400));
document.getElementById("cdH").textContent=p(Math.floor(s%86400/3600));
document.getElementById("cdM").textContent=p(Math.floor(s%3600/60));
document.getElementById("cdS").textContent=p(s%60);}
tick();setInterval(tick,1000);})();
</script>'''

# ================= 6v6 =================
tiers_html = ""
for r in RANK:
    chips = "".join(f'<a class="tchip" href="index.html#jobs">{e(c)}</a>' for c in r["classes"])
    tiers_html += (f'<div class="tier-row"><div class="tier-badge" style="background:{e(r["color"])}">{e(r["tier"])}</div>'
                   f'<div class="tier-body"><div class="tier-label">{e(r["label"])}</div><div class="tchips">{chips}</div></div></div>')
top = RANK[0] if RANK else {"tier":"S","color":"#ef4444","label":"","classes":[]}
feat_chips = "".join(f'<span class="tchip">{e(c)}</span>' for c in top["classes"][:4])
if len(top["classes"])>4: feat_chips += f'<span class="tchip">+{len(top["classes"])-4}</span>'
sixv6_body = f'''
<section class="hero hero-6v6"><div class="wrap">
  <span class="deco d3"></span>
  <div class="six-grid">
    <div class="hero-in">
      <span class="eyebrow">PvP meta</span>
      <h1 style="background:linear-gradient(135deg,var(--coral),var(--pink));-webkit-background-clip:text;background-clip:text;color:transparent">6v6</h1>
      <p>อันดับ tier ของอาชีพในโหมด 6v6 PvP — อัปเดตตามเมตา SS24</p>
      <div class="hstats">
        <div class="hstat"><div class="n">{len(RANK)}</div><div class="l">TIERS</div></div>
        <div class="hstat"><div class="n">{sum(len(r["classes"]) for r in RANK)}</div><div class="l">RANKED CLASSES</div></div>
        <div class="hstat"><div class="n">6v6</div><div class="l">MODE</div></div>
      </div>
    </div>
    <div class="feat-card">
      <div class="fc-top"><span>★ 6v6 META</span><span class="fc-pill" style="background:{e(top["color"])}22;color:{e(top["color"])}">{e(top["tier"])}-TIER</span></div>
      <div class="fc-name">{e(top["tier"])}-Tier</div><div class="fc-sub">{e(top["label"])}</div>
      <div class="fc-art">🏆</div>
      <div class="tchips">{feat_chips}</div>
    </div>
  </div>
</div></section>
<div class="wrap section-wrap">
  <div class="tl-head">
    <h2 class="page-h">6v6 Tier list — Meta in SS24</h2>
    <div class="tl-actions">
      <button class="lb-edit" id="tierEdit" onclick="tierEditClick()">✎ Edit</button>
      <span class="tier-admin" id="tierAdmin">
        <button class="btn-mini" onclick="tAddTier()">+ Tier</button>
        <button class="btn-mini save" onclick="tierSave()">💾 บันทึก</button>
        <button class="btn-mini ghost" onclick="tierCancel()">ยกเลิก</button>
      </span>
    </div>
  </div>
  <div class="tier-list" id="tierList"></div>
  <div class="lb-card">
    <div class="lb-head"><h3>🏆 Top Rankings</h3>
      <div class="lb-head-r"><span class="lb-season">SEASON SS24 · TOP {len(LB)}</span>
        <button class="lb-edit" id="lbEdit" onclick="lbEditClick()">✎ Edit</button></div>
    </div>
    <div class="lb-search"><input id="lbq" placeholder="ค้นหาด้วยชื่อ, UID, หรือ Guild..."></div>
    <div class="lb-admin" id="lbAdmin">
      <button class="btn-mini" onclick="lbAdd()">+ เพิ่มแถว</button>
      <button class="btn-mini save" onclick="lbSave()">💾 บันทึก</button>
      <button class="btn-mini ghost" onclick="lbCancel()">ยกเลิก</button>
      <button class="btn-mini ghost" onclick="lbLogout()">ออกจากระบบ</button>
      <span class="lb-note">* แก้ไขบันทึกในเบราว์เซอร์นี้เท่านั้น (static · ไม่มีเซิร์ฟเวอร์)</span>
    </div>
    <div class="lb-table">
      <div class="lb-row lb-th"><span>อันดับ</span><span>ชื่อ (NAME)</span><span>กิลด์ (GUILD)</span><span class="r">คะแนน</span></div>
      <div id="lbBody"></div>
    </div>
  </div>
  <div class="modal-ov" id="lbLogin" onclick="if(event.target===this)lbCloseLogin()">
    <div class="modal-bx">
      <h4>🔒 เข้าสู่ระบบแอดมิน</h4>
      <p class="mb-sub">กรอกรหัสผ่านเพื่อแก้ไข Top Rankings</p>
      <input type="password" id="lbPw" placeholder="รหัสผ่านแอดมิน">
      <div class="lb-err" id="lbErr"></div>
      <div class="modal-btns"><button class="btn-mini ghost" onclick="lbCloseLogin()">ปิด</button><button class="btn-mini save" onclick="lbDoLogin()">เข้าสู่ระบบ</button></div>
    </div>
  </div>
</div>'''
sixv6_js = ('<script>window.LB_DEFAULT=' + json.dumps(LB, ensure_ascii=False, separators=(",", ":")) +
            ';window.RANK_DEFAULT=' + json.dumps(RANK, ensure_ascii=False, separators=(",", ":")) +
            ';window.JOB_POOL=' + json.dumps(JOB_POOL, ensure_ascii=False, separators=(",", ":")) + ''';
(function(){
var ADMIN_PW="RO@Admin2024";          /* ประตู UI เท่านั้น — ไม่ใช่ security จริง */
var LB,RANK,lbEdit=false,tierEdit=false,expanded=null,pending=null;
var q=document.getElementById("lbq"),body=document.getElementById("lbBody"),tl=document.getElementById("tierList");
function esc(s){return String(s==null?"":s).replace(/[&<>"']/g,function(c){return({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#39;"})[c]})}
function authed(){try{return sessionStorage.getItem("rom-admin")==="1"}catch(e){return false}}

/* ---------- shared admin login ---------- */
function requireAdmin(cb){if(authed()){cb()}else{pending=cb;document.getElementById("lbLogin").classList.add("show");setTimeout(function(){document.getElementById("lbPw").focus()},50)}}
window.lbDoLogin=function(){if(document.getElementById("lbPw").value===ADMIN_PW){try{sessionStorage.setItem("rom-admin","1")}catch(e){}lbCloseLogin();var cb=pending;pending=null;if(cb)cb()}else{document.getElementById("lbErr").textContent="รหัสผ่านไม่ถูกต้อง"}};
window.lbCloseLogin=function(){document.getElementById("lbLogin").classList.remove("show");document.getElementById("lbPw").value="";document.getElementById("lbErr").textContent=""};
window.lbLogout=function(){try{sessionStorage.removeItem("rom-admin")}catch(e){}lbCancel();tierCancel()};

/* ---------- leaderboard ---------- */
function lbLoad(){try{var s=localStorage.getItem("rom-lb");LB=s?JSON.parse(s):window.LB_DEFAULT.slice()}catch(e){LB=window.LB_DEFAULT.slice()}}
function filt(){var s=(q.value||"").toLowerCase().trim();return s?LB.filter(function(e){return(e.name||"").toLowerCase().indexOf(s)>=0||(e.uid||"").indexOf(s)>=0||(e.guild||"").toLowerCase().indexOf(s)>=0}):LB}
function nRow(e){var t=e.rank<=3?(" top"+e.rank):"",ex=expanded===e.rank;
  var h='<div class="lb-row lb-click" onclick="lbToggle('+e.rank+')"><span class="lb-rank'+t+'">'+e.rank+'</span><span class="lb-name">'+esc(e.name)+' <i class="caret">'+(ex?"▾":"▸")+'</i></span><span class="lb-guild">'+esc(e.guild)+'</span><span class="r lb-cr">'+e.credit+'</span></div>';
  if(ex)h+='<div class="lb-expand"><span class="le-k">UID</span><code class="le-uid">'+esc(e.uid||"-")+'</code><button class="copy-btn" onclick="lbCopy(\\''+esc(e.uid||"")+'\\',this,event)">📋 Copy UID</button><span class="le-k">GUILD</span><span class="le-g">'+esc(e.guild||"None")+'</span></div>';
  return h}
function eRow(e,i){return '<div class="lb-row lb-edit-row"><span class="lb-rank">'+e.rank+'</span>'
  +'<span class="ecell"><input class="ei" value="'+esc(e.name)+'" oninput="LB['+i+'].name=this.value" placeholder="ชื่อ"><input class="ei sm" value="'+esc(e.uid)+'" oninput="LB['+i+'].uid=this.value" placeholder="UID"></span>'
  +'<span><input class="ei" value="'+esc(e.guild)+'" oninput="LB['+i+'].guild=this.value" placeholder="Guild"></span>'
  +'<span class="r"><input class="ei num" type="number" value="'+e.credit+'" oninput="LB['+i+'].credit=parseInt(this.value)||0"><button class="rm" onclick="lbRemove('+i+')">✕</button></span></div>'}
function render(){var d=filt();
  if(lbEdit){body.innerHTML=d.slice(0,200).map(function(e){return eRow(e,LB.indexOf(e))}).join("")}
  else{body.innerHTML=d.slice(0,200).map(nRow).join("")||'<div class="lb-row"><span>ไม่พบ</span></div>'}}
function reRank(){LB.forEach(function(e,i){e.rank=i+1})}
function lbEnter(){lbEdit=true;expanded=null;document.getElementById("lbAdmin").classList.add("on");document.getElementById("lbEdit").style.display="none";render()}
function lbExit(){lbEdit=false;document.getElementById("lbAdmin").classList.remove("on");document.getElementById("lbEdit").style.display="";render()}
window.lbToggle=function(r){if(lbEdit)return;expanded=expanded===r?null:r;render()};
window.lbCopy=function(uid,btn,ev){ev&&ev.stopPropagation();try{navigator.clipboard.writeText(uid);btn.textContent="✓ Copied";setTimeout(function(){btn.textContent="📋 Copy UID"},1200)}catch(e){}};
window.lbEditClick=function(){requireAdmin(lbEnter)};
window.lbAdd=function(){LB.unshift({rank:0,name:"New Player",uid:"",guild:"None",credit:0});reRank();render()};
window.lbRemove=function(i){LB.splice(i,1);reRank();render()};
window.lbSave=function(){reRank();try{localStorage.setItem("rom-lb",JSON.stringify(LB))}catch(e){}lbExit()};
window.lbCancel=function(){lbLoad();lbExit()};

/* ---------- tier list (icons + autocomplete) ---------- */
function tierLoad(){try{var s=localStorage.getItem("rom-rank");RANK=s?JSON.parse(s):window.RANK_DEFAULT.slice()}catch(e){RANK=window.RANK_DEFAULT.slice()}if(!Array.isArray(RANK))RANK=window.RANK_DEFAULT.slice()}
function jf(name){return String(name||"").normalize("NFKD").replace(/[̀-ͯ]/g,"").toLowerCase().replace(/[^a-z0-9]/g,"")}
function cIcon(name){var f=jf(name);return '<img class="tci" src="assets/icons/jobs/'+f+'.png" alt="" loading="lazy" onerror="this.outerHTML=\\'<span class=&quot;tci fb&quot;>'+esc((name||"?").charAt(0))+'</span>\\'">'}
function cap(label){return esc(String(label||"").split("·")[0].trim().toUpperCase())}
function badge(r,edit,i){
  if(edit)return '<div class="tier-badge edit" style="background:'+esc(r.color)+'"><input class="tletter" value="'+esc(r.tier)+'" maxlength="3" oninput="RANK['+i+'].tier=this.value"><input class="tcolor" type="color" value="'+esc(r.color)+'" oninput="RANK['+i+'].color=this.value;document.querySelectorAll(\\'.tier-badge\\')['+i+'].style.background=this.value"></div>';
  return '<div class="tier-badge" style="background:'+esc(r.color)+'"><span class="tletter-v">'+esc(r.tier)+'</span><span class="tlabel">'+cap(r.label)+'</span></div>';
}
function tierRender(){
  if(tierEdit){
    tl.innerHTML=RANK.map(function(r,i){
      var chips=(r.classes||[]).map(function(c,j){return '<span class="tchip ed">'+cIcon(c)+esc(c)+'<button class="cx" onclick="tDelCls('+i+','+j+')">✕</button></span>'}).join("");
      return '<div class="tier-row">'+badge(r,true,i)
        +'<div class="tier-body"><input class="ei" value="'+esc(r.label)+'" placeholder="คำอธิบาย tier" oninput="RANK['+i+'].label=this.value">'
        +'<div class="tchips">'+chips+'</div>'
        +'<div class="add-wrap"><input class="ei addcls" placeholder="🔍 พิมพ์ค้นหาอาชีพ…" oninput="tFilter('+i+',this.value)" onfocus="tFilter('+i+',this.value)" onblur="tBlur('+i+')" onkeydown="tKey(event,'+i+')">'
        +'<button class="btn-mini save" onclick="tierSave()">💾 Save</button>'
        +'<div class="ac-list" id="ac'+i+'"></div></div>'
        +'<button class="btn-mini ghost del-tier" onclick="tDelTier('+i+')">ลบ Tier นี้</button></div></div>';
    }).join("");
  } else {
    tl.innerHTML=RANK.map(function(r){
      var chips=(r.classes||[]).map(function(c){return '<a class="tchip" href="index.html#jobs">'+cIcon(c)+esc(c)+'</a>'}).join("");
      return '<div class="tier-row">'+badge(r,false)
        +'<div class="tier-body"><div class="tier-label">'+esc(r.label)+'</div><div class="tchips">'+chips+'</div></div></div>';
    }).join("");
  }
}
window.tFilter=function(i,v){var el=document.getElementById("ac"+i);if(!el)return;var q=(v||"").toLowerCase().trim();
  var ex={};(RANK[i].classes||[]).forEach(function(c){ex[c.toLowerCase()]=1});
  var m=window.JOB_POOL.filter(function(j){return !ex[j.n.toLowerCase()]&&(!q||j.n.toLowerCase().indexOf(q)>=0)}).slice(0,14);
  el.innerHTML=m.map(function(j){return '<div class="ac-item" onmousedown="tPick('+i+',\\''+esc(j.n).replace(/'/g,"&#39;")+'\\')"><img class="tci" src="assets/icons/jobs/'+j.f+'.png" loading="lazy" onerror="this.style.visibility=\\'hidden\\'"><span class="acn">'+esc(j.n)+'</span><span class="acb">'+esc(j.b)+'</span></div>'}).join("");
  el.classList.add("on");};
window.tBlur=function(i){setTimeout(function(){var el=document.getElementById("ac"+i);if(el)el.classList.remove("on")},180)};
window.tPick=function(i,name){RANK[i].classes=RANK[i].classes||[];RANK[i].classes.push(name);tierRender()};
window.tKey=function(ev,i){if(ev.key==="Enter"){var v=ev.target.value.trim();if(v){RANK[i].classes=(RANK[i].classes||[]).concat([v]);tierRender()}}};
function tierEnter(){tierEdit=true;document.getElementById("tierAdmin").classList.add("on");document.getElementById("tierEdit").style.display="none";tierRender()}
function tierExit(){tierEdit=false;document.getElementById("tierAdmin").classList.remove("on");document.getElementById("tierEdit").style.display="";tierRender()}
window.tierEditClick=function(){requireAdmin(tierEnter)};
window.tDelCls=function(i,j){RANK[i].classes.splice(j,1);tierRender()};
window.tAddTier=function(){var add=function(){RANK.push({tier:"?",color:"#8b8fa0",label:"New tier",classes:[]});tierRender()};if(!tierEdit){requireAdmin(function(){tierEnter();add()})}else add()};
window.tDelTier=function(i){RANK.splice(i,1);tierRender()};
window.tierSave=function(){try{localStorage.setItem("rom-rank",JSON.stringify(RANK))}catch(e){}tierExit()};
window.tierCancel=function(){tierLoad();tierExit()};

/* ---------- init ---------- */
var pw=document.getElementById("lbPw");if(pw)pw.addEventListener("keydown",function(e){if(e.key==="Enter")lbDoLogin()});
lbLoad();tierLoad();q.addEventListener("input",render);render();tierRender();
})();</script>''')

def w(name, content):
    with open(os.path.join(HERE, name), "w", encoding="utf-8") as f:
        f.write(content)

w("home.html", page("Home", "Home", home_body, home_js))
w("6v6.html", page("6v6 Tier List", "6v6", sixv6_body, sixv6_js))
print("wrote home.html + 6v6.html | leaderboard rows:", len(LB), "| tiers:", len(RANK))
