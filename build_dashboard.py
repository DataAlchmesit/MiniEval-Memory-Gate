import json
from collections import defaultdict

entries = []
with open("gate_audit_log.json") as f:
    for line in f:
        line = line.strip()
        if line:
            entries.append(json.loads(line))

try:
    with open("adjudication_log.json") as af:
        adjudications = json.load(af)
except:
    adjudications = []

adj_cards = ""
for a in adjudications:
    vclass = "adj-accept" if a["verdict"] == "ACCEPT" else ("adj-block" if a["verdict"] == "BLOCK" else "adj-review")
    adj_cards += f'''
    <div class="adj-card">
      <div class="adj-verdict {vclass}">{a["verdict"]}</div>
      <div class="adj-mem">
        <div class="adj-label">EXISTING MEMORY</div>
        <div class="adj-old">{a["old_fact"]} <span class="adj-score">{a["old_score"]}</span></div>
      </div>
      <div class="adj-arrow">vs</div>
      <div class="adj-mem">
        <div class="adj-label">INCOMING MEMORY</div>
        <div class="adj-new">{a["new_fact"]} <span class="adj-score">{a["new_score"]}</span></div>
      </div>
      <div class="adj-reason">{a["reason"]}</div>
    </div>'''


stored = [e for e in entries if e["decision"] == "STORE"]
blocked = [e for e in entries if e["decision"] == "REJECT"]
review = [e for e in entries if e["decision"] == "REVIEW"]
total = len(entries)
halluc_total = len([e for e in entries if e.get("kind") == "hallucination"])
halluc_caught = len([e for e in entries if e.get("kind") == "hallucination" and e["decision"] == "REJECT"])
catch_rate = round(100 * halluc_caught / halluc_total, 1) if halluc_total else 0

cat_stats = defaultdict(lambda: {"halluc": 0, "caught": 0})
for e in entries:
    if e.get("kind") == "hallucination":
        c = e.get("category", "other")
        cat_stats[c]["halluc"] += 1
        if e["decision"] == "REJECT":
            cat_stats[c]["caught"] += 1

pastels = ["#A7C7E7", "#C3B1E1", "#B5EAD7", "#FFDAC1", "#FFB7B2", "#E2C2FF", "#B2E2E2", "#FDCB9E"]
cat_labels, cat_rates, cat_colors = [], [], []
i = 0
for cat, s in sorted(cat_stats.items(), key=lambda x: -x[1]["halluc"]):
    rate = round(100 * s["caught"] / s["halluc"], 0) if s["halluc"] else 0
    cat_labels.append(cat)
    cat_rates.append(rate)
    cat_colors.append(pastels[i % len(pastels)])
    i += 1

cat_rows = ""
for idx, cat in enumerate(cat_labels):
    cat_rows += f"""
    <div class="crow">
      <div class="cat-name">{cat}</div>
      <div class="cat-bar-wrap"><div class="cat-bar" style="width:{cat_rates[idx]}%;background:{cat_colors[idx]}"></div></div>
      <div class="cat-pct">{int(cat_rates[idx])}%</div>
    </div>"""

faith_scores = [e["faith"] for e in entries]
labels_json = json.dumps(list(range(1, len(faith_scores) + 1)))
scores_json = json.dumps(faith_scores)
cat_labels_json = json.dumps(cat_labels)
cat_rates_json = json.dumps(cat_rates)
cat_colors_json = json.dumps(cat_colors)

def audit_rows(items, badge_class, badge_text):
    rows = ""
    for e in items:
        rows += f"""
      <tr>
        <td><span class="badge {badge_class}">{badge_text}</span></td>
        <td class="cat">{e.get('category','')}</td>
        <td class="factcol">{e['fact']}</td>
        <td class="srccol">{e['source']}</td>
        <td class="scorecol">{e['faith']:.2f}</td>
        <td class="lblcol">{e.get('label','')}</td>
      </tr>"""
    return rows

all_audit = audit_rows(blocked, "b-blocked", "BLOCKED") + audit_rows(review, "b-review", "REVIEW") + audit_rows(stored, "b-stored", "STORED")

csv_lines = ["decision,category,kind,faith,fact,source"]
for e in entries:
    fact = e['fact'].replace('"', "'")
    source = e['source'].replace('"', "'")
    csv_lines.append(f'{e["decision"]},{e.get("category","")},{e.get("kind","")},{e["faith"]},"{fact}","{source}"')
csv_data = "\\n".join(csv_lines).replace("`", "'")

html = f"""<!DOCTYPE html>
<html><head><meta charset="utf-8"><title>MiniEval Memory Gate</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{ font-family:-apple-system,Segoe UI,Roboto,sans-serif; background:#f4f6fa; color:#1a2233; padding:36px; }}
.header {{ display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:28px; }}
.header h1 {{ font-size:26px; font-weight:600; margin-bottom:6px; color:#1a2233; }}
.header p {{ color:#6b7280; font-size:14px; }}
.export-btn {{ background:#7c6ee6; color:#fff; border:none; padding:10px 18px; border-radius:8px; font-size:14px; cursor:pointer; font-weight:500; }}
.export-btn:hover {{ background:#6a5bd0; }}
.stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:16px; margin-bottom:24px; }}
.card {{ background:#fff; border:1px solid #e5e9f0; border-radius:12px; padding:22px; }}
.card .label {{ color:#6b7280; font-size:13px; margin-bottom:8px; }}
.card .value {{ font-size:34px; font-weight:700; }}
.value.blue {{ color:#5b8def; }} .value.green {{ color:#4caf82; }}
.value.purple {{ color:#7c6ee6; }} .value.amber {{ color:#e0a04d; }}
.grid2 {{ display:grid; grid-template-columns:1fr 1fr; gap:20px; margin-bottom:24px; }}
.section {{ background:#fff; border:1px solid #e5e9f0; border-radius:12px; padding:22px; margin-bottom:24px; }}
.section h2 {{ font-size:16px; margin-bottom:18px; font-weight:600; color:#1a2233; }}
.chartbox {{ height:220px; }}
.crow {{ display:flex; align-items:center; gap:14px; padding:8px 0; }}
.cat-name {{ width:110px; font-size:14px; text-transform:capitalize; color:#374151; }}
.cat-bar-wrap {{ flex:1; background:#eef1f6; border-radius:6px; height:20px; overflow:hidden; }}
.cat-bar {{ height:100%; border-radius:6px; }}
.cat-pct {{ width:50px; text-align:right; font-size:14px; font-family:monospace; color:#6b7280; }}
table {{ width:100%; border-collapse:collapse; }}
th {{ text-align:left; font-size:12px; color:#6b7280; text-transform:uppercase; letter-spacing:0.5px; padding:10px 12px; border-bottom:2px solid #e5e9f0; }}
td {{ padding:11px 12px; font-size:13px; border-bottom:1px solid #f0f2f6; vertical-align:top; }}
.badge {{ font-size:11px; font-weight:700; padding:4px 10px; border-radius:6px; display:inline-block; }}
.b-blocked {{ background:#efe9fc; color:#7c6ee6; }}
.b-stored {{ background:#e6f4ee; color:#4caf82; }}
.b-review {{ background:#fdf3e2; color:#e0a04d; }}
.cat {{ color:#8b93a3; }}
.factcol {{ font-weight:500; }}
.srccol {{ color:#8b93a3; max-width:280px; }}
.scorecol {{ font-family:monospace; color:#6b7280; }}
.lblcol {{ color:#8b93a3; }}
.adj-panel {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.adj-card {{ border:1px solid #e5e9f0; border-radius:10px; padding:16px; display:flex; flex-direction:column; gap:10px; }}
.adj-verdict {{ font-size:12px; font-weight:700; padding:4px 12px; border-radius:6px; align-self:flex-start; }}
.adj-accept {{ background:#e6f4ee; color:#4caf82; }}
.adj-block {{ background:#efe9fc; color:#7c6ee6; }}
.adj-review {{ background:#fdf3e2; color:#e0a04d; }}
.adj-label {{ font-size:10px; color:#9ca3af; letter-spacing:0.5px; margin-bottom:3px; }}
.adj-old {{ font-size:13px; color:#8b93a3; }}
.adj-new {{ font-size:13px; font-weight:500; color:#1a2233; }}
.adj-score {{ font-family:monospace; color:#9ca3af; font-size:12px; }}
.adj-arrow {{ font-size:11px; color:#c0c6d0; text-align:center; }}
.adj-reason {{ font-size:12px; color:#6b7280; border-top:1px solid #f0f2f6; padding-top:8px; }}
.footer {{ text-align:center; color:#9ca3af; font-size:13px; margin-top:28px; }}
</style></head><body>
<div class="header">
  <div>
    <h1>MiniEval Memory Gate</h1>
    <p>Every fact checked for faithfulness before it enters your AI's memory. Built on Supermemory.</p>
  </div>
  <button class="export-btn" onclick="exportCSV()">Export CSV</button>
</div>
<div class="stats">
  <div class="card"><div class="label">Facts Processed</div><div class="value blue">{total}</div></div>
  <div class="card"><div class="label">Stored (Faithful)</div><div class="value green">{len(stored)}</div></div>
  <div class="card"><div class="label">Blocked (Hallucinations)</div><div class="value purple">{len(blocked)}</div></div>
  <div class="card"><div class="label">Catch Rate</div><div class="value amber">{catch_rate}%</div></div>
</div>
<div class="grid2">
  <div class="section"><h2>Faithfulness Score Distribution</h2><div class="chartbox"><canvas id="trendChart"></canvas></div></div>
  <div class="section"><h2>Catch Rate by Category</h2><div class="chartbox"><canvas id="catChart"></canvas></div></div>
</div>
<div class="section">
  <h2>Hallucination Catch Rate by Fact Type</h2>
  {cat_rows}
</div>
<div class="section">
  <h2>Contradiction Adjudication — protecting true memories from false overwrites</h2>
  <p style="font-size:13px;color:#6b7280;margin-bottom:16px;">Supermemory resolves memory conflicts by recency. MiniEval checks faithfulness first — so a hallucinated new memory can never overwrite a true one.</p>
  <div class="adj-panel">{adj_cards}</div>
</div>
<div class="section">
  <h2>Complete Audit Trail</h2>
  <table>
    <thead><tr><th>Decision</th><th>Category</th><th>Fact</th><th>Source Message</th><th>Faith</th><th>Verdict</th></tr></thead>
    <tbody>{all_audit}</tbody>
  </table>
</div>
<div class="footer">MiniEval Memory Gate · Powered by MiniEval Pro · Supermemory Hackathon 2026 · Built by Preeti Soni</div>
<script>
const csvData = `{csv_data}`;
function exportCSV() {{
  const blob = new Blob([csvData], {{type:'text/csv'}});
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url; a.download = 'minieval_memory_audit.csv'; a.click();
}}
new Chart(document.getElementById('trendChart'), {{
  type:'line',
  data:{{ labels:{labels_json}, datasets:[{{ label:'Faithfulness', data:{scores_json}, borderColor:'#7fb0f0', backgroundColor:'rgba(127,176,240,0.12)', fill:true, pointRadius:0, pointHoverRadius:5, borderWidth:2, tension:0.45 }}] }},
  options:{{ responsive:true, maintainAspectRatio:false, interaction:{{mode:'index',intersect:false}}, plugins:{{legend:{{labels:{{color:'#6b7280'}}}}}}, scales:{{ y:{{min:0,max:1,ticks:{{color:'#9ca3af'}},grid:{{color:'#eef1f6'}}}}, x:{{ticks:{{color:'#9ca3af',maxTicksLimit:12}},grid:{{display:false}}}} }} }}
}});
new Chart(document.getElementById('catChart'), {{
  type:'bar',
  data:{{ labels:{cat_labels_json}, datasets:[{{ label:'Catch Rate %', data:{cat_rates_json}, backgroundColor:{cat_colors_json}, borderRadius:6 }}] }},
  options:{{ responsive:true, maintainAspectRatio:false, plugins:{{legend:{{display:false}}}}, scales:{{ y:{{min:0,max:100,ticks:{{color:'#9ca3af'}},grid:{{color:'#eef1f6'}}}}, x:{{ticks:{{color:'#6b7280'}},grid:{{display:false}}}} }} }}
}});
</script>
</body></html>"""

with open("dashboard.html", "w") as f:
    f.write(html)

print("Dashboard rebuilt.")
print(f"  Total: {total} | Stored: {len(stored)} | Blocked: {len(blocked)} | Review: {len(review)} | Catch: {catch_rate}%")
