#!/usr/bin/env python3
"""
validate.py — Hard validation that all-apps-final.json contains exactly the
canonical 100 apps. Compares by NORMALIZED NAME (not position, not substring,
not app_id). Exits non-zero on any mismatch.

Usage:
    python3 validate.py                    # validates all-apps-final.json
    python3 validate.py path/to/file.json  # validates custom file
"""
import json, re, sys
from pathlib import Path

# ── Canonical 100 apps: normalized name → category ──
# This is the ground truth. Every entry must match exactly by normalized name.
CANONICAL = {
    # CRM and Sales (10)
    "attio":                     "CRM and Sales",
    "close":                     "CRM and Sales",
    "copper":                    "CRM and Sales",
    "dealcloud (intapp)":        "CRM and Sales",
    "hubspot":                   "CRM and Sales",
    "pipedrive":                 "CRM and Sales",
    "podio":                     "CRM and Sales",
    "salesforce":                "CRM and Sales",
    "twenty":                    "CRM and Sales",
    "zoho crm":                  "CRM and Sales",
    # Support and Helpdesk (10)
    "freshdesk":                 "Support and Helpdesk",
    "front":                     "Support and Helpdesk",
    "gladly":                    "Support and Helpdesk",
    "gorgias":                   "Support and Helpdesk",
    "help scout":                "Support and Helpdesk",
    "intercom":                  "Support and Helpdesk",
    "liveagent":                 "Support and Helpdesk",
    "plain":                     "Support and Helpdesk",
    "pylon":                     "Support and Helpdesk",
    "zendesk":                   "Support and Helpdesk",
    # Communications and Messaging (10)
    "aircall":                   "Communications and Messaging",
    "discord":                   "Communications and Messaging",
    "lark (larksuite)":          "Communications and Messaging",
    "pumble":                    "Communications and Messaging",
    "slack":                     "Communications and Messaging",
    "telegram":                  "Communications and Messaging",
    "twilio":                    "Communications and Messaging",
    "vonage":                    "Communications and Messaging",
    "whatsapp business":         "Communications and Messaging",
    "zoho cliq":                 "Communications and Messaging",
    # Marketing, Ads, Email and Social (10)
    "google ads":                "Marketing, Ads, Email and Social",
    "gohighlevel":               "Marketing, Ads, Email and Social",
    "klaviyo":                   "Marketing, Ads, Email and Social",
    "linkedin ads":              "Marketing, Ads, Email and Social",
    "mailchimp":                 "Marketing, Ads, Email and Social",
    "meta ads":                  "Marketing, Ads, Email and Social",
    "pinterest":                 "Marketing, Ads, Email and Social",
    "sendgrid":                  "Marketing, Ads, Email and Social",
    "threads (meta)":            "Marketing, Ads, Email and Social",
    "systeme.io":                "Marketing, Ads, Email and Social",
    # Ecommerce (10)
    "amazon selling partner api":"Ecommerce",
    "bigcommerce":               "Ecommerce",
    "ecwid":                     "Ecommerce",
    "fanbasis (now commas)":     "Ecommerce",
    "gumroad":                   "Ecommerce",
    "squarespace":               "Ecommerce",
    "magento (adobe commerce)":  "Ecommerce",
    "shopify":                   "Ecommerce",
    "salesforce commerce cloud": "Ecommerce",
    "woocommerce":               "Ecommerce",
    # Data, SEO and Scraping (10)
    "ahrefs":                    "Data, SEO and Scraping",
    "apify":                     "Data, SEO and Scraping",
    "bright data":               "Data, SEO and Scraping",
    "clay":                      "Data, SEO and Scraping",
    "dataforseo":                "Data, SEO and Scraping",
    "firecrawl":                 "Data, SEO and Scraping",
    "mrscraper":                 "Data, SEO and Scraping",
    "se ranking":                "Data, SEO and Scraping",
    "sherlock":                  "Data, SEO and Scraping",
    "waterfall.io":              "Data, SEO and Scraping",
    # Developer, Infra and Data platforms (10)
    "cloudflare":                "Developer, Infra and Data platforms",
    "datadog":                   "Developer, Infra and Data platforms",
    "github":                    "Developer, Infra and Data platforms",
    "mongodb atlas":             "Developer, Infra and Data platforms",
    "neo4j":                     "Developer, Infra and Data platforms",
    "netlify":                   "Developer, Infra and Data platforms",
    "sentry":                    "Developer, Infra and Data platforms",
    "snowflake":                 "Developer, Infra and Data platforms",
    "supabase":                  "Developer, Infra and Data platforms",
    "vercel":                    "Developer, Infra and Data platforms",
    # Productivity and Project Management (10)
    "airtable":                  "Productivity and Project Management",
    "asana":                     "Productivity and Project Management",
    "clickup":                   "Productivity and Project Management",
    "coda":                      "Productivity and Project Management",
    "harvest":                   "Productivity and Project Management",
    "jira":                      "Productivity and Project Management",
    "linear":                    "Productivity and Project Management",
    "monday.com":                "Productivity and Project Management",
    "notion":                    "Productivity and Project Management",
    "smartsheet":                "Productivity and Project Management",
    # Finance and Fintech (10)
    "binance":                   "Finance and Fintech",
    "brex":                      "Finance and Fintech",
    "paygent connect":           "Finance and Fintech",
    "pitchbook":                 "Finance and Fintech",
    "plaid":                     "Finance and Fintech",
    "quickbooks":                "Finance and Fintech",
    "ramp":                      "Finance and Fintech",
    "stripe":                    "Finance and Fintech",
    "xero":                      "Finance and Fintech",
    "ipayx":                     "Finance and Fintech",
    # AI, Research and Media-native (10)
    "consensus":                 "AI, Research and Media-native",
    "devin":                     "AI, Research and Media-native",
    "fathom":                    "AI, Research and Media-native",
    "grain":                     "AI, Research and Media-native",
    "mermaid cli":               "AI, Research and Media-native",
    "notebooklm":                "AI, Research and Media-native",
    "otter.ai":                  "AI, Research and Media-native",
    "reducto":                   "AI, Research and Media-native",
    "youtube transcript":        "AI, Research and Media-native",
    "higgsfield":                "AI, Research and Media-native",
}


def norm(name: str) -> str:
    """Strict normalization: lowercase, strip, collapse whitespace."""
    return re.sub(r'\s+', ' ', name.strip().lower())


def validate(data_path: str) -> bool:
    with open(data_path) as f:
        apps = json.load(f)

    errors = []

    # 1. Count check
    if len(apps) != 100:
        errors.append(f"FATAL: Expected 100 apps, got {len(apps)}")

    # 2. Build set of normalized names from JSON
    json_names = {}
    for i, app in enumerate(apps):
        n = norm(app.get("app_name", ""))
        if n in json_names:
            errors.append(f"DUPLICATE: '{app.get('app_name')}' appears at positions #{json_names[n]+1} and #{i+1}")
        json_names[n] = i

    json_name_set = set(json_names.keys())
    canonical_name_set = set(CANONICAL.keys())

    # 3. Diff: what's in canonical but not in JSON?
    missing = canonical_name_set - json_name_set
    for m in sorted(missing):
        errors.append(f"MISSING: '{m}' (expected category: {CANONICAL[m]})")

    # 4. Diff: what's in JSON but not in canonical?
    extra = json_name_set - canonical_name_set
    for e in sorted(extra):
        pos = json_names[e] + 1
        errors.append(f"EXTRA: '{e}' at position #{pos} — not in canonical 100-app list")

    # 5. Category check for matched apps
    for n in json_name_set & canonical_name_set:
        expected_cat = CANONICAL[n]
        actual_cat = apps[json_names[n]].get("category", "")
        if norm(actual_cat) != norm(expected_cat):
            pos = json_names[n] + 1
            errors.append(f"CATEGORY MISMATCH: '{n}' at #{pos} — expected '{expected_cat}', got '{actual_cat}'")

    # Report
    print(f"\n{'='*60}")
    print(f"VALIDATION: {data_path}")
    print(f"{'='*60}")
    print(f"Apps in file:     {len(apps)}")
    print(f"Canonical apps:   {len(CANONICAL)}")
    print(f"Matched:          {len(json_name_set & canonical_name_set)}")
    print(f"Missing:          {len(missing)}")
    print(f"Extra:            {len(extra)}")
    print(f"Duplicates:       {len([e for e in errors if 'DUPLICATE' in e])}")
    print(f"Category errors:  {len([e for e in errors if 'CATEGORY' in e])}")

    if errors:
        print(f"\nERRORS ({len(errors)}):")
        for e in errors:
            print(f"  ✗ {e}")
        print(f"\n✗ VALIDATION FAILED")
        return False
    else:
        print(f"\n✓ ALL CHECKS PASSED — exactly 100 canonical apps, no missing, no extras, no duplicates")
        return True


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "all-apps-final.json"
    ok = validate(path)
    sys.exit(0 if ok else 1)
