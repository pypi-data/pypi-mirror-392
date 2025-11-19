#!/usr/bin/env python3
"""
Test script for new v0.3.0 endpoints.
Tests the 4 new HIGH PRIORITY endpoints added in version 0.3.0.
"""

import os
from dotenv import load_dotenv
from src.marqeta_diva_mcp.client import DiVAClient

# Load environment variables
load_dotenv()

def test_transaction_token():
    """Test transaction token mapping endpoint (CRITICAL for reconciliation)."""
    print("\n" + "="*80)
    print("TEST 1: Transaction Token Mapping (get_transaction_token)")
    print("="*80)
    print("Purpose: Map Core API transaction tokens to DiVA report tokens")
    print("Use Case: Reconciliation between webhooks and reports\n")

    try:
        client = DiVAClient()
        # Query for transaction tokens (limited count for testing)
        result = client.get_view("transactiontoken", None, count=5)

        if result.get("records"):
            print(f"✅ SUCCESS: Retrieved {len(result['records'])} transaction token mappings")
            print(f"Sample record: {result['records'][0]}")
        else:
            print("⚠️  No transaction token data available (may not have recent transactions)")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

def test_card_counts():
    """Test card counts endpoint."""
    print("\n" + "="*80)
    print("TEST 2: Card Counts (get_card_counts)")
    print("="*80)
    print("Purpose: Track card metrics over time")
    print("Use Case: Monitor card program health\n")

    try:
        client = DiVAClient()
        # Query for card counts aggregated by day
        result = client.get_view("cardcounts", "day", count=5)

        if result.get("records"):
            print(f"✅ SUCCESS: Retrieved {len(result['records'])} card count records")
            print(f"Sample record: {result['records'][0]}")
        else:
            print("⚠️  No card count data available")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

def test_user_counts():
    """Test user counts endpoint."""
    print("\n" + "="*80)
    print("TEST 3: User Counts (get_user_counts)")
    print("="*80)
    print("Purpose: Track user base growth")
    print("Use Case: Monitor user engagement metrics\n")

    try:
        client = DiVAClient()
        # Query for user counts aggregated by day
        result = client.get_view("usercounts", "day", count=5)

        if result.get("records"):
            print(f"✅ SUCCESS: Retrieved {len(result['records'])} user count records")
            print(f"Sample record: {result['records'][0]}")
        else:
            print("⚠️  No user count data available")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

def test_activity_balances_network_detail():
    """Test activity balances network detail endpoint."""
    print("\n" + "="*80)
    print("TEST 4: Activity Balances Network Detail (get_activity_balances_network_detail)")
    print("="*80)
    print("Purpose: Break out transactions by card network")
    print("Use Case: Analyze network-specific transaction volumes\n")

    try:
        client = DiVAClient()
        # Query for activity balances with network detail
        result = client.get_view("activitybalances/day/networkdetail", None, count=5)

        if result.get("records"):
            print(f"✅ SUCCESS: Retrieved {len(result['records'])} network detail records")
            print(f"Sample record: {result['records'][0]}")
        else:
            print("⚠️  No network detail data available")

    except Exception as e:
        print(f"❌ FAILED: {str(e)}")

def main():
    """Run all endpoint tests."""
    print("\n" + "#"*80)
    print("#" + " "*78 + "#")
    print("#  Marqeta DiVA MCP Server v0.3.0 - New Endpoint Tests".center(80) + "#")
    print("#" + " "*78 + "#")
    print("#"*80)

    # Verify environment is configured
    if not all([os.getenv("MARQETA_APP_TOKEN"), os.getenv("MARQETA_ACCESS_TOKEN"), os.getenv("MARQETA_PROGRAM")]):
        print("\n❌ ERROR: Missing required environment variables")
        print("Required: MARQETA_APP_TOKEN, MARQETA_ACCESS_TOKEN, MARQETA_PROGRAM")
        return 1

    print(f"\n✓ Environment configured for program: {os.getenv('MARQETA_PROGRAM')}")

    # Run tests
    test_transaction_token()
    test_card_counts()
    test_user_counts()
    test_activity_balances_network_detail()

    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    print("\nAll 4 new endpoints have been tested.")
    print("\n✅ If you see SUCCESS messages above, the endpoints are working correctly!")
    print("⚠️  If you see warnings, your program may not have data for those views yet.")
    print("❌ If you see FAILED, check the error messages for details.\n")
    print("Next steps:")
    print("1. Review the test results above")
    print("2. Try the endpoints in your MCP client (Claude Desktop, etc.)")
    print("3. Use the audit report (ENDPOINT_AUDIT.md) for implementation details")
    print("\n" + "="*80 + "\n")

    return 0

if __name__ == "__main__":
    exit(main())
