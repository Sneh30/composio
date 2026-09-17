#!/usr/bin/env python3
"""
BUG 2 FIX: Hard validation that all-apps-final.json matches the canonical
100-app assignment list exactly — by position, app_name, and category.

Run as part of build_case_study.py or standalone. Exits non-zero on any mismatch.
"""
import json, sys, re
from pathlib import Path

# ── Canonical assignment list: position → (app_name, category) ──
# Extracted from the original assignment document. This is ground truth.
ASSIGNMENT = {
    1:   ("Attio",                     "CRM and Sales"),
    2:   ("Close",                     "CRM and Sales"),
    3:   ("Copper",                    "CRM and Sales"),
    4:   ("DealCloud (Intapp)",        "CRM and Sales"),
    5:   ("HubSpot",                   "CRM and Sales"),
    6:   ("Pipedrive",                 "CRM and Sales"),
    7:   ("Podio",                     "CRM and Sales"),
    8:   ("Salesforce",                "CRM and Sales"),
    9:   ("Twenty",                    "CRM and Sales"),
    10:  ("Zoho CRM",                  "CRM and Sales"),
    11:  ("Freshdesk",                 "Support and Helpdesk"),
    12:  ("Front",                     "Support and Helpdesk"),
    13:  ("Gladly",                    "Support and Helpdesk"),
    14:  ("Gorgias",                   "Support and Helpdesk"),
    15:  ("Help Scout",                "Support and Helpdesk"),
    16:  ("Intercom",                  "Support and Helpdesk"),
    17:  ("LiveAgent",                 "Support and Helpdesk"),
    18:  ("Plain",                     "Support and Helpdesk"),
    19:  ("Pylon",                     "Support and Helpdesk"),
    20:  ("Zendesk",                   "Support and Helpdesk"),
    21:  ("Aircall",                   "Communications and Messaging"),
    22:  ("Discord",                   "Communications and Messaging"),
    23:  ("Lark (Larksuite)",          "Communications and Messaging"),
    24:  ("Pumble",                    "Communications and Messaging"),
    25:  ("Slack",                     "Communications and Messaging"),
    26:  ("Telegram",                  "Communications and Messaging"),
    27:  ("Twilio",                    "Communications and Messaging"),
    28:  ("Vonage",                    "Communications and Messaging"),
    29:  ("WhatsApp Business",         "Communications and Messaging"),
    30:  ("Zoho Cliq",                 "Communications and Messaging"),
    31:  ("Google Ads",                "Marketing, Ads, Email and Social"),
    32:  ("Google Calendar",           "Marketing, Ads, Email and Social"),
    33:  ("Klaviyo",                   "Marketing, Ads, Email and Social"),
    34:  ("LinkedIn Ads",              "Marketing, Ads, Email and Social"),
    35:  ("Mailchimp",                 "Marketing, Ads, Email and Social"),
    36:  ("Meta Ads",                  "Marketing, Ads, Email and Social"),
    37:  ("Pinterest",                 "Marketing, Ads, Email and Social"),
    38:  ("SendGrid",                  "Marketing, Ads, Email and Social"),
    39:  ("Threads (Meta)",            "Marketing, Ads, Email and Social"),
    40:  ("systeme.io",                "Marketing, Ads, Email and Social"),
    41:  ("Amazon Selling Partner API","Ecommerce"),
    42:  ("BigCommerce",               "Ecommerce"),
    43:  ("Ecwid",                     "Ecommerce"),
    44:  ("FanBasis (now Commas)",     "Ecommerce"),
    45:  ("Gumroad",                   "Ecommerce"),
    46:  ("Squarespace",               "Ecommerce"),
    47:  ("Magento (Adobe Commerce)",  "Ecommerce"),
    48:  ("Shopify",                   "Ecommerce"),
    49:  ("Square",                    "Ecommerce"),
    50:  ("WooCommerce",               "Ecommerce"),
    51:  ("Ahrefs",                    "Data, SEO and Scraping"),
    52:  ("Apify",                     "Data, SEO and Scraping"),
    53:  ("Bright Data",               "Data, SEO and Scraping"),
    54:  ("Clay",                      "Data, SEO and Scraping"),
    55:  ("DataForSEO",                "Data, SEO and Scraping"),
    56:  ("Firecrawl",                 "Data, SEO and Scraping"),
    57:  ("MrScraper",                 "Data, SEO and Scraping"),
    58:  ("SE Ranking",                "Data, SEO and Scraping"),
    59:  ("Sherlock",                  "Data, SEO and Scraping"),
    60:  ("Waterfall.io",              "Data, SEO and Scraping"),
    61:  ("Cloudflare",                "Developer, Infra and Data platforms"),
    62:  ("Datadog",                   "Developer, Infra and Data platforms"),
    63:  ("GitHub",                    "Developer, Infra and Data platforms"),
    64:  ("MongoDB Atlas",             "Developer, Infra and Data platforms"),
    65:  ("Neo4j",                     "Developer, Infra and Data platforms"),
    66:  ("Netlify",                   "Developer, Infra and Data platforms"),
    67:  ("Sentry",                    "Developer, Infra and Data platforms"),
    68:  ("Snowflake",                 "Developer, Infra and Data platforms"),
    69:  ("Supabase",                  "Developer, Infra and Data platforms"),
    70:  ("Vercel",                    "Developer, Infra and Data platforms"),
    71:  ("Airtable",                  "Productivity and Project Management"),
    72:  ("Asana",                     "Productivity and Project Management"),
    73:  ("ClickUp",                   "Productivity and Project Management"),
    74:  ("Coda",                      "Productivity and Project Management"),
    75:  ("Harvest",                   "Productivity and Project Management"),
    76:  ("Jira",                      "Productivity and Project Management"),
    77:  ("Linear",                    "Productivity and Project Management"),
    78:  ("Monday.com",                "Productivity and Project Management"),
    79:  ("Notion",                    "Productivity and Project Management"),
    80:  ("Smartsheet",                "Productivity and Project Management"),
    81:  ("Binance",                   "Finance and Fintech"),
    82:  ("Brex",                      "Finance and Fintech"),
    83:  ("Paygent Connect",           "Finance and Fintech"),
    84:  ("PitchBook",                 "Finance and Fintech"),
    85:  ("Plaid",                     "Finance and Fintech"),
    86:  ("QuickBooks",                "Finance and Fintech"),
    87:  ("Ramp",                      "Finance and Fintech"),
    88:  ("Stripe",                    "Finance and Fintech"),
    89:  ("Xero",                      "Finance and Fintech"),
    90:  ("iPayX",                     "Finance and Fintech"),
    91:  ("Consensus",                 "AI, Research and Media-native"),
    92:  ("Devin",                     "AI, Research and Media-native"),
    93:  ("Fathom",                    "AI, Research and Media-native"),
    94:  ("Grain",                     "AI, Research and Media-native"),
    95:  ("Mermaid CLI",               "AI, Research and Media-native"),
    96:  ("NotebookLM",                "AI, Research and Media-native"),
    97:  ("Otter.ai",                  "AI, Research and Media-native"),
    98:  ("Reducto",                   "AI, Research and Media-native"),
    99:  ("YouTube Transcript",        "AI, Research and Media-native"),
    100: ("higgsfield",                "AI, Research and Media-native"),
}


def normalize(name: str) -> str:
    """Strict normalized comparison — lowercase, strip, collapse whitespace."""
    return re.sub(r'\s+', ' ', name.strip().lower())


def validate(data_path: str = "all-apps-final.json") -> bool:
    with open(data_path) as f:
        apps = json.load(f)

    errors = []
    warnings = []

    # 1. Count check
    if len(apps) != 100:
        errors.append(f"FATAL: Expected 100 apps, got {len(apps)}")

    # 2. Check each position
    seen_names = {}
    seen_ids = {}
    for i, app in enumerate(apps):
        pos = i + 1
        if pos not in ASSIGNMENT:
            errors.append(f"Position #{pos}: no assignment entry (off-list app '{app.get('app_name')}')")
            continue

        expected_name, expected_cat = ASSIGNMENT[pos]
        actual_name = app.get("app_name", "")
        actual_cat = app.get("category", "")

        # Name match (strict normalized, NOT substring)
        if normalize(actual_name) != normalize(expected_name):
            errors.append(f"Position #{pos}: expected '{expected_name}', got '{actual_name}'")

        # Category match
        if normalize(actual_cat) != normalize(expected_cat):
            errors.append(f"Position #{pos} ({expected_name}): expected category '{expected_cat}', got '{actual_cat}'")

        # Duplicate name check
        name_key = normalize(actual_name)
        if name_key in seen_names:
            errors.append(f"Duplicate app_name '{actual_name}' at positions #{seen_names[name_key]} and #{pos}")
        seen_names[name_key] = pos

        # Duplicate ID check
        aid = app.get("app_id", "")
        if aid in seen_ids:
            errors.append(f"Duplicate app_id '{aid}' at positions #{seen_ids[aid]} and #{pos}")
        seen_ids[aid] = pos

    # 3. Check for off-list apps in assignment
    assigned_names = {normalize(v[0]) for v in ASSIGNMENT.values()}
    for i, app in enumerate(apps):
        pos = i + 1
        if pos <= 100:
            continue  # already checked above
        errors.append(f"Off-list entry at position #{pos}: '{app.get('app_name')}'")

    # Report
    print(f"\n{'='*60}")
    print(f"VALIDATION: {data_path}")
    print(f"{'='*60}")
    print(f"Apps in file: {len(apps)}")
    print(f"Errors: {len(errors)}")
    print(f"Warnings: {len(warnings)}")

    if errors:
        print(f"\nERRORS:")
        for e in errors:
            print(f"  ✗ {e}")
    if warnings:
        print(f"\nWARNINGS:")
        for w in warnings:
            print(f"  ! {w}")

    if not errors:
        print(f"\n✓ ALL CHECKS PASSED — 100 apps match assignment by position, name, and category")
        return True
    else:
        print(f"\n✗ VALIDATION FAILED — {len(errors)} error(s)")
        return False


if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else "all-apps-final.json"
    ok = validate(path)
    sys.exit(0 if ok else 1)
