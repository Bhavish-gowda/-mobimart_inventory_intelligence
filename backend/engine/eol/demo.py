"""
EOL Risk Engine Defense Demo for MobiMart.
Runs End-of-Life risk assessments against the generated dataset and
displays exposure, option comparisons, recommended actions, and rupee impact.
"""

import pandas as pd
from backend.engine.eol.decision import run_eol_portfolio_assessment
from backend.engine.eol.summary import generate_eol_summary


def run_demo():
    print("=" * 60)
    print("   MOBIMART EOL RISK ENGINE - PHASE 3B DEFENSE DEMO")
    print("=" * 60)

    # Load generated dataset
    stores = pd.read_csv("data/generated/stores.csv").to_dict(orient="records")
    products = pd.read_csv("data/generated/products.csv").to_dict(orient="records")
    sales_df = pd.read_csv("data/generated/sales_history.csv")
    inventory = pd.read_csv("data/generated/inventory.csv").to_dict(orient="records")

    planning_week = 24

    print(f"\n  Planning Week: {planning_week}")
    print(f"  Stores: {len(stores)} | Products: {len(products)} | Inventory Records: {len(inventory)}")

    # Run EOL assessment engine
    print("\n  Running EOL risk assessment across all store-product positions...")
    assessments, resolution = run_eol_portfolio_assessment(
        stores=stores,
        products=products,
        inventory_records=inventory,
        sales_history_df=sales_df,
        current_week=planning_week,
        min_risk_level="MEDIUM",
    )

    summary = generate_eol_summary(assessments, resolution)

    # ──────────────────────────────────────────────
    print("\n--- 1. PORTFOLIO EOL EXPOSURE SUMMARY ---")
    print(f"  Total EOL-Risk Units:          {summary.total_eol_risk_units:,} units")
    print(f"  Total Inventory Value at Risk: ₹{summary.total_inventory_value_at_risk:,.2f}")
    print(f"  Risky SKUs:                    {summary.risky_sku_count}")
    print(f"  Risky Stores:                  {summary.risky_store_count}")
    print()
    print(f"  Markdown Exposure (all units): ₹{summary.markdown_exposure:,.2f}")
    print(f"  Hold Exposure (all units):     ₹{summary.hold_exposure:,.2f}")
    print(f"  Candidate Transfer Opportunity: ₹{summary.candidate_transfer_opportunity:,.2f}")
    print(f"  Approved Transfer Opportunity:  ₹{summary.approved_transfer_opportunity:,.2f}")
    print(f"  Approved Transfer Units:        {summary.approved_transfer_units}")
    print(f"  Approved Transfer Cost:         ₹{summary.approved_transfer_cost:,.2f}")
    print(f"  Approved Transfer Routes:       {summary.approved_transfer_routes}")
    print(f"  Rejected Destination Capacity:  {summary.rejected_due_to_destination_capacity}")
    print(f"  Rejected Source Capacity:       {summary.rejected_due_to_source_capacity}")

    # ──────────────────────────────────────────────
    print("\n--- 2. RECOMMENDED ACTIONS BREAKDOWN ---")
    for action, count in summary.action_breakdown.items():
        print(f"  {action}: {count} positions")
    print()
    print(f"  Recommended Markdown: {summary.recommended_markdown_units} units | Cost: ₹{summary.recommended_markdown_cost:,.2f}")
    print(f"  Recommended Transfer: {summary.recommended_transfer_units} units | Logistics: ₹{summary.recommended_transfer_cost:,.2f}")
    print(f"  Recommended Hold:     {summary.recommended_hold_units} units | Exposure: ₹{summary.recommended_hold_cost:,.2f}")

    # ──────────────────────────────────────────────
    print("\n--- 3. TOP 10 HIGHEST-RISK POSITIONS ---")
    for i, a in enumerate(assessments[:10], 1):
        trans_avail = "✓" if a.transfer_option.units_affected > 0 else "✗"
        print(
            f"\n  #{i} [{a.risk_level}] {a.product_id} ({a.product_name}) @ {a.store_id}"
        )
        print(f"     Risk Score:    {a.risk_score:.1f}/100 | Stage: {a.lifecycle_stage}")
        print(f"     Inventory:     {a.inventory_units} units | WOC: {a.weeks_of_cover:.1f} wks | Value: ₹{a.inventory_value:,.2f}")
        if a.weeks_to_successor is not None:
            conf_pct = int(a.successor_confidence * 100)
            print(f"     Successor:     {a.successor_id} in {a.weeks_to_successor:.1f} wks (confidence: {conf_pct}%)")
        print(f"     Markdown Loss: ₹{a.markdown_option.net_financial_loss:,.2f}")
        print(f"     Hold Loss:     ₹{a.hold_option.net_financial_loss:,.2f}")
        if a.transfer_option.net_financial_loss != float('inf'):
            print(f"     Transfer Loss: ₹{a.transfer_option.net_financial_loss:,.2f} → {a.transfer_option.target_store_id} [{trans_avail}]")
        else:
            print(f"     Transfer:      Not viable (no demand destination) [✗]")
        print(f"     ⭐ RECOMMENDATION: {a.recommended_action} (Expected Loss: ₹{a.expected_financial_impact:,.2f})")
        print(f"     📋 {a.explanation[:180]}{'...' if len(a.explanation) > 180 else ''}")

    # ──────────────────────────────────────────────
    print("\n--- 4. TOP 5 APPROVED TRANSFER ROUTES ---")
    transfer_recs = [a for a in assessments if a.recommended_action == "TRANSFER"]
    if transfer_recs:
        for a in transfer_recs[:5]:
            print(
                f"  {a.product_id} ({a.product_name}): {a.store_id} → {a.transfer_option.target_store_id} | "
                f"{a.transfer_option.units_affected} units | Logistics: ₹{a.transfer_option.expected_cost:,.2f}"
            )
    else:
        print("  No TRANSFER recommendations (all markdown or hold preferred).")

    # ──────────────────────────────────────────────
    print("\n--- 5. MARKDOWN vs TRANSFER vs HOLD EXAMPLE ---")
    example = assessments[0] if assessments else None
    if example:
        print(f"\n  Product: {example.product_name} | Store: {example.store_id}")
        print(f"  MARKDOWN: ₹{example.markdown_option.net_financial_loss:,.2f}")
        print(f"    {example.markdown_option.explanation}")
        print(f"\n  TRANSFER: ₹{example.transfer_option.net_financial_loss if example.transfer_option.net_financial_loss != float('inf') else 'N/A' }")
        print(f"    {example.transfer_option.explanation}")
        print(f"\n  HOLD: ₹{example.hold_option.net_financial_loss:,.2f}")
        print(f"    {example.hold_option.explanation}")
        print(f"\n  ⭐ Decision: {example.recommended_action} (Expected Loss: ₹{example.expected_financial_impact:,.2f})")

    print("\n" + "=" * 60)
    print("  END OF EOL RISK ENGINE DEMO")
    print("=" * 60)


if __name__ == "__main__":
    run_demo()
