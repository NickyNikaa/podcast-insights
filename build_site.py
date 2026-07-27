# -*- coding: utf-8 -*-
import json, glob, re, os
HERE=os.path.dirname(os.path.abspath(__file__))
from collections import Counter

# Evergreen allowlist: older (<=2024) entries worth keeping, relabeled "Zeitlos"
EVERGREEN = {
 "Der schwierige Weg zur AGI bei OpenAI","Skalierungsgesetze treiben Claude und AGI",
 "LLMs führen nicht zur echten AGI","15 Jahre Hölle bevor KI uns hilft",
 "KI verändert Sprache, Macht und Vertrauen","Godfather of AI warnt vor Kontrollverlust",
 "12 rohe Wahrheiten über Macht und Respekt","Emotionen werden vom Gehirn konstruiert",
 "Stress, Testosteron und freier Wille","Dopamin steuern statt jagen",
 "Werkzeugkasten für besseren Fokus","Fokus verändert dein Gehirn","Schlaf als Lernverstärker",
 "Identität schlägt Ziele","Beschäftigt sein tötet Produktivität","Warum du ständig erschöpft bist",
 "Umgebung gestalten statt Willenskraft",
 "Das FATE-Modell der Beeinflussung","Authority strahlt man aus",
 "Identität ist der #1 Hebel der Persuasion","Die Blinzelrate verrät Stress",
 "Elicitation: Aussagen statt Fragen","Spiegeln nach der 3er-Regel",
 "Disziplin = das Zukunfts-Ich priorisieren",
 "Ex-Google-Manager schlägt Alarm zu KI-Gefahren","Die Zukunft der KI hängt von uns ab",
 "Die Glücksformel des Google-Ingenieurs","Letzte Warnung: Bedrohung für die Menschheit",
 "AGI noch in diesem Jahrzehnt erwartet","Grundeinkommen-Studie: Hilfe, kein Allheilmittel",
 "Überzeugung und Fokus für Gründer","Skalierungsgesetze treiben KI Richtung Menschenniveau",
 "Machines of Loving Grace: 100 Jahre Biologie in 10","Ein 'Wettlauf nach oben' bei KI-Sicherheit",
}

rows=[]
for f in sorted(sorted(glob.glob(os.path.join(HERE,'data','*.json')))):
    rows+=json.load(open(f,encoding='utf-8'))

clean=[]; seen=set(); dropped=0
for r in rows:
    url=(r.get('url') or '').strip()
    if not url.startswith('http'): continue
    title=r.get('title','').strip(); source=r.get('source','').strip()
    key=(title.lower(), source.lower())
    if key in seen: continue
    kw=r.get('keywords',''); kw=' '.join(kw) if isinstance(kw,list) else kw
    date=(r.get('date') or '').strip()
    m=re.match(r'(\d{4})(?:-(\d{2}))?', date)
    if m:
        year=int(m.group(1)); month=int(m.group(2) or 0)
    else:
        year=None; month=0
    # prune / bucket
    if year is None:
        bucket="Zeitlos"; sortkey=1  # evergreen frameworks (no date)
    elif year>=2025:
        bucket=str(year); sortkey=year*100+month
    else:  # year <= 2024
        if title in EVERGREEN:
            bucket="Zeitlos"; sortkey=1
        else:
            dropped+=1; continue
    seen.add(key)
    clean.append({'topic':r.get('topic','').strip() or 'Sonstiges','pod':r.get('pod','').strip(),
        'guest':r.get('guest','').strip(),'title':title,'insight':r.get('insight','').strip(),
        'source':source,'url':url,'keywords':kw,'date':date or 'Zeitlos','bucket':bucket,'sortkey':sortkey})

# sort newest first; Zeitlos (sortkey=1) at the end
clean.sort(key=lambda d: d['sortkey'], reverse=True)

cnt=Counter(c['topic'] for c in clean); bcnt=Counter(c['bucket'] for c in clean)
topics=[t for t,_ in cnt.most_common()]
print('Kept:',len(clean),'| dropped(old news):',dropped)
print('Topics:',dict(cnt)); print('Buckets:',dict(bcnt))

DATA_JSON=json.dumps(clean, ensure_ascii=False, separators=(',',':'))
TOPICS_JSON=json.dumps(topics, ensure_ascii=False)
# period order for chips
periods=["2026","2025","Zeitlos"]
PERIODS_JSON=json.dumps([p for p in periods if p in bcnt], ensure_ascii=False)

CSS = """
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');
  :root{ --bg:#f7f6f3; --surface:#ffffff; --surface-2:#f2f0ea; --text:#15151a; --muted:#74747c; --border:rgba(20,20,35,.10); --ink:#16161b; --shadow:0 1px 2px rgba(20,20,40,.04),0 6px 22px rgba(20,20,40,.06); --grad:linear-gradient(120deg,#6366f1,#8b5cf6,#ec4899,#f97316); --fresh-bg:#eceefe; --fresh-tx:#5757d4; --ok-bg:#e7f6ed; --ok-tx:#1c8a4e; --warn-bg:#fbf0dd; --warn-tx:#b9791b; --danger-bg:#fbe7e7; --danger-tx:#c0453f; }
  *{ box-sizing:border-box; margin:0; padding:0; }
  body{ position:relative; font-family:'Inter',-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif; background:var(--bg); color:var(--text); line-height:1.55; padding:0 0 70px; -webkit-font-smoothing:antialiased; }
  body::before{ content:""; position:absolute; top:0; left:0; right:0; height:460px; z-index:0; pointer-events:none; opacity:.85; background:radial-gradient(50% 60% at 22% 12%,rgba(99,102,241,.50),transparent 62%),radial-gradient(48% 58% at 78% 16%,rgba(236,72,153,.46),transparent 60%),radial-gradient(60% 65% at 55% 48%,rgba(249,115,22,.38),transparent 62%),radial-gradient(45% 55% at 90% 50%,rgba(139,92,246,.34),transparent 60%); }

  header{ position:relative; z-index:1; padding:52px 24px 8px; max-width:1180px; margin:0 auto; text-align:center; }
  header .kicker{ display:inline-block; font-size:12.5px; letter-spacing:1.5px; text-transform:uppercase; font-weight:800; background:var(--grad); -webkit-background-clip:text; background-clip:text; color:transparent; }
  header h1{ font-size:44px; font-weight:800; letter-spacing:-1px; margin:12px 0 10px; color:var(--ink); }
  header p{ color:var(--muted); font-size:15.5px; max-width:690px; margin:0 auto; }
  header p strong{ color:var(--text); font-weight:700; }

  .topnav{ position:relative; z-index:1; max-width:1180px; margin:22px auto 0; padding:0 24px; display:flex; flex-wrap:wrap; gap:10px; justify-content:center; }
  .navbtn{ display:inline-flex; align-items:center; gap:7px; padding:11px 18px; border-radius:999px; font-size:14px; font-weight:600; text-decoration:none; border:1px solid var(--border); background:var(--surface); color:var(--text); box-shadow:var(--shadow); transition:transform .14s,box-shadow .14s; }
  .navbtn:hover{ transform:translateY(-1px); box-shadow:0 6px 18px rgba(20,20,40,.10); }
  .navbtn.active{ background:var(--ink); color:#fff; border-color:var(--ink); cursor:default; }
  .navbtn.active:hover{ transform:none; }

  .controls{ position:relative; z-index:1; max-width:1180px; margin:28px auto 0; padding:0 24px; }
  .searchrow{ display:flex; gap:10px; }
  #search{ flex:1; padding:16px 20px; font-size:16px; background:var(--surface); border:1px solid var(--border); border-radius:16px; color:var(--text); outline:none; box-shadow:var(--shadow); transition:box-shadow .15s,border-color .15s; }
  #search:focus{ border-color:#cdccdd; box-shadow:0 0 0 4px rgba(99,102,241,.13); }
  #search::placeholder{ color:#9a9aa2; }
  #searchBtn{ padding:0 30px; font-size:15px; font-weight:600; background:var(--ink); color:#fff; border:none; border-radius:16px; cursor:pointer; transition:opacity .15s; white-space:nowrap; }
  #searchBtn:hover{ opacity:.9; }
  #clearBtn{ padding:0 18px; font-size:14px; background:var(--surface); color:var(--muted); border:1px solid var(--border); border-radius:16px; cursor:pointer; }
  #clearBtn:hover{ color:var(--text); }
  .filterlabel{ font-size:11px; text-transform:uppercase; letter-spacing:1px; color:#9a9aa2; margin:18px 0 8px; font-weight:700; }
  .filters{ display:flex; flex-wrap:wrap; gap:8px; }
  .chip{ padding:8px 15px; font-size:13px; border-radius:999px; border:1px solid var(--border); background:var(--surface); color:var(--muted); cursor:pointer; transition:all .15s; user-select:none; }
  .chip:hover{ color:var(--text); border-color:#cdccdd; }
  .chip.active{ background:var(--ink); border-color:var(--ink); color:#fff; font-weight:600; }
  .chip.period.active{ background:var(--ink); border-color:var(--ink); color:#fff; }
  .count{ max-width:1180px; margin:22px auto 0; padding:0 24px; color:var(--muted); font-size:13px; }
  .grid{ max-width:1180px; margin:12px auto 0; padding:0 24px; display:grid; grid-template-columns:repeat(auto-fill,minmax(330px,1fr)); gap:18px; }
  .card{ background:var(--surface); border:1px solid var(--border); border-radius:18px; padding:22px; display:flex; flex-direction:column; box-shadow:var(--shadow); transition:transform .14s,box-shadow .14s; }
  .card:hover{ transform:translateY(-3px); box-shadow:0 10px 32px rgba(20,20,40,.10); }
  .badges{ display:flex; flex-wrap:wrap; gap:6px; margin-bottom:12px; align-items:center; }
  .badge{ font-size:11px; letter-spacing:.2px; padding:4px 11px; border-radius:999px; font-weight:600; }
  .badge.topic{ background:var(--surface-2); color:#4a4a53; text-transform:uppercase; letter-spacing:.4px; }
  .badge.pod{ background:transparent; color:var(--muted); border:1px solid var(--border); }
  .badge.date{ margin-left:auto; color:#9a9aa2; font-weight:600; }
  .badge.date.is2026{ background:var(--fresh-bg); color:var(--fresh-tx); }
  .card h3{ font-size:17px; font-weight:700; margin-bottom:8px; line-height:1.35; color:var(--ink); }
  .card p{ font-size:14.5px; color:#55555e; flex-grow:1; }
  .card .src{ margin-top:16px; padding-top:13px; border-top:1px solid var(--border); font-size:12.5px; color:var(--muted); display:flex; justify-content:space-between; align-items:center; gap:10px; }
  .card .src .who{ flex:1; }
  .card .src a{ color:var(--text); text-decoration:none; font-weight:700; white-space:nowrap; }
  .card .src a:hover{ color:#ec4899; }
  .empty{ max-width:1180px; margin:40px auto; padding:0 24px; text-align:center; color:var(--muted); }
  footer{ max-width:1180px; margin:54px auto 0; padding:26px 24px; text-align:center; color:var(--muted); font-size:12.5px; border-top:1px solid var(--border); }
  footer a{ color:var(--text); font-weight:600; }
  mark{ background:linear-gradient(120deg,rgba(236,72,153,.28),rgba(249,115,22,.28)); color:var(--ink); padding:0 3px; border-radius:4px; }
  @media (max-width:560px){ .searchrow{ flex-wrap:wrap } #searchBtn,#clearBtn{ flex:1 } header h1{ font-size:34px } }
"""

JS = """
const TOPICS=__TOPICS__, PERIODS=__PERIODS__;
let activeTopic="Alle", activePeriod="Alle", query="";
const grid=document.getElementById("grid"), tfilters=document.getElementById("topicfilters"),
      pfilters=document.getElementById("periodfilters"), countEl=document.getElementById("count"),
      emptyEl=document.getElementById("empty"), searchEl=document.getElementById("search"),
      btn=document.getElementById("searchBtn"), clearBtn=document.getElementById("clearBtn");
["Alle",...PERIODS].forEach(p=>{
  const chip=document.createElement("div");
  chip.className="chip period"+(p==="Alle"?" active":""); chip.textContent=p==="Alle"?"Alle Zeiträume":(p==="Zeitlos"?"Zeitlos / Klassiker":p);
  chip.onclick=()=>{ activePeriod=p; pfilters.querySelectorAll(".chip").forEach(c=>c.classList.remove("active")); chip.classList.add("active"); render(); };
  pfilters.appendChild(chip);
});
["Alle",...TOPICS].forEach(t=>{
  const chip=document.createElement("div");
  chip.className="chip"+(t==="Alle"?" active":""); chip.textContent=t==="Alle"?"Alle Themen":t;
  chip.onclick=()=>{ activeTopic=t; tfilters.querySelectorAll(".chip").forEach(c=>c.classList.remove("active")); chip.classList.add("active"); render(); };
  tfilters.appendChild(chip);
});
function escapeHtml(s){return String(s).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));}
function highlight(t,q){const safe=escapeHtml(t); if(!q) return safe; const re=new RegExp("("+q.replace(/[.*+?^${}()|[\\]\\\\]/g,"\\\\$&")+")","gi"); return safe.replace(re,"<mark>$1</mark>");}
function doSearch(){ query=searchEl.value; render(); }
function render(){
  const q=query.trim().toLowerCase();
  const items=DATA.filter(d=>{
    const tOk=activeTopic==="Alle"||d.topic===activeTopic;
    const pOk=activePeriod==="Alle"||d.bucket===activePeriod;
    const text=(d.title+" "+d.insight+" "+d.source+" "+d.topic+" "+d.pod+" "+d.guest+" "+d.keywords+" "+d.date).toLowerCase();
    return tOk&&pOk&&(!q||text.includes(q));
  });
  countEl.textContent=items.length+(items.length===1?" Insight":" Insights")+" · neueste zuerst";
  grid.innerHTML=items.map(d=>{
    const fresh=d.bucket==="2026";
    return `
    <div class="card">
      <div class="badges">
        <span class="badge topic">${escapeHtml(d.topic)}</span>
        <span class="badge pod">${escapeHtml(d.pod)}</span>
        <span class="badge date${fresh?" is2026":""}">${escapeHtml(d.date)}</span>
      </div>
      <h3>${highlight(d.title,q)}</h3>
      <p>${highlight(d.insight,q)}</p>
      <div class="src">
        <span class="who">${highlight(d.source,q)}</span>
        <a href="${encodeURI(d.url)}" target="_blank" rel="noopener">Quelle ansehen &rarr;</a>
      </div>
    </div>`;}).join("");
  emptyEl.style.display=items.length?"none":"block";
}
btn.addEventListener("click",doSearch);
clearBtn.addEventListener("click",()=>{ searchEl.value=""; query=""; render(); searchEl.focus(); });
searchEl.addEventListener("keydown",e=>{ if(e.key==="Enter"){ doSearch(); }});
searchEl.addEventListener("input",doSearch);
render();
"""
JS=JS.replace("__TOPICS__",TOPICS_JSON).replace("__PERIODS__",PERIODS_JSON)

n2026=bcnt.get("2026",0)
html = f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Podcast-Wissensbibliothek — Insights mit Quellen</title>
<style>{CSS}</style>
</head>
<body>
<header>
  <div class="kicker">Learnings &amp; Insights aus den großen Podcasts</div>
  <h1>Podcast-Wissensbibliothek</h1>
  <p>{len(clean)} kuratierte Erkenntnisse &mdash; davon {n2026} aus 2026 &mdash; aus Diary of a CEO, Lex Fridman, Dwarkesh, Huberman Lab, Modern Wisdom, My First Million, ZOE, OMR, Doppelgänger, Finanzfluss &amp; vielen mehr. Standardmäßig <strong>neueste zuerst</strong>. Such z.&nbsp;B. <strong>AI</strong>, <strong>Schlaf</strong> oder <strong>Geld</strong> &mdash; jede Karte verlinkt zur Quelle.</p>
</header>
<nav class="topnav">
  <a class="navbtn active" href="podcast-learnings.html">🎧 Wissensbibliothek</a>
  <a class="navbtn" href="checkliste.html">✅ Lebensqualität-Checkliste</a>
  <a class="navbtn" href="diary-of-a-ceo.html">📔 Diary of a CEO</a>
</nav>
<div class="controls">
  <div class="searchrow">
    <input id="search" type="text" placeholder="Suche nach Thema, Gast oder Stichwort… (z. B. AI, Künstliche Intelligenz, Anthropic, Dopamin)" autocomplete="off">
    <button id="searchBtn">Suchen</button>
    <button id="clearBtn">Zurücksetzen</button>
  </div>
  <div class="filterlabel">Zeitraum</div>
  <div class="filters" id="periodfilters"></div>
  <div class="filterlabel">Thema</div>
  <div class="filters" id="topicfilters"></div>
</div>
<div class="count" id="count"></div>
<div class="grid" id="grid"></div>
<div class="empty" id="empty" style="display:none">Keine Treffer. Versuch ein anderes Stichwort, Thema oder einen anderen Zeitraum.</div>
<footer>
  {len(clean)} Insights aus öffentlich verfügbaren Podcast-Folgen, Show-Notes und Interviews &mdash; kuratierte Kurzfassungen mit Link zur Originalquelle. „Zeitlos / Klassiker" bündelt zeitlose Frameworks &amp; Grundlagen (z.&nbsp;B. Schlaf, Gewohnheiten, FATE). Ältere reine Tagesnews wurden bewusst entfernt.
  &nbsp;·&nbsp; <a href="diary-of-a-ceo.html">Reine Diary-of-a-CEO-Seite →</a>
</footer>
<script>
const DATA = {DATA_JSON};
{JS}
</script>
</body>
</html>
"""
open(os.path.join(HERE,'podcast-learnings.html'),'w',encoding='utf-8').write(html)
print('Built bytes:', len(html))
