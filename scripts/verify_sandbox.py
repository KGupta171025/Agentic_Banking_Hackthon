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
from dotenv import load_dotenv
from rich.console import Console
from rich.table import Table

# Add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.airwallex.client import AirwallexClient

console = Console()


def main():
    load_dotenv()

    client_id = os.getenv("AIRWALLEX_CLIENT_ID")
    api_key = os.getenv("AIRWALLEX_API_KEY")
    api_url = os.getenv("AIRWALLEX_API_URL", "https://api-sandbox.airwallex.com")

    console.print(
        "[bold cyan]🔍 Airwallex Sandbox Verification & Initialization[/bold cyan]"
    )

    if not client_id or not api_key or "your_" in client_id:
        console.print(
            "[bold red]❌ Error:[/bold red] AIRWALLEX_CLIENT_ID or AIRWALLEX_API_KEY is not set in `.env`."
        )
        console.print("Please create `.env` based on `.env.example` and add your sandbox credentials.")
        console.print("Get credentials from: [underline]https://www.sandbox.airwallex.com/app/#/developer/api-keys[/underline]")
        sys.exit(1)

    client = AirwallexClient(client_id=client_id, api_key=api_key, base_url=api_url)

    # 1. Verify Authentication
    console.print("\n[yellow]Step 1: Authenticating with Airwallex Sandbox...[/yellow]")
    try:
        token = client.get_auth_token()
        console.print(f"[bold green]✔ Auth successful![/bold green] Token acquired (len={len(token)}).")
    except Exception as e:
        console.print(f"[bold red]❌ Auth failed:[/bold red] {e}")
        sys.exit(1)

    # 2. List Global Accounts
    console.print("\n[yellow]Step 2: Checking Global Accounts...[/yellow]")
    accounts = client.list_global_accounts()
    global_account_id = None

    if accounts:
        console.print(f"[bold green]✔ Found {len(accounts)} Global Account(s).[/bold green]")
        global_account_id = accounts[0].get("id")
        console.print(f"Primary Account ID: [bold]{global_account_id}[/bold]")
    else:
        console.print("[dim]No accounts found. Creating primary USD account...[/dim]")
        new_acc = client.create_global_account(country_code="US", currency="USD")
        global_account_id = new_acc.get("id")
        console.print(f"[bold green]✔ Created Global Account ID: {global_account_id}[/bold green]")

    # 3. Simulate Deposit
    console.print("\n[yellow]Step 3: Simulating $25,000 Deposit...[/yellow]")
    try:
        deposit_resp = client.simulate_deposit(
            global_account_id=global_account_id,
            amount=25000.0,
            currency="USD",
            payer_name="Seed funding",
        )
        console.print(f"[bold green]✔ Deposit simulated![/bold green] Status: {deposit_resp.get('status')}")
    except Exception as e:
        console.print(f"[dim yellow]Notice during deposit: {e}[/dim yellow]")

    # 4. Check Wallet Balances
    console.print("\n[yellow]Step 4: Fetching Wallet Balances...[/yellow]")
    balances = client.get_current_balances()

    table = Table(title="Airwallex Wallet Balances")
    table.add_column("Currency", style="cyan")
    table.add_column("Available Balance", style="green")
    table.add_column("Pending Amount", style="magenta")

    for b in balances:
        table.add_row(
            b.get("currency", "USD"),
            str(b.get("available_amount", "0.0")),
            str(b.get("pending_amount", "0.0")),
        )

    console.print(table)
    console.print(
        "\n[bold green]🎉 Sandbox environment is fully ready for PayOps Sentinel![/bold green]"
    )


if __name__ == "__main__":
    main()
