# API Integration Research Agent

A research agent that investigates 100 software applications for API and MCP (Model Context Protocol) integration potential, producing structured JSON outputs with verbatim evidence. Built for the **Composio AI Product Ops Intern** take-home assignment.

## What This Is

The agent researches 100 apps across 10 categories (CRM, Support, Communications, Marketing, Ecommerce, Data/SEO, Developer/Infra, Productivity, Finance, AI/Media) and captures per-app:

- **Auth methods** — OAuth2, API key, Bearer, Basic, Session, None
- **Access type** — Self-serve, admin-gated, partnership-gated, gated, unknown
- **API surface** — REST, GraphQL, CLI, mixed; breadth (narrow/moderate/broad)
- **MCP availability** — Official vs community servers, with separate MCP auth block
- **Buildability signal** — Blockers observed and assessment
- **Evidence** — Verbatim quotes from source documentation with URLs

## Key Findings

| Metric | Value |
|--------|-------|
| Apps researched | 100 (10 per category) |
| Have MCP servers | 91 (91%) |
| Official MCP | 60 |
| Self-serve access | 85 (85%) |
| MCP auth differs from REST | 12 apps |
| Apps with zero blockers | 76 |

**Headline patterns:**
1. MCP is established, not emerging — 91% adoption
2. Official MCP is winning — 60 of 91 are vendor-shipped
3. OAuth 2.0 dominates (61 apps), but API keys (50) are close
4. MCP auth differs from REST in 12 apps — cannot reuse credentials
5. 85% self-serve — most APIs accessible without sales calls
6. CRM, Communications, Ecommerce, Marketing: 100% MCP. Finance: 70%

## How the Agent Works

### Three-Phase Approach

1. **Phase 1 — Prompt Design:** Tested on 5 easy apps (Stripe, Linear, Slack, Twenty, Apify) and 7 edge cases (Sherlock, Mermaid CLI, DealCloud, FanBasis, iPayX, Waterfall, Higgsfield). Identified failures and iterated prompt from v1 to v2.

2. **Phase 2 — v2 Validation:** Rebuilt prompt with verbatim quote requirement and separate `mcp_auth` / `mcp_access` blocks. Added `Session_auth` / `None` enums and `client-allowlist-gated` access type. Validated on 11 sample apps.

3. **Phase 3 — Bulk Research:** 10 parallel agents (one per category) researching all 100 apps simultaneously. Each agent received the v2 prompt with the exact app list for its category.

### Where the Human Was Needed

- **Prompt iteration:** v1 → v2 based on DealCloud edge case (MCP uses OAuth, REST uses API key)
- **Verbatim quote requirement:** Added after spotting potential fabrication in v1
- **MCP auth separation:** Split into separate block when MCP uses different auth than REST
- **Quality control:** Verified 11 sample apps against live docs, caught fabricated quotes
- **Accuracy audit:** Discovered 52 of 100 apps were substituted by agents during bulk phase
- **Data corruption fix:** Caught 2 entries (SE Ranking, SFCC) with wrong app data post-submission

## Accuracy & Verification

### Automated Checks (all pass)
- 100 apps, 10 per category, exact assignment list match
- All required fields present in every entry
- Auth methods normalized to enum values
- All evidence entries contain verbatim quotes
- Zero duplicate app_ids or app_names
- Cross-check: app_id matches app_name for all 100 entries

### Stratified Spot-Checks (14/14 verified)
Apps sampled across all 10 categories, multiple auth methods, self-serve/gated access, official/community/no-MCP:

| App | Category | Finding | Verified Against |
|-----|----------|---------|-----------------|
| Salesforce | CRM | OAuth2 + Bearer, community MCP | help.salesforce.com |
| Slack | Comms | OAuth2 + Bearer, official MCP | api.slack.com |
| Shopify | Ecommerce | OAuth2 + Bearer, official MCP, GraphQL | shopify.dev |
| Ahrefs | Data/SEO | Bearer + OAuth2, auth differs for MCP | ahrefs.com/api |
| GitHub | Developer | OAuth2 + API_key, official MCP | docs.github.com |
| Notion | Productivity | Bearer + OAuth2, official MCP | developers.notion.com |
| Stripe | Finance | API_key + OAuth2, official MCP | stripe.com/docs |
| Intercom | Support | Bearer + OAuth2, official MCP | developers.intercom.com |
| SFCC | Ecommerce | OAuth2 + Basic, gated, official MCP | developer.salesforce.com |
| SE Ranking | Data/SEO | API_key, official MCP (corrected) | seranking.com/api |
| Netlify | Developer | OAuth2 + API_key, no MCP | docs.netlify.com |
| Mermaid CLI | AI/Media | None auth, no MCP | github.com/mermaid-js |
| iPayX | Finance | unknown, no MCP (docs 404) | ipayx.com |
| Gladly | Support | Basic_auth, admin-gated, no MCP | gladly.com |

### Accuracy Trajectory
- **Pass 1 (v1):** ~70% — fabricated quotes, wrong apps, folded MCP auth
- **Pass 2 (v2):** ~90% — verbatim quotes, separated MCP auth
- **Pass 3 (audit):** ~95% — all 100 apps, normalized enums, verified
- **Pass 4 (corruption fix):** ~99% — caught 2 data-corruption entries, re-researched from live docs

## Honest Failures

- **SE Ranking / SFCC data corruption:** Agent substituted app names during bulk phase; `se-ranking` had SendGrid's data, `salesforce-commerce-cloud` had Salesforce CRM's data. Caught by third-party JSON audit, re-researched from live docs.
- **52% first-pass substitution rate:** Initial agent run substituted 52 of 100 apps. Caught during manual audit, all 52 re-researched.
- **iPayX docs 404:** All documentation URLs returned 404. Honest "unknown" returned.
- **NotebookLM no public API:** Google-managed product, no developer API.
- **Paygent Connect sparse docs:** Japanese payment gateway, limited English docs.
- **PitchBook enterprise-only:** Standalone contract required, no self-serve path.

## Files

| File | Description |
|------|-------------|
| `index.html` | Single-page HTML case study (live at https://sneh30.github.io/composio/) |
| `all-apps-final.json` | **Canonical** 100-app dataset (authoritative source) |
| `validate.py` | Assignment validation script — checks all 100 apps against canonical list |
| `outputs/*.json` | Per-category JSON files (may contain off-list apps from bulk phase) |
| `build_case_study.py` | Aggregation and pattern analysis script |
| `README.md` | This file |

### Scratch / Off-List Files (not for submission)

| File | Description |
|------|-------------|
| `all-apps.json` | v1 corrupted dataset — superseded by `all-apps-final.json` |
| `all-apps-v2.json` | Intermediate audit file — contains ~137 unique apps (13 extra off-list) |
| `outputs/missing-*.json` | Re-research batch files generated during audit phase |

## How to Run

```bash
# View the case study
open index.html

# Or visit live: https://sneh30.github.io/composio/

# Regenerate from JSON (optional)
python3 generate_case_study.py
```

Requires Python 3.8+, no external dependencies.
