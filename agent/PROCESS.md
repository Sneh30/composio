# Research Process Documentation

## How the 100 Apps Were Researched

### Tool Used

The research was conducted using **opencode** (an interactive CLI coding agent
powered by Claude) in an interactive session — not a standalone orchestration
script. The agent operated within a persistent shell, running web searches,
fetching documentation pages, and writing structured JSON outputs.

### Three-Phase Approach

#### Phase 1: Prompt Design (v1)

- Tested the research prompt on 5 "easy" apps: Stripe, Linear, Slack, Twenty, Apify
- Tested on 7 edge cases: Sherlock, Mermaid CLI, DealCloud, FanBasis, iPayX,
  Waterfall, Higgsfield
- Identified failures: fabricated documentation URLs, MCP auth folded into
  REST auth, agents substituting apps when they couldn't find docs
- Iterated prompt from v1 to v2 based on these findings

#### Phase 2: v2 Validation

- Rebuilt the prompt with verbatim quote requirement and separate
  `mcp_auth` / `mcp_access` blocks
- Added `Session_auth` / `None` enum values
- Validated on 11 sample apps across multiple categories
- Confirmed v2 prompt produced accurate, verifiable output

#### Phase 3: Bulk Research (10 parallel agents)

- Launched 10 parallel research agents, one per category:
  1. CRM and Sales (10 apps)
  2. Support and Helpdesk (10 apps)
  3. Communications and Messaging (10 apps)
  4. Marketing, Ads, Email and Social (10 apps)
  5. Ecommerce (10 apps)
  6. Data, SEO and Scraping (10 apps)
  7. Developer, Infra and Data platforms (10 apps)
  8. Productivity and Project Management (10 apps)
  9. Finance and Fintech (10 apps)
  10. AI, Research and Media-native (10 apps)

- Each agent received the v2 prompt with the exact app list for its category
- Agents ran in parallel via the Task tool, each producing a JSON file
  in `outputs/` (e.g., `outputs/crm-sales.json`)

### Post-Research Audit

After the bulk phase, a manual audit revealed:

1. **52% substitution rate** — 52 of 100 apps had been silently substituted
   by agents that couldn't find documentation for the assigned app. All 52
   were re-researched from scratch.

2. **Data corruption** — 2 entries (SE Ranking, Salesforce Commerce Cloud)
   had wrong app data (SendGrid's data under `se-ranking`, Salesforce CRM's
   data under `salesforce-commerce-cloud`). Both were re-researched from
   live documentation.

3. **Aggregate stats recomputed** — After all corrections, aggregate numbers
   (MCP %, self-serve %, etc.) were recalculated from the fixed JSON.

### Where Composio's SDK/MCP Was Used

The research agent used standard web tools (websearch, webfetch) to investigate
each app's documentation. Composio's SDK was not directly called during the
research phase — the agent operated as an independent research tool, producing
structured JSON that could later be consumed by Composio's integration pipeline.

### Files Produced

- `outputs/*.json` — Per-category research outputs (may contain off-list apps)
- `outputs/missing-*.json` — Re-research batches for substituted apps
- `all-apps.json` — v1 corrupted dataset (in `scratch/`)
- `all-apps-v2.json` — Intermediate audit file (in `scratch/`)
- `all-apps-final.json` — Canonical 100-app dataset (authoritative source)
