# Configuration - Fill in your details here
DEST_API_KEY = "YOUR KEY HERE"
SOURCE_API_KEY = "YOUR KEY HERE"
DEST_ORG_ID = "YOUR ORG ID HERE"
SOURCE_ORG_ID = "YOUR ORG ID HERE"

import meraki
import json
import sys

# =============================================================================
# CONFIG
# =============================================================================

source = meraki.DashboardAPI(SOURCE_API_KEY)
dest = meraki.DashboardAPI(DEST_API_KEY)

# =============================================================================
# MAIN
# =============================================================================

def main():
    print("Meraki Organization Migration - Manual Unclaim")
    print("=" * 60)

    # Step 1: Get ALL devices in source org
    print("Fetching devices from source organization...")
    try:
        inventory = source.organizations.getOrganizationDevices(SOURCE_ORG_ID, total_pages=-1)
    except Exception as e:
        print(f"Failed to fetch devices: {e}")
        sys.exit(1)

    if not inventory:
        print("No devices found in source org.")
        sys.exit(1)

    serials = [d["serial"] for d in inventory]
    print(f"\nFound {len(serials)} device(s):")
    for s in serials:
        print(f"  {s}")

    # Step 2: Instruct user to manually unclaim
    print("\n" + "="*60)
    print("MANUAL STEP REQUIRED:")
    print("1. Open SOURCE organization in Meraki Dashboard")
    print("2. Go to Organization → Inventory")
    print("3. Select ALL devices above")
    print("4. Click 'Unclaim'")
    print("5. Confirm 'Are you sure?' → YES")
    print("="*60)

    input("\nPress Enter when you have UNCLAIMED all devices from the SOURCE org...")

    confirm = ""
    while confirm != "YES":
        confirm = input("\nType YES to continue claiming into destination org: ").strip().upper()
        if confirm != "YES":
            print("Please type YES when ready.")

    # Step 3: Claim into destination
    print(f"\nClaiming {len(serials)} devices into destination org...")
    try:
        dest.organizations.claimIntoOrganization(
            organizationId=DEST_ORG_ID,
            serials=serials
        )
        print("  Claim successful!")
    except Exception as e:
        print(f"  Claim failed: {e}")
        print("  Try again after a few minutes or contact Meraki support.")
        sys.exit(1)

    # Step 4: Fetch networks & re-add devices
    print("\nFetching source network configs...")
    try:
        source_networks = source.organizations.getOrganizationNetworks(SOURCE_ORG_ID, total_pages=-1)
    except Exception as e:
        print(f"Failed to fetch networks: {e}")
        source_networks = []

    config = {}
    device_map = {}  # serial → source network ID
    network_names = {}

    for dev in inventory:
        net_id = dev.get("networkId")
        if net_id:
            device_map[dev["serial"]] = net_id
            try:
                net = source.networks.getNetwork(net_id)
                network_names[net_id] = net["name"]
            except:
                network_names[net_id] = net_id

    for net in source_networks:
        net_id = net["id"]
        config[net_id] = {"name": net["name"], "productTypes": net["productTypes"], "settings": {}}

        # Copy SSIDs
        try:
            ssids = source.wireless.getNetworkWirelessSsids(net_id)
            if ssids:
                config[net_id]["settings"]["ssids"] = ssids
        except: pass

        # Add other settings as needed (firewall, VLANs, etc.)

       # Step 5: Create networks in destination
    print("\nCreating networks in destination org...")
    network_map = {}  # source_net_id → new_net_id
    for net in source_networks:
        net_id = net["id"]
        name = net["name"]
        product_types = net["productTypes"]

        try:
            # CORRECT METHOD
            new_net = dest.organizations.createOrganizationNetwork(
                organizationId=DEST_ORG_ID,
                name=name,
                productTypes=product_types
            )
            new_id = new_net["id"]
            network_map[net_id] = new_id
            print(f"  Created '{name}' → {new_id}")

            # Copy SSIDs
            try:
                ssids = source.wireless.getNetworkWirelessSsids(net_id)
                print("    Applying SSIDs...")
                for ssid in ssids:
                    num = ssid["number"]
                    payload = {k: v for k, v in ssid.items() if k != "number"}
                    dest.wireless.updateNetworkWirelessSsid(
                        networkId=new_id,
                        number=num,
                        **payload
                    )
            except Exception as e:
                print(f"    SSID copy failed: {e}")

        except Exception as e:
            print(f"  Failed to create network '{name}': {e}")

    # Step 6: Re-add devices to correct networks
    print("\nRe-adding devices to new networks...")
    added = 0
    for serial, src_net_id in device_map.items():
        if src_net_id not in network_map:
            continue
        new_net_id = network_map[src_net_id]
        try:
            dest.networks.claimNetworkDevices(new_net_id, serials=[serial])
            print(f"  Added {serial} → {config[src_net_id]['name']}")
            added += 1
        except Exception as e:
            print(f"  Failed to add {serial}: {e}")

    unbound = [s for s in serials if s not in device_map]
    if unbound:
        print(f"  {len(unbound)} device(s) → inventory: {', '.join(unbound)}")

    print(f"\nMigration complete!")
    print(f"  {len(serials)} devices claimed")
    print(f"  {len(config)} networks created")
    print(f"  {added} devices re-added to networks")
    print("\nDone! Check destination org.")

if __name__ == "__main__":
    main()
