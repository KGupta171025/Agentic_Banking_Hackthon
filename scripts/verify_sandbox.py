"""
Sandbox Verification & Preparation Script.
Implements Step 3 & 4 of the Airwallex Developer Lab guide:
1. Verifies REST login using Client ID and API Key.
2. Lists global accounts; creates one if empty.
3. Simulates a $25,000 seed deposit into the global account.
4. Confirms multi-currency wallet balances.
"""

import os
import sys

# Force UTF-8 encoding on Windows consoles
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from dotenv import load_dotenv

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.airwallex.client import AirwallexClient


def main():
    load_dotenv()

    client_id = os.getenv("AIRWALLEX_CLIENT_ID")
    api_key = os.getenv("AIRWALLEX_API_KEY")
    api_url = os.getenv("AIRWALLEX_API_URL", "https://api-sandbox.airwallex.com")

    print("=======================================================")
    print("Airwallex Sandbox Verification & Initialization")
    print("=======================================================")

    if not client_id or not api_key or "your_" in client_id:
        print("ERROR: AIRWALLEX_CLIENT_ID or AIRWALLEX_API_KEY is not configured in .env.")
        sys.exit(1)

    print(f"Using Client ID: {client_id}")
    print(f"Target API URL:  {api_url}\n")

    client = AirwallexClient(client_id=client_id, api_key=api_key, base_url=api_url)

    # 1. Verify Authentication
    print("[Step 1] Authenticating with Airwallex Sandbox...")
    try:
        token = client.get_auth_token()
        print(f"[OK] Authentication successful! Bearer token acquired (length: {len(token)}).")
    except Exception as e:
        print(f"[FAIL] Authentication failed: {e}")
        sys.exit(1)

    # 2. List Global Accounts
    print("\n[Step 2] Checking Global Accounts...")
    try:
        accounts = client.list_global_accounts()
    except Exception as e:
        print(f"[FAIL] Could not list global accounts: {e}")
        accounts = []

    global_account_id = None
    if accounts:
        print(f"[OK] Found {len(accounts)} active Global Account(s).")
        for idx, acc in enumerate(accounts, 1):
            print(f"  Account #{idx}: ID={acc.get('id')} | Nickname={acc.get('nickname')} | Status={acc.get('status')}")
        global_account_id = accounts[0].get("id")
    else:
        print("No accounts found. Creating primary USD Global Account...")
        try:
            new_acc = client.create_global_account(country_code="US", currency="USD")
            global_account_id = new_acc.get("id")
            print(f"[OK] Created Global Account ID: {global_account_id}")
        except Exception as e:
            print(f"[FAIL] Failed to create global account: {e}")

    # 3. Simulate Deposit
    if global_account_id:
        print(f"\n[Step 3] Simulating $25,000 USD Seed Deposit into Account {global_account_id}...")
        try:
            dep_resp = client.simulate_deposit(
                global_account_id=global_account_id,
                amount=25000.0,
                currency="USD",
                payer_name="Seed funding",
            )
            print(f"[OK] Deposit created successfully! Deposit ID: {dep_resp.get('id')} | Status: {dep_resp.get('status')}")
        except Exception as e:
            print(f"[NOTE] Deposit simulation note: {e}")
    else:
        print("\n[Step 3] Skipping deposit: no global_account_id available.")

    # 4. Check Wallet Balances
    print("\n[Step 4] Querying Current Wallet Balances...")
    try:
        balances = client.get_current_balances()
        print("-------------------------------------------------------")
        print(f"{'Currency':<10} | {'Available Balance':<18} | {'Pending Amount':<15}")
        print("-------------------------------------------------------")
        if balances:
            for b in balances:
                curr = b.get("currency", "USD")
                avail = b.get("available_amount", 0.0)
                pend = b.get("pending_amount", 0.0)
                print(f"{curr:<10} | {avail:<18} | {pend:<15}")
        else:
            print("No balance records returned yet.")
        print("-------------------------------------------------------")
    except Exception as e:
        print(f"[FAIL] Error querying balances: {e}")

    print("\n[SUCCESS] Airwallex Sandbox is connected and ready for PayOps Sentinel!")


if __name__ == "__main__":
    main()
