"""
Terminal Demonstration Script for MobiMart 52-Week Rolling Simulator & Baseline Benchmark.
Runs the 52-week simulation for Baseline vs MobiMart and prints a professional terminal report.
"""

import sys
import pandas as pd
from typing import Dict, List, Any

from backend.engine.simulation.models import SimulationConfig
from backend.engine.simulation.state import (
    build_starting_inventory_snapshot,
    build_warehouse_opening_state,
)
from backend.engine.simulation.runner import run_simulation
from backend.engine.simulation.comparison import compare_strategies

def run_demo() -> None:
    """Run full 52-week simulation benchmark and output terminal report."""
    print("Loading MobiMart datasets...")
    stores = pd.read_csv("data/generated/stores.csv").to_dict(orient="records")
    products = pd.read_csv("data/generated/products.csv").to_dict(orient="records")
    sales_history_df = pd.read_csv("data/generated/sales_history.csv")
    inventory_df = pd.read_csv("data/generated/inventory.csv")

    config = SimulationConfig(
        start_week=1,
        end_week=52,
        capital_budget_limit=40000000.0,
        starting_capital_target=38000000.0,
        warehouse_cover_weeks=8.0,
        store_transfer_cost_per_unit=500.0,
        warehouse_allocation_cost_per_unit=250.0,
        baseline_lookback_weeks=4,
        dead_stock_lookback_weeks=4,
        block_high_risk_eol_replenishment=True,
    )

    print("Building budget-compliant starting operational inventory snapshot...")
    starting_snapshot = build_starting_inventory_snapshot(
        inventory_df_or_records=inventory_df,
        products=products,
        stores=stores,
        target_capital=config.starting_capital_target,
    )

    print("Building warehouse opening inventory stock...")
    warehouse_opening = build_warehouse_opening_state(
        products=products,
        sales_history_df=sales_history_df,
        cover_weeks=config.warehouse_cover_weeks,
    )
    tot_wh_units = sum(warehouse_opening.values())

    print("Running Strategy A: Naive Baseline Simulator (52 weeks)...")
    baseline_run = run_simulation(
        strategy_name="BASELINE",
        sales_history_df=sales_history_df,
        stores=stores,
        products=products,
        starting_snapshot=starting_snapshot,
        warehouse_opening_stock=warehouse_opening,
        config=config,
    )

    print("Running Strategy B: MobiMart Intelligent Engine Simulator (52 weeks)...")
    mobimart_run = run_simulation(
        strategy_name="MOBIMART",
        sales_history_df=sales_history_df,
        stores=stores,
        products=products,
        starting_snapshot=starting_snapshot,
        warehouse_opening_stock=warehouse_opening,
        config=config,
    )

    comp = compare_strategies(baseline_run, mobimart_run)

    # Format Rupee formatting helper
    def fmt_cr(val: float) -> str:
        return f"₹{val / 10000000.0:.2f} Cr"

    def fmt_curr(val: float) -> str:
        return f"₹{val:,.2f}"

    def fmt_delta_curr(val: float) -> str:
        sign = "+" if val >= 0 else "-"
        return f"{sign}₹{abs(val):,.2f}"

    def fmt_delta_pp(val: float) -> str:
        sign = "+" if val >= 0 else ""
        return f"{sign}{val:.1f} percentage points"

    def fmt_delta_val(val: float, suffix: str = "") -> str:
        sign = "+" if val >= 0 else ""
        return f"{sign}{val:.2f}{suffix}"

    print("\n====================================================")
    print("MOBIMART 52-WEEK SIMULATION")
    print("====================================================")

    print(f"\nStarting Operational Inventory:\n{fmt_cr(starting_snapshot.operational_inventory_cost)} (Headroom: {fmt_cr(starting_snapshot.capital_headroom)})")
    print(f"\nStarting Warehouse Inventory:\n{tot_wh_units:,} units")
    print(f"\nEvaluation Period:\nWeek {config.start_week} → Week {config.end_week}")

    print("\n----------------------------------------------------")
    print("NAIVE BASELINE")
    print("----------------------------------------------------")
    print(f"Stockout Rate:\n{baseline_run.stockout_rate:.1f}%")
    print(f"Average Weeks of Cover:\n{baseline_run.average_weeks_of_cover:.1f}")
    print(f"Dead Stock:\n{baseline_run.dead_stock_pct:.1f}%")
    print(f"Markdown Loss:\n{fmt_curr(baseline_run.actual_markdown_loss)}")
    print(f"Capital Turns:\n{baseline_run.capital_turns:.2f}x")
    print(f"Revenue:\n{fmt_curr(baseline_run.total_revenue)}")
    print(f"Gross Margin:\n{fmt_curr(baseline_run.total_gross_margin)}")
    print(f"Lost Sales:\n{baseline_run.total_lost_sales_units:,} units ({fmt_curr(baseline_run.total_lost_sales_value)})")

    print("\n----------------------------------------------------")
    print("MOBIMART INTELLIGENT ENGINE")
    print("----------------------------------------------------")
    print(f"Stockout Rate:\n{mobimart_run.stockout_rate:.1f}%")
    print(f"Average Weeks of Cover:\n{mobimart_run.average_weeks_of_cover:.1f}")
    print(f"Dead Stock:\n{mobimart_run.dead_stock_pct:.1f}%")
    print(f"Markdown Loss:\n{fmt_curr(mobimart_run.actual_markdown_loss)}")
    print(f"Capital Turns:\n{mobimart_run.capital_turns:.2f}x")
    print(f"Revenue:\n{fmt_curr(mobimart_run.total_revenue)}")
    print(f"Gross Margin:\n{fmt_curr(mobimart_run.total_gross_margin)}")
    print(f"Lost Sales:\n{mobimart_run.total_lost_sales_units:,} units ({fmt_curr(mobimart_run.total_lost_sales_value)})")

    print("\n----------------------------------------------------")
    print("MOBIMART vs BASELINE")
    print("----------------------------------------------------")
    st_diff = comp.metrics["Stockout Rate"].absolute_difference
    ds_diff = comp.metrics["Dead Stock %"].absolute_difference
    mk_diff = comp.metrics["Actual Markdown Loss"].absolute_difference
    ct_diff = comp.metrics["Capital Turns"].absolute_difference
    rv_diff = comp.metrics["Total Revenue"].absolute_difference
    gm_diff = comp.metrics["Total Gross Margin"].absolute_difference

    print(f"Stockout Rate:\n{fmt_delta_pp(st_diff)}")
    print(f"Dead Stock:\n{fmt_delta_pp(ds_diff)}")
    print(f"Markdown Loss:\n{fmt_delta_curr(mk_diff)}")
    print(f"Capital Turns:\n{fmt_delta_val(ct_diff, 'x')}")
    print(f"Revenue:\n{fmt_delta_curr(rv_diff)}")
    print(f"Gross Margin:\n{fmt_delta_curr(gm_diff)}")

    print("\n----------------------------------------------------")
    print("EOL ACTIONS")
    print("----------------------------------------------------")
    print(f"Markdowned Units:\n{mobimart_run.total_markdowned_units:,}")
    print(f"Transferred Units:\n{mobimart_run.total_transferred_units:,}")
    print(f"Transfer Cost:\n{fmt_curr(mobimart_run.total_transfer_cost)}")
    print(f"Markdown Loss:\n{fmt_curr(mobimart_run.actual_markdown_loss)}")

    print("\n====================================================")
    print(f"Benchmark completed in {mobimart_run.runtime_seconds + baseline_run.runtime_seconds:.2f} seconds.")
    print("====================================================")

if __name__ == "__main__":
    run_demo()
