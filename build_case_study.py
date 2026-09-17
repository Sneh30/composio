import json, glob, os
from collections import Counter

# 1. Load all category JSONs
all_apps = []
for f in sorted(glob.glob('outputs/*.json')):
    with open(f) as fh:
        all_apps.extend(json.load(fh))

# 2. Add the 11 validated sample apps
sample_apps = [
    {"app_id": "salesforce", "app_name": "Salesforce", "category": "CRM and Sales", "one_liner": "Enterprise CRM platform", "auth": {"methods": ["OAuth2", "Bearer_token"], "auth_notes": "OAuth 2.0 JWT bearer flow for server-to-server, OAuth 2.0 authorization code for user-context."}, "access": {"type": "self-serve", "access_notes": "Free Developer Edition org for testing. Production requires Enterprise/Unlimited license."}, "api_surface": {"type": "REST", "breadth": "broad", "breadth_notes": "Comprehensive REST and SOAP APIs covering all objects, metadata, analytics.", "existing_mcp": True, "mcp_source": "community"}, "mcp_auth": {"methods": ["OAuth2"], "mcp_auth_notes": "MCP uses OAuth 2.0 authorization code flow.", "same_credentials_as_rest_api": True}, "mcp_access": {"type": "self-serve", "mcp_access_notes": "Community MCP server available on GitHub."}, "buildability_signal": {"blockers_observed": [], "notes": "Very strong API surface, many existing integrations."}, "evidence": [{"claim": "OAuth 2.0", "url": "https://help.salesforce.com/s/articleView?id=sf.remoteaccess_oauth_web_server_flow.htm", "quote": "The OAuth 2.0 web server flow is for web applications that are hosted on a secure server."}], "confidence_per_field": {"auth": "high", "access": "high", "api_surface": "high", "mcp_auth": "medium"}, "research_notes": "", "fetched_urls": []},
    {"app_id": "linear", "app_name": "Linear", "category": "CRM and Sales", "one_liner": "Modern issue tracking and project management", "auth": {"methods": ["OAuth2", "API_key"], "auth_notes": "OAuth 2.0 for user-context access, API key for personal access."}, "access": {"type": "self-serve", "access_notes": "Free tier available with API access."}, "api_surface": {"type": "GraphQL", "breadth": "broad", "breadth_notes": "Full GraphQL API covering issues, projects, teams, cycles.", "existing_mcp": True, "mcp_source": "official"}, "mcp_auth": {"methods": ["OAuth2"], "mcp_auth_notes": "Official MCP server uses OAuth 2.0.", "same_credentials_as_rest_api": True}, "mcp_access": {"type": "self-serve", "mcp_access_notes": "Available on free plan."}, "buildability_signal": {"blockers_observed": [], "notes": "Excellent API surface with official MCP."}, "evidence": [{"claim": "API key", "url": "https://developers.linear.app/docs/api-reference", "quote": "Authenticate with a personal API key or OAuth 2.0."}], "confidence_per_field": {"auth": "high", "access": "high", "api_surface": "high", "mcp_auth": "high"}, "research_notes": "", "fetched_urls": []},
    {"app_id": "slack", "app_name": "Slack", "category": "Communications", "one_liner": "Team messaging and collaboration platform", "auth": {"methods": ["OAuth2", "Bearer_token"], "auth_notes": "OAuth 2.0 for user/bot tokens, Bearer token for workspace apps."}, "access": {"type": "self-serve", "access_notes": "Free tier with API access. Paid plans for more features."}, "api_surface": {"type": "REST", "breadth": "broad", "breadth_notes": "Comprehensive API: messaging, channels, users, files, admin.", "existing_mcp": True, "mcp_source": "official"}, "mcp_auth": {"methods": ["OAuth2"], "mcp_auth_notes": "Official MCP plugin uses OAuth 2.0.", "same_credentials_as_rest_api": True}, "mcp_access": {"type": "self-serve", "mcp_access_notes": "MCP plugin available for agent-assisted development."}, "buildability_signal": {"blockers_observed": [], "notes": "Very mature API ecosystem."}, "evidence": [{"claim": "OAuth", "url": "https://docs.slack.dev/authentication", "quote": "OAuth 2.0 is the primary authentication method for Slack apps."}], "confidence_per_field": {"auth": "high", "access": "high", "api_surface": "high", "mcp_auth": "high"}, "research_notes": "", "fetched_urls": []},
    {"app_id": "twenty", "app_name": "Twenty", "category": "CRM and Sales", "one_liner": "Open-source CRM alternative to Salesforce", "auth": {"methods": ["API_key", "OAuth2"], "auth_notes": "API key for personal access, OAuth 2.0 for integrations."}, "access": {"type": "self-serve", "access_notes": "Open source, self-hostable. Cloud plans available."}, "api_surface": {"type": "REST", "breadth": "moderate", "breadth_notes": "REST and GraphQL APIs for CRM objects.", "existing_mcp": True, "mcp_source": "official"}, "mcp_auth": {"methods": ["OAuth2"], "mcp_auth_notes": "MCP server uses OAuth 2.0 authentication.", "same_credentials_as_rest_api": False}, "mcp_access": {"type": "self-serve", "mcp_access_notes": "MCP included on paid cloud plans."}, "buildability_signal": {"blockers_observed": [], "notes": "Open source with growing ecosystem."}, "evidence": [{"claim": "API", "url": "https://docs.twenty.com/developers/extend/api", "quote": "Twenty provides REST and GraphQL APIs for all CRM operations."}], "confidence_per_field": {"auth": "high", "access": "high", "api_surface": "high", "mcp_auth": "high"}, "research_notes": "", "fetched_urls": []},
    {"app_id": "apify", "app_name": "Apify", "category": "Data, SEO and Scraping", "one_liner": "Web scraping and automation platform", "auth": {"methods": ["API_key", "Bearer_token"], "auth_notes": "API token for REST API, Bearer token for authenticated requests."}, "access": {"type": "self-serve", "access_notes": "Free tier with $5 monthly credit."}, "api_surface": {"type": "REST", "breadth": "broad", "breadth_notes": "Full API for actors, runs, datasets, storage.", "existing_mcp": True, "mcp_source": "official"}, "mcp_auth": {"methods": ["OAuth2", "Bearer_token", "agentic"], "mcp_auth_notes": "MCP supports OAuth 2.0, Bearer token, and anonymous agentic access.", "same_credentials_as_rest_api": False}, "mcp_access": {"type": "self-serve", "mcp_access_notes": "MCP available with free tier."}, "buildability_signal": {"blockers_observed": [], "notes": "Very accessible with multiple auth paths."}, "evidence": [{"claim": "MCP auth", "url": "https://docs.apify.com/integrations/mcp", "quote": "Apify MCP supports OAuth 2.0, API token, and anonymous agentic access."}], "confidence_per_field": {"auth": "high", "access": "high", "api_surface": "high", "mcp_auth": "high"}, "research_notes": "", "fetched_urls": []},
    {"app_id": "sherlock", "app_name": "Sherlock", "category": "Developer Tools and Infra", "one_liner": "Username OSINT tool for finding accounts across platforms", "auth": {"methods": ["None"], "auth_notes": "CLI tool, no API authentication needed."}, "access": {"type": "self-serve", "access_notes": "Open source, pip install."}, "api_surface": {"type": "CLI", "breadth": "narrow", "breadth_notes": "Single-purpose CLI tool for username enumeration.", "existing_mcp": False, "mcp_source": "none"}, "mcp_auth": None, "mcp_access": None, "buildability_signal": {"blockers_observed": [], "notes": "CLI-only, no API to integrate with."}, "evidence": [{"claim": "CLI only", "url": "https://github.com/sherlock-project/sherlock", "quote": "Sherlock can find a user profile on 400+ social networks."}], "confidence_per_field": {"auth": "n/a", "access": "high", "api_surface": "high", "mcp_auth": "n/a"}, "research_notes": "", "fetched_urls": []},
    {"app_id": "mermaid-cli", "app_name": "Mermaid CLI", "category": "Developer Tools and Infra", "one_liner": "Diagram generation tool from text definitions", "auth": {"methods": ["None"], "auth_notes": "CLI tool, no authentication."}, "access": {"type": "self-serve", "access_notes": "Open source, npm install."}, "api_surface": {"type": "CLI", "breadth": "narrow", "breadth_notes": "Single-purpose CLI for rendering diagrams.", "existing_mcp": False, "mcp_source": "none"}, "mcp_auth": None, "mcp_access": None, "buildability_signal": {"blockers_observed": [], "notes": "CLI-only, no API."}, "evidence": [{"claim": "CLI", "url": "https://github.com/mermaid-js/mermaid-cli", "quote": "Command line interface for generating Mermaid diagrams."}], "confidence_per_field": {"auth": "n/a", "access": "high", "api_surface": "high", "mcp_auth": "n/a"}, "research_notes": "", "fetched_urls": []},
    {"app_id": "dealcloud", "app_name": "DealCloud (Intapp)", "category": "CRM and Sales", "one_liner": "Enterprise relationship and deal management CRM for finance", "auth": {"methods": ["API_key", "Bearer_token"], "auth_notes": "REST API: API key generated from user profile. Bearer token for requests."}, "access": {"type": "admin-approval-gated", "access_notes": "API access requires admin to enable API capability in user group permissions."}, "api_surface": {"type": "REST", "breadth": "broad", "breadth_notes": "Broad REST API: Schema, Data, User Management, Publications, Backups, Relationship Intelligence.", "existing_mcp": True, "mcp_source": "official"}, "mcp_auth": {"methods": ["OAuth2"], "mcp_auth_notes": "MCP uses OAuth 2.0 with pre-registered clients only. Different from REST API key.", "same_credentials_as_rest_api": False}, "mcp_access": {"type": "client-allowlist-gated", "mcp_access_notes": "Only pre-registered AI clients can connect via OAuth."}, "buildability_signal": {"blockers_observed": ["Admin approval for REST", "Celeste license for MCP"], "notes": "Well-documented but double-gated."}, "evidence": [{"claim": "MCP OAuth", "url": "https://api.docs.dealcloud.com/mcp/authentication", "quote": "DealCloud MCP maintains a set of pre-registered client integrations — only AI clients with a pre-registered redirect URI can connect."}], "confidence_per_field": {"auth": "high", "access": "high", "api_surface": "high", "mcp_auth": "high"}, "research_notes": "", "fetched_urls": []},
    {"app_id": "fanbasis", "app_name": "FanBasis (now Commas)", "category": "Finance and Fintech", "one_liner": "Creator payments platform with checkout and BNPL", "auth": {"methods": ["unknown"], "auth_notes": "No public API documentation found."}, "access": {"type": "partnership-gated", "access_notes": "Enterprise APIs require sales contact."}, "api_surface": {"type": "undocumented", "breadth": "unknown", "breadth_notes": "Enterprise section mentions APIs but no public reference.", "existing_mcp": True, "mcp_source": "official"}, "mcp_auth": {"methods": ["unknown"], "mcp_auth_notes": "MCP listed as beta on enterprise page, no auth details.", "same_credentials_as_rest_api": "unknown"}, "mcp_access": {"type": "partnership-gated", "mcp_access_notes": "MCP under Enterprise section."}, "buildability_signal": {"blockers_observed": ["No public API docs", "Enterprise gate"], "notes": "Has APIs and MCP but all behind enterprise gate."}, "evidence": [{"claim": "Enterprise APIs", "url": "https://commas.com/enterprises", "quote": "APIs and embeddable components, live in days not quarters."}], "confidence_per_field": {"auth": "low", "access": "high", "api_surface": "low", "mcp_auth": "low"}, "research_notes": "", "fetched_urls": []},
    {"app_id": "ipayx", "app_name": "iPayX", "category": "Finance and Fintech", "one_liner": "FINTRAC-registered FX forensic audit layer", "auth": {"methods": ["unknown"], "auth_notes": "Could not determine. Docs page returned 404."}, "access": {"type": "unknown", "access_notes": "Could not determine."}, "api_surface": {"type": "unknown", "breadth": "unknown", "breadth_notes": "No accessible API documentation.", "existing_mcp": False, "mcp_source": "unknown"}, "mcp_auth": None, "mcp_access": None, "buildability_signal": {"blockers_observed": ["Docs 404"], "notes": "Cannot assess without documentation."}, "evidence": [{"claim": "FINTRAC", "url": "https://ipayx.ai/docs", "quote": "FINTRAC-registered (MSB C10001283) FX forensic audit layer."}], "confidence_per_field": {"auth": "low", "access": "low", "api_surface": "low", "mcp_auth": "n/a"}, "research_notes": "", "fetched_urls": []},
    {"app_id": "waterfall", "app_name": "Waterfall.io", "category": "Data, SEO and Scraping", "one_liner": "B2B contact data enrichment API", "auth": {"methods": ["API_key"], "auth_notes": "API key via x-api-key header."}, "access": {"type": "partnership-gated", "access_notes": "Book a Call required, no self-serve signup."}, "api_surface": {"type": "REST", "breadth": "broad", "breadth_notes": "13 endpoints: Prospector, Search, Enrichment, Verification, etc.", "existing_mcp": False, "mcp_source": "none"}, "mcp_auth": None, "mcp_access": None, "buildability_signal": {"blockers_observed": ["No self-serve signup"], "notes": "Strong API but requires sales conversation."}, "evidence": [{"claim": "API key", "url": "https://docs.waterfall.io/v1/introduction", "quote": "All requests require an API key in the x-api-key header."}], "confidence_per_field": {"auth": "high", "access": "high", "api_surface": "high", "mcp_auth": "n/a"}, "research_notes": "", "fetched_urls": []}
]

all_apps.extend(sample_apps)
print(f"Total apps loaded: {len(all_apps)}")

# 3. Deduplicate by app_id
seen = set()
deduped = []
for app in all_apps:
    aid = app.get("app_id", "")
    if aid not in seen:
        seen.add(aid)
        deduped.append(app)

print(f"After dedup: {len(deduped)}")

# 4. Save merged JSON
with open("all-apps.json", "w") as f:
    json.dump(deduped, f, indent=2)

# 5. Pattern analysis
print("\n=== PATTERN ANALYSIS ===")

auth_counter = Counter()
for app in deduped:
    for m in app.get("auth", {}).get("methods", []):
        auth_counter[m] += 1
print("\nAuth methods across all apps:")
for k, v in auth_counter.most_common():
    print(f"  {k}: {v}")

access_counter = Counter()
for app in deduped:
    access_counter[app.get("access", {}).get("type", "unknown")] += 1
print("\nAccess types:")
for k, v in access_counter.most_common():
    print(f"  {k}: {v}")

mcp_counter = Counter()
for app in deduped:
    mcp_counter[str(app.get("api_surface", {}).get("existing_mcp", False))] += 1
print("\nMCP availability:")
for k, v in mcp_counter.most_common():
    print(f"  {k}: {v}")

mcp_source_counter = Counter()
for app in deduped:
    mcp_source_counter[app.get("api_surface", {}).get("mcp_source", "unknown")] += 1
print("\nMCP source:")
for k, v in mcp_source_counter.most_common():
    print(f"  {k}: {v}")

mcp_auth_same = Counter()
for app in deduped:
    mcp_auth = app.get("mcp_auth")
    if mcp_auth and mcp_auth.get("same_credentials_as_rest_api") is not None:
        mcp_auth_same[str(mcp_auth["same_credentials_as_rest_api"])] += 1
print("\nMCP auth same as REST:")
for k, v in mcp_auth_same.most_common():
    print(f"  {k}: {v}")

cat_counter = Counter()
for app in deduped:
    cat_counter[app.get("category", "unknown")] += 1
print("\nApps per category:")
for k, v in cat_counter.most_common():
    print(f"  {k}: {v}")

conf_counter = Counter()
for app in deduped:
    for field, conf in app.get("confidence_per_field", {}).items():
        if conf != "n/a":
            conf_counter[conf] += 1
print("\nConfidence across all fields:")
for k, v in conf_counter.most_common():
    print(f"  {k}: {v}")

print("\n=== HIGH-VALUE FINDINGS: MCP auth differs from REST ===")
for app in deduped:
    mcp_auth = app.get("mcp_auth")
    if mcp_auth and mcp_auth.get("same_credentials_as_rest_api") == False:
        print(f"  {app['app_name']}: REST={app['auth']['methods']}, MCP={mcp_auth['methods']}")

print("\n=== SELF-SERVE vs GATED ===")
for app in deduped:
    access = app.get("access", {})
    if access.get("type") in ["admin-approval-gated", "partnership-gated"]:
        print(f"  {access['type']}: {app['app_name']}")

print("\nDone. Saved merged JSON to all-apps.json")
