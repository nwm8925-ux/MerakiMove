#!/usr/bin/env python3
import requests, json, sys

# -------------------------------------------------
# 1. Paste your Meraki API key here (or pass as argument)
API_KEY = "YOUR API KEY"      # <-- replace this
# -------------------------------------------------

def get_org_id(api_key):
    url = "https://api.meraki.com/api/v1/organizations"
    headers = {
        "X-Cisco-Meraki-API-Key": api_key,
        "Content-Type": "application/json"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        orgs = resp.json()
    except Exception as e:
        print(f"Error calling Meraki API: {e}", file=sys.stderr)
        sys.exit(1)

    if not orgs:
        print("No organizations found for this API key.")
        sys.exit(1)

    # Print a nice table
    print("\nOrganization(s) accessible with this API key:")
    print("-" * 60)
    for org in orgs:
        print(f"ID : {org['id']}\nName: {org['name']}\n")
    print("-" * 60)

    # Return the first (usually only) ID for scripting
    return orgs[0]['id']

if __name__ == "__main__":
    key = API_KEY.strip()
    if key == "YOUR_API_KEY_HERE":
        print("Edit the script and replace YOUR_API_KEY_HERE with your real key.")
        sys.exit(1)
    org_id = get_org_id(key)
    print(f"\nPrimary Org ID (copy-paste): {org_id}\n")
