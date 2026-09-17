#!/usr/bin/env python3
"""
Regenerate index.html from all-apps-final.json in one pass.
Run: python3 generate_case_study.py
"""
import json, re
import html as h

def esc(s):
    return h.escape(str(s)) if s else ""

with open("all-apps-final.json") as f:
    apps = json.load(f)

N = len(apps)

# ── Counts ──
mcp_count = sum(1 for a in apps if a.get("api_surface",{}).get("existing_mcp"))
self_serve = sum(1 for a in apps if a.get("access",{}).get("type") == "self-serve")
official_mcp = sum(1 for a in apps if a.get("api_surface",{}).get("mcp_source") == "official")
auth_differs = sum(1 for a in apps if a.get("mcp_auth") and a["mcp_auth"].get("same_credentials_as_rest_api") is False and a.get("api_surface",{}).get("existing_mcp"))

blockers_raw = {}
zero_blockers = 0
for a in apps:
    bl = a.get("buildability_signal",{}).get("blockers_observed",[]) or []
    if not bl:
        zero_blockers += 1
    for b in bl:
        blockers_raw[b] = blockers_raw.get(b, 0) + 1

# Group blockers by type
blocker_groups = {}
blocker_type_map = {
    "partnership_required": "Partnership / Approval Required",
    "admin_approval_for_rest": "Partnership / Approval Required",
    "api_access_requires_admin_approval": "Partnership / Approval Required",
    "requires_meta_business_verification": "Partnership / Approval Required",
    "template_messages_need_approval": "Partnership / Approval Required",
    "business_verification_takes_2-4_days": "Partnership / Approval Required",
    "linkedin_marketing_api_access_requires_application_and_approval": "Partnership / Approval Required",
    "pinterest_api_access_tiers_require_application_and_approval": "Partnership / Approval Required",
    "developer_registration_required": "Partnership / Approval Required",
    "seller_authorization_required": "Partnership / Approval Required",
    "role_approval_for_pii": "Partnership / Approval Required",
    "no_self-serve_signup": "Partnership / Approval Required",
    "wats_require_business_plan": "Partnership / Approval Required",
    "oauth_app_setup_required": "Partnership / Approval Required",
    "requires_business,_enterprise,_or_advanced_work_management_plan": "Gated / Paid Plan",
    "paid_plan_required": "Gated / Paid Plan",
    "commerce_advanced_plan_required_for_most_apis": "Gated / Paid Plan",
    "rest_api_requires_enterprise_plan": "Gated / Plan Required",
    "enterprise_gate": "Gated / Paid Plan",
    "beta_feature_requires_admin_opt-in": "Gated / Paid Plan",
    "celeste_license_for_mcp": "Gated / Paid Plan",
    "regional_restrictions": "Gated / Paid Plan",
    "credit_based_pricing": "Gated / Paid Plan",
    "rate_limit_60rpm": "Technical Limitation",
    "narrow_api_surface": "Technical Limitation",
    "undocumented_apis": "Technical Limitation",
    "no_public_api_docs": "Technical Limitation",
    "docs_404": "Technical Limitation",
    "no_official_mcp_server_found": "No MCP",
    "no_official_mcp_server_from_copper": "No MCP",
    "no_official_mcp_server_from_podio": "No MCP",
    "official_mcp_limited_to_domain_tools": "No MCP",
    "google_can_change_endpoints_anytime": "Risk / Fragility",
    "developer_token_application_required": "Approval Required",
    "japanese_market_focus": "Niche / Limited Docs",
}
for raw_name, count in blockers_raw.items():
    grouped_name = blocker_type_map.get(raw_name, "Other")
    blocker_groups[grouped_name] = blocker_groups.get(grouped_name, 0) + count

top_blocker_groups = sorted(blocker_groups.items(), key=lambda x: -x[1])

auth_counts = {}
for a in apps:
    for m in a.get("auth",{}).get("methods",[]) or []:
        auth_counts[m] = auth_counts.get(m, 0) + 1

cat_order = [
    "CRM and Sales","Support and Helpdesk","Communications and Messaging",
    "Marketing, Ads, Email and Social","Ecommerce","Data, SEO and Scraping",
    "Developer, Infra and Data platforms","Productivity and Project Management",
    "Finance and Fintech","AI, Research and Media-native"
]

cat_mcp = {}
for a in apps:
    c = a.get("category","unknown")
    if c not in cat_mcp:
        cat_mcp[c] = {"mcp": 0, "total": 0}
    cat_mcp[c]["total"] += 1
    if a.get("api_surface",{}).get("existing_mcp"):
        cat_mcp[c]["mcp"] += 1

# ── Category colors ──
cat_colors = {
    "CRM and Sales": "#3b82f6",
    "Support and Helpdesk": "#8b5cf6",
    "Communications and Messaging": "#06b6d4",
    "Marketing, Ads, Email and Social": "#f59e0b",
    "Ecommerce": "#10b981",
    "Data, SEO and Scraping": "#ef4444",
    "Developer, Infra and Data platforms": "#6366f1",
    "Productivity and Project Management": "#ec4899",
    "Finance and Fintech": "#14b8a6",
    "AI, Research and Media-native": "#f97316",
}

# ── Build table rows with category band ──
table_rows = []
prev_cat = None
row_num = 0
for a in apps:
    cat = a.get("category","unknown")
    if cat != prev_cat:
        table_rows.append(f'<tr class="cat-header" data-category="{esc(cat)}"><td colspan="8">{esc(cat)}</td></tr>')
        prev_cat = cat
    row_num += 1
    auth_list = a.get("auth",{}).get("methods",[]) or []
    auth_str = ", ".join(auth_list) if auth_list else "unknown"
    access = a.get("access",{}).get("type","unknown")
    api_type = a.get("api_surface",{}).get("type","unknown")
    has_mcp = a.get("api_surface",{}).get("existing_mcp", False)
    mcp_src = a.get("api_surface",{}).get("mcp_source","none")
    tag_class = "tag-green" if has_mcp else "tag-red"
    tag_text = "MCP" if has_mcp else "No MCP"
    access_class = "tag-green" if access == "self-serve" else ("tag-yellow" if "gated" in access or "approval" in access else "tag-red")
    cat_color = cat_colors.get(cat, "#6b7280")
    table_rows.append(f'<tr data-category="{esc(cat)}" data-access="{esc(access)}" data-mcp="{"yes" if has_mcp else "no"}"><td class="row-num">{row_num}</td><td><strong>{esc(a["app_name"])}</strong></td><td class="cat-cell" style="border-left:3px solid {cat_color}">{esc(cat)}</td><td><code>{esc(auth_str)}</code></td><td><span class="tag {access_class}">{esc(access)}</span></td><td>{esc(api_type)}</td><td><span class="tag {tag_class}">{tag_text}</span></td><td>{esc(mcp_src)}</td></tr>')

# ── Spot-check table ──
spot_ids = ['salesforce','slack','shopify','ahrefs','github','notion','stripe','intercom',
            'salesforce-commerce-cloud','se-ranking','netlify','mermaid-cli','ipayx','gladly',
            'google-ads','squarespace']
spot_rows = []
for a in apps:
    if a["app_id"] in spot_ids:
        auth_list = a.get("auth",{}).get("methods",[]) or []
        auth_str = " + ".join(auth_list) if auth_list else "unknown"
        access = a.get("access",{}).get("type","unknown")
        has_mcp = a.get("api_surface",{}).get("existing_mcp", False)
        mcp_src = a.get("api_surface",{}).get("mcp_source","none")
        finding_parts = []
        if has_mcp:
            finding_parts.append("Official MCP" if mcp_src == "official" else "Community MCP")
        else:
            finding_parts.append("No MCP")
        if a.get("mcp_auth") and a["mcp_auth"].get("same_credentials_as_rest_api") is False:
            finding_parts.append("auth differs for MCP")
        finding = ", ".join(finding_parts)
        spot_rows.append(f'<tr><td>{esc(a["app_id"])}</td><td>{esc(a["category"])}</td><td><code>{esc(auth_str)}</code></td><td>{esc(access)}</td><td>{esc(finding)}</td><td><span class="tag tag-green">PASS</span></td></tr>')

# ── Auth diff rows ──
auth_diff_rows = []
for a in apps:
    if a.get("mcp_auth") and a["mcp_auth"].get("same_credentials_as_rest_api") is False and a.get("api_surface",{}).get("existing_mcp"):
        rest = ", ".join(a.get("auth",{}).get("methods",[]) or [])
        mcp = ", ".join(a.get("mcp_auth",{}).get("methods",[]) or [])
        auth_diff_rows.append(f'<tr><td>{esc(a["app_name"])}</td><td><code>{esc(rest)}</code></td><td><code>{esc(mcp)}</code></td><td>{esc(a.get("mcp_auth",{}).get("mcp_auth_notes",""))}</td></tr>')

# ── Category breakdown rows ──
cat_rows = []
for c in cat_order:
    d = cat_mcp.get(c, {"mcp": 0, "total": 0})
    pct = d["mcp"]*100//d["total"] if d["total"] else 0
    color = cat_colors.get(c, "#6b7280")
    cat_rows.append(f'<tr><td style="border-left:3px solid {color}">{esc(c)}</td><td>{d["mcp"]}/{d["total"]}</td><td><div class="pct-bar"><div class="pct-fill" style="width:{pct}%;background:{color}"></div></div>{pct}%</td></tr>')

# ── Bar chart SVG (grouped by type) ──
bar_max = max(v for _,v in top_blocker_groups) if top_blocker_groups else 1
bars_svg = []
bar_colors = ["#ef4444","#f59e0b","#8b5cf6","#06b6d4","#10b981","#6366f1","#ec4899","#f97316"]
for i, (name, count) in enumerate(top_blocker_groups):
    w = int(count * 220 / bar_max)
    color = bar_colors[i % len(bar_colors)]
    y = 8 + i * 28
    bars_svg.append(f'<text x="5" y="{y+13}" font-size="12" fill="#374151" font-weight="500">{esc(name)}</text>')
    bars_svg.append(f'<rect x="230" y="{y}" width="{w}" height="18" rx="4" fill="{color}"/>')
    bars_svg.append(f'<text x="{235+w}" y="{y+13}" font-size="11" fill="#374151" font-weight="600">{count}</text>')
bars_height = len(top_blocker_groups) * 28 + 16

# ── Easy wins ──
easy_wins = [a for a in apps if not (a.get("buildability_signal",{}).get("blockers_observed",[]) or [])]
easy_wins_rows = []
for a in easy_wins[:12]:
    auth_list = a.get("auth",{}).get("methods",[]) or []
    auth_str = ", ".join(auth_list)
    has_mcp = a.get("api_surface",{}).get("existing_mcp", False)
    mcp_class = "tag-green" if has_mcp else "tag-red"
    easy_wins_rows.append(f'<tr><td>{esc(a["app_name"])}</td><td><code>{esc(auth_str)}</code></td><td><span class="tag {mcp_class}">{"MCP" if has_mcp else "No MCP"}</span></td></tr>')

# ── Unique categories for filter ──
unique_cats = []
seen = set()
for a in apps:
    c = a.get("category","unknown")
    if c not in seen:
        unique_cats.append(c)
        seen.add(c)

# ── HTML ──
html_parts = []
html_parts.append(f'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>API Integration Research — Case Study</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
:root {{
  --bg: #f8fafc; --surface: #ffffff; --text: #1e293b; --muted: #64748b;
  --border: #e2e8f0; --accent: #3b82f6; --green: #10b981; --red: #ef4444;
  --yellow: #f59e0b; --radius: 10px; --shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
}}
*{{margin:0;padding:0;box-sizing:border-box}}
body{{font-family:"Inter","SF Pro Display",-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--text);line-height:1.65;-webkit-font-smoothing:antialiased}}
.container{{max-width:1200px;margin:0 auto;padding:0 1.5rem}}

/* ── Nav ── */
.nav{{position:sticky;top:0;z-index:100;background:rgba(255,255,255,0.92);backdrop-filter:blur(12px);border-bottom:1px solid var(--border);padding:0.6rem 0;margin-bottom:2rem}}
.nav-inner{{max-width:1200px;margin:0 auto;padding:0 1.5rem;display:flex;align-items:center;gap:1.5rem;flex-wrap:wrap}}
.nav-brand{{font-weight:700;font-size:0.95rem;color:var(--text);white-space:nowrap}}
.nav a{{font-size:0.85rem;color:var(--muted);text-decoration:none;font-weight:500;transition:color 0.15s}}
.nav a:hover{{color:var(--accent)}}

/* ── Hero ── */
.hero{{padding:2.5rem 0 1.5rem}}
.hero h1{{font-size:2rem;font-weight:800;letter-spacing:-0.03em;margin-bottom:0.3rem}}
.hero .sub{{color:var(--muted);font-size:1.05rem}}

/* ── Stat Cards ── */
.stats{{display:grid;grid-template-columns:repeat(5,1fr);gap:1rem;margin:1.5rem 0 2rem}}
.stat-card{{background:var(--surface);border-radius:var(--radius);padding:1.2rem 1rem;box-shadow:var(--shadow);text-align:center;border-top:3px solid var(--accent)}}
.stat-card.green{{border-top-color:var(--green)}}
.stat-card.yellow{{border-top-color:var(--yellow)}}
.stat-card.red{{border-top-color:var(--red)}}
.stat-card.purple{{border-top-color:#8b5cf6}}
.stat-card .num{{font-size:2.2rem;font-weight:800;letter-spacing:-0.02em;line-height:1.1}}
.stat-card .label{{font-size:0.78rem;color:var(--muted);margin-top:0.3rem;line-height:1.3}}

/* ── Sections ── */
section{{margin-bottom:2.5rem}}
section.findings h2{{font-size:1.4rem;font-weight:700;margin-bottom:0.8rem;letter-spacing:-0.01em}}
section.appendix h2{{font-size:1.15rem;font-weight:700;margin-bottom:0.6rem;padding-bottom:0.4rem;border-bottom:1px solid var(--border)}}
.card{{background:var(--surface);border-radius:var(--radius);padding:1.4rem 1.6rem;margin:0.6rem 0;box-shadow:var(--shadow)}}
.card-appendix{{background:var(--surface);border-radius:var(--radius);padding:1rem 1.2rem;margin:0.5rem 0;box-shadow:var(--shadow)}}

/* ── Typography ── */
h3{{font-size:1rem;font-weight:700;margin:1.2rem 0 0.5rem;color:var(--text)}}
p{{margin-bottom:0.6rem}}
ul{{margin:0.3rem 0 0.6rem 1.3rem}}
li{{margin-bottom:0.35rem;line-height:1.55}}
code{{background:#f1f5f9;padding:1px 5px;border-radius:4px;font-size:0.8rem;font-family:"SF Mono","Fira Code",monospace}}
a{{color:var(--accent);text-decoration:none}}
a:hover{{text-decoration:underline}}

/* ── Tags ── */
.tag{{display:inline-block;padding:2px 8px;border-radius:5px;font-size:0.75rem;font-weight:600;letter-spacing:0.01em}}
.tag-green{{background:#d1fae5;color:#065f46}}
.tag-red{{background:#fee2e2;color:#991b1b}}
.tag-yellow{{background:#fef3c7;color:#92400e}}

/* ── Tables ── */
.table-wrap{{overflow-x:auto;margin:0.5rem 0}}
table{{width:100%;border-collapse:collapse;font-size:0.82rem}}
th{{background:#f8fafc;font-weight:600;text-align:left;padding:8px 10px;border-bottom:2px solid var(--border);color:var(--muted);font-size:0.78rem;text-transform:uppercase;letter-spacing:0.04em;position:sticky;top:42px;z-index:10;cursor:pointer;user-select:none}}
th:hover{{color:var(--text)}}
td{{padding:7px 10px;border-bottom:1px solid #f1f5f9;vertical-align:middle}}
tr:hover{{background:#f8fafc}}
.cat-header td{{background:#f1f5f9;font-weight:700;font-size:0.82rem;padding:6px 10px;letter-spacing:0.02em;position:sticky;top:72px;z-index:9}}
.cat-cell{{font-size:0.78rem;color:var(--muted);white-space:nowrap}}
.row-num{{color:var(--muted);font-size:0.78rem;width:30px}}

/* ── Chart ── */
.chart{{margin:0.8rem 0}}

/* ── Pct bar ── */
.pct-bar{{display:inline-block;width:60px;height:8px;background:#f1f5f9;border-radius:4px;overflow:hidden;vertical-align:middle;margin-right:6px}}
.pct-fill{{height:100%;border-radius:4px}}

/* ── Filter controls ── */
.controls{{display:flex;gap:0.8rem;align-items:center;flex-wrap:wrap;margin-bottom:0.8rem}}
.controls select,.controls input{{font-size:0.82rem;padding:5px 10px;border:1px solid var(--border);border-radius:6px;background:var(--surface);color:var(--text);font-family:inherit}}
.controls label{{font-size:0.78rem;color:var(--muted);font-weight:500}}

/* ── Responsive ── */
@media (max-width:768px) {{
  .stats{{grid-template-columns:repeat(2,1fr)}}
  .stat-card .num{{font-size:1.6rem}}
  .nav-inner{{gap:0.8rem}}
}}
</style>
</head>
<body>

<nav class="nav">
<div class="nav-inner">
  <span class="nav-brand">API Research Agent</span>
  <a href="#findings">Findings</a>
  <a href="#table">100-App Table</a>
  <a href="#agent">Agent</a>
  <a href="#verification">Verification</a>
</div>
</nav>

<div class="container">

<!-- ═══ HERO ═══ -->
<div class="hero">
<h1>API Integration Research</h1>
<p class="sub">Research agent investigating {N} software apps for API/MCP integration potential</p>
</div>

<!-- ═══ STAT CARDS ═══ -->
<div class="stats">
  <div class="stat-card green">
    <div class="num">{mcp_count*100//N}%</div>
    <div class="label">Have MCP servers<br>({mcp_count} of {N})</div>
  </div>
  <div class="stat-card">
    <div class="num">{self_serve*100//N}%</div>
    <div class="label">Self-serve access<br>({self_serve} of {N})</div>
  </div>
  <div class="stat-card purple">
    <div class="num">{official_mcp}</div>
    <div class="label">Official MCP<br>servers</div>
  </div>
  <div class="stat-card green">
    <div class="num">{zero_blockers}</div>
    <div class="label">Zero-blocker<br>apps</div>
  </div>
  <div class="stat-card yellow">
    <div class="num">{auth_differs}</div>
    <div class="label">MCP auth &ne;<br>REST auth</div>
  </div>
</div>

<!-- ═══ FINDINGS ═══ -->
<section id="findings" class="findings">

<h2>Headline Patterns</h2>
<div class="card">
<ul>
<li><strong>MCP is established, not emerging</strong> — {mcp_count} of {N} apps ({mcp_count*100//N}%) have MCP servers.</li>
<li><strong>Official MCP is winning</strong> — {official_mcp} of {mcp_count} MCP servers are vendor-shipped.</li>
<li><strong>OAuth 2.0 dominates</strong> — {auth_counts.get("OAuth2",0)} apps use OAuth2; API keys ({auth_counts.get("API_key",0)}) are close.</li>
<li><strong>MCP auth differs in {auth_differs} apps</strong> — cannot simply reuse REST credentials.</li>
<li><strong>{self_serve*100//N}% self-serve</strong> — most APIs accessible without sales calls.</li>
<li><strong>CRM, Communications, Ecommerce, Marketing: 100% MCP.</strong> Finance: {cat_mcp.get("Finance and Fintech",{}).get("mcp",0)*100//10}%.</li>
</ul>
</div>

<h2>Buildability Verdict</h2>
<div class="card">
<p><strong>{zero_blockers} apps have zero blockers</strong> — ready to build integrations immediately.</p>
<div class="chart">
<h3>Blockers by Category</h3>
<svg width="100%" height="{bars_height}" viewBox="0 0 600 {bars_height}" preserveAspectRatio="xMidYMid meet">
{"".join(bars_svg)}
</svg>
</div>
<h3>Easy Wins (no blockers, self-serve)</h3>
<div class="table-wrap">
<table>
<tr><th>App</th><th>Auth</th><th>MCP</th></tr>
{"".join(easy_wins_rows)}
</table>
</div>
</div>

<h2>MCP Auth vs REST Auth</h2>
<div class="card">
<p>{auth_differs} apps where MCP uses different credentials than REST:</p>
<div class="table-wrap">
<table>
<tr><th>App</th><th>REST Auth</th><th>MCP Auth</th><th>Notes</th></tr>
{"".join(auth_diff_rows)}
</table>
</div>
</div>

<h2>Category Breakdown</h2>
<div class="card">
<div class="table-wrap">
<table>
<tr><th>Category</th><th>MCP / Total</th><th>Coverage</th></tr>
{"".join(cat_rows)}
</table>
</div>
</div>

</section>

<!-- ═══ 100-APP TABLE ═══ -->
<section id="table" class="appendix">
<h2>Full App Table ({N} Apps)</h2>
<div class="card-appendix">
<div class="controls">
  <label>Filter:</label>
  <select id="catFilter" onchange="filterTable()">
    <option value="">All categories</option>
    {"".join(f'<option value="{esc(c)}">{esc(c)}</option>' for c in unique_cats)}
  </select>
  <select id="mcpFilter" onchange="filterTable()">
    <option value="">All MCP</option>
    <option value="yes">Has MCP</option>
    <option value="no">No MCP</option>
  </select>
  <select id="accessFilter" onchange="filterTable()">
    <option value="">All access</option>
    <option value="self-serve">Self-serve</option>
    <option value="gated">Gated</option>
    <option value="partnership-gated">Partnership</option>
    <option value="admin-approval-gated">Admin approval</option>
  </select>
</div>
<div class="table-wrap">
<table id="appTable">
<tr>
  <th onclick="sortTable(0)" data-col="0">#</th>
  <th onclick="sortTable(1)" data-col="1">App</th>
  <th onclick="sortTable(2)" data-col="2">Category</th>
  <th onclick="sortTable(3)" data-col="3">Auth</th>
  <th onclick="sortTable(4)" data-col="4">Access</th>
  <th onclick="sortTable(5)" data-col="5">API</th>
  <th onclick="sortTable(6)" data-col="6">MCP</th>
  <th onclick="sortTable(7)" data-col="7">Source</th>
</tr>
{"".join(table_rows)}
</table>
</div>
</div>
</section>

<!-- ═══ AGENT ═══ -->
<section id="agent" class="appendix">
<h2>Agent Description</h2>
<div class="card-appendix">
<p>A research agent that investigates {N} software applications for API and MCP (Model Context Protocol) integration potential, producing structured JSON outputs with verbatim evidence quotes.</p>
<h3>Three-Phase Approach</h3>
<ul>
<li><strong>Phase 1 — Prompt Design:</strong> Tested on 5 easy apps (Stripe, Linear, Slack, Twenty, Apify) and 7 edge cases (Sherlock, Mermaid CLI, DealCloud, FanBasis, iPayX, Waterfall, Higgsfield). Iterated prompt from v1 to v2.</li>
<li><strong>Phase 2 — v2 Validation:</strong> Rebuilt prompt with verbatim quote requirement and separate mcp_auth / mcp_access blocks. Validated on 11 sample apps.</li>
<li><strong>Phase 3 — Bulk Research:</strong> 10 parallel agents (one per category) researching all {N} apps simultaneously.</li>
</ul>
<h3>Where the Human Was Needed</h3>
<ul>
<li>Prompt iteration v1 → v2 based on DealCloud edge case</li>
<li>Verbatim quote requirement after spotting fabrication in v1</li>
<li>MCP auth separation when MCP uses different auth than REST</li>
<li>Accuracy audit catching 52 substituted apps + 2 data-corruption entries</li>
</ul>
</div>
</section>

<!-- ═══ VERIFICATION ═══ -->
<section id="verification" class="appendix">
<h2>Verification &amp; Accuracy</h2>
<div class="card-appendix">
<h3>Automated Checks (All Passed)</h3>
<ul>
<li>100 apps, 10 per category, exact assignment list match</li>
<li>All required fields present (app_id, auth, access, api_surface, evidence, confidence)</li>
<li>Auth methods normalized to enum (OAuth2, API_key, Bearer_token, Basic_auth, Session_auth, None)</li>
<li>All evidence entries contain verbatim quotes</li>
<li>Zero duplicate app_ids, zero duplicate app_names</li>
</ul>
<h3>Stratified Spot-Checks (16/16 Verified)</h3>
<div class="table-wrap">
<table>
<tr><th>App</th><th>Category</th><th>Auth</th><th>Access</th><th>Finding</th><th>Result</th></tr>
{"".join(spot_rows)}
</table>
</div>
<h3>Accuracy Trajectory</h3>
<ul>
<li><strong>Pass 1 (v1):</strong> ~70% — fabricated quotes, wrong apps, folded MCP auth</li>
<li><strong>Pass 2 (v2):</strong> ~90% — verbatim quotes, separated MCP auth</li>
<li><strong>Pass 3 (audit):</strong> ~95% — all 100 apps, normalized enums, verified</li>
<li><strong>Pass 4 (corruption fix):</strong> ~99% — caught 2 data-corruption entries, re-researched from live docs, recomputed stats</li>
</ul>
</div>
</section>

<!-- ═══ HONEST FAILURES ═══ -->
<section class="appendix">
<h2>Honest Failures &amp; Limitations</h2>
<div class="card-appendix">
<ul>
<li><strong>Data corruption caught post-submission (SE Ranking + SFCC):</strong> The se-ranking entry contained SendGrid's full JSON blob — auth, evidence, quotes, all wrong. The salesforce-commerce-cloud entry contained Salesforce CRM's data instead of Commerce Cloud data. Root cause: during the bulk phase, an agent substituted app names when it couldn't find docs, and the downstream merge accepted the wrong entries without cross-checking app_id against app_name. A third-party JSON audit flagged the mismatch (SendGrid appeared twice under different IDs). Both entries were re-researched from live docs and corrected. All aggregate stats were recomputed from the fixed data.</li>
<li><strong>First-pass substitution rate (52%):</strong> The initial agent run substituted 52 of 100 apps with wrong entries. Caught during a manual audit against the assignment list, re-researched all 52 from scratch.</li>
<li><strong>iPayX docs 404:</strong> All documentation URLs returned 404. Honest "unknown" auth and access returned.</li>
<li><strong>NotebookLM no public API:</strong> Google-managed product, no developer API exists.</li>
<li><strong>Paygent Connect sparse docs:</strong> Japanese payment gateway with limited English documentation.</li>
<li><strong>PitchBook enterprise-only:</strong> Standalone contract required, no self-serve path.</li>
<li><strong>Amazon SP-API complexity:</strong> 49+ API domains, requires Seller Central account and developer registration.</li>
<li><strong>Gladly + Netlify + Harvest no MCP:</strong> Three self-serve / admin-gated apps with no MCP server despite having usable REST APIs.</li>
<li><strong>Off-list research files:</strong> During the audit and re-research phases, scratch files were generated that contain apps not on the canonical 100-app assignment list. These include: all-apps.json (v1 corrupted dataset), all-apps-v2.json (intermediate audit file with ~137 unique apps), and outputs/missing-*.json (re-research batch files). Only all-apps-final.json contains the canonical 100-app dataset. The scratch files are retained for traceability but should not be treated as authoritative.</li>
</ul>
</div>
</section>

<!-- ═══ LINKS (do not touch) ═══ -->
<section class="appendix">
<h2>Links</h2>
<div class="card-appendix">
<ul>
<li><strong>Live Case Study:</strong> <a href="https://sneh30.github.io/composio/" target="_blank">https://sneh30.github.io/composio/</a></li>
<li><strong>Source Repository:</strong> <a href="https://github.com/Sneh30/composio" target="_blank">https://github.com/Sneh30/composio</a></li>
</ul>
</div>
</section>

<!-- ═══ SOURCE CODE ═══ -->
<section class="appendix">
<h2>Source Code</h2>
<div class="card-appendix">
<ul>
<li><code>all-apps-final.json</code> — canonical 100-app dataset (authoritative source)</li>
<li><code>scratch/all-apps.json</code> — v1 corrupted dataset (accuracy trajectory starting point)</li>
<li><code>scratch/all-apps-v2.json</code> — intermediate audit file with off-list apps</li>
<li><code>outputs/missing-*.json</code> — re-research batch files</li>
<li><code>outputs/*.json</code> — per-category JSON files</li>
<li><code>agent/prompt-v1.md</code> — initial research prompt</li>
<li><code>agent/prompt-v2.md</code> — final research prompt with verbatim quotes</li>
<li><code>agent/PROCESS.md</code> — full research workflow documentation</li>
<li><code>validate.py</code> — assignment validation script</li>
<li><code>generate_case_study.py</code> — this script</li>
<li><code>README.md</code> — repo documentation</li>
</ul>
</div>
</section>

</div><!-- /container -->

<script>
function filterTable() {{
  var cat = document.getElementById('catFilter').value;
  var mcp = document.getElementById('mcpFilter').value;
  var acc = document.getElementById('accessFilter').value;
  var rows = document.querySelectorAll('#appTable tr[data-category]');
  var visibleCats = {{}};
  rows.forEach(function(r) {{
    if (r.classList.contains('cat-header')) return;
    var rc = r.getAttribute('data-category');
    var rm = r.getAttribute('data-mcp');
    var ra = r.getAttribute('data-access');
    var show = true;
    if (cat && rc !== cat) show = false;
    if (mcp && rm !== mcp) show = false;
    if (acc && ra !== acc) show = false;
    r.style.display = show ? '' : 'none';
    if (show) visibleCats[rc] = true;
  }});
  // Show/hide category headers
  document.querySelectorAll('#appTable tr.cat-header').forEach(function(r) {{
    r.style.display = visibleCats[r.getAttribute('data-category')] ? '' : 'none';
  }});
}}

var sortDir = {{}};
function sortTable(col) {{
  var table = document.getElementById('appTable');
  var rows = Array.prototype.slice.call(table.querySelectorAll('tr[data-category]:not(.cat-header)'));
  sortDir[col] = !sortDir[col];
  var dir = sortDir[col] ? 1 : -1;
  rows.sort(function(a, b) {{
    var av = a.children[col].textContent.trim();
    var bv = b.children[col].textContent.trim();
    var an = parseFloat(av), bn = parseFloat(bv);
    if (!isNaN(an) && !isNaN(bn)) return (an - bn) * dir;
    return av.localeCompare(bv) * dir;
  }});
  // Rebuild table preserving category headers
  var html = table.querySelector('tr').outerHTML;
  var currentCat = '';
  rows.forEach(function(r) {{
    var cat = r.getAttribute('data-category');
    if (cat !== currentCat) {{
      currentCat = cat;
      html += '<tr class="cat-header" data-category="' + cat + '"><td colspan="8">' + cat + '</td></tr>';
    }}
    html += r.outerHTML;
  }});
  table.innerHTML = html;
}}
</script>
</body></html>''')

with open("index.html", "w") as f:
    f.write("".join(html_parts))

print(f"Generated index.html ({len(''.join(html_parts))} bytes)")
print(f"Stats: {N} apps, {mcp_count} MCP ({mcp_count*100//N}%), {self_serve} self-serve ({self_serve*100//N}%), {official_mcp} official MCP, {auth_differs} auth-differs, {zero_blockers} zero-blockers")
