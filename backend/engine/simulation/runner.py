"""
52-Week Rolling Simulation Runner for MobiMart & Baseline Benchmark.
Implements the full weekly rolling execution loop with shared EOL operational layer,
zero future data leakage, inventory conservation identity checks, and complete metrics reporting.
"""

import time
from typing import Dict, List, Any, Tuple
import pandas as pd
import numpy as np

from backend.engine.allocation.allocator import allocate_inventory
from backend.engine.eol.decision import run_eol_portfolio_assessment
from backend.engine.simulation.models import (
    SimulationConfig,
    StartingInventorySnapshot,
    WeeklySimulationResult,
    SimulationRunResult,
)
from backend.engine.simulation.state import (
    build_starting_inventory_snapshot,
    build_warehouse_opening_state,
    get_independent_store_inventory,
)
from backend.engine.simulation.inventory import (
    apply_eol_transfers,
    apply_eol_markdowns,
    fulfill_weekly_demand,
    verify_inventory_conservation,
)
from backend.engine.simulation.baseline import allocate_baseline_inventory
from backend.engine.simulation.metrics import (
    calculate_dead_stock_units,
    aggregate_simulation_metrics,
)

def run_simulation(
    strategy_name: str,
    sales_history_df: pd.DataFrame,
    stores: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    starting_snapshot: StartingInventorySnapshot,
    warehouse_opening_stock: Dict[str, int],
    config: SimulationConfig = SimulationConfig(),
) -> SimulationRunResult:
    """
    Run 52-week rolling simulation for strategy_name ("BASELINE" or "MOBIMART").
    """
    start_time = time.time()
    products_by_id = {p["id"]: p for p in products}

    # Precompute per-week dead-stock sales index for all (store, product) pairs
    # This avoids repeating groupby inside each week of the simulation loop.
    # Key: week_number -> Dict[(store_id, product_id) -> units_sold sum over lookback]
    # We build a rolling map: for each week W, sales_by_pair[W] covers [W-lookback, W-1]
    _dead_stock_sales_cache: Dict[int, Dict] = {}
    _woc_sales_cache: Dict[int, Dict] = {}
    for W in range(config.start_week, config.end_week + 1):
        if W > 1:
            ds_start = max(1, W - config.dead_stock_lookback_weeks)
            ds_end = W - 1
            ds_hist = sales_history_df[
                (sales_history_df["week_number"] >= ds_start) &
                (sales_history_df["week_number"] <= ds_end)
            ]
            _dead_stock_sales_cache[W] = ds_hist.groupby(["store_id", "product_id"])["units_sold"].sum().to_dict()

            woc_start = max(1, W - 4)
            woc_hist = sales_history_df[
                (sales_history_df["week_number"] >= woc_start) &
                (sales_history_df["week_number"] < W)
            ]
            _woc_sales_cache[W] = (
                woc_hist.groupby(["store_id", "product_id"])["units_sold"].mean().to_dict()
                if len(woc_hist) > 0 else {}
            )

    # Initialize independent working copies of store and warehouse stock
    store_inv = get_independent_store_inventory(starting_snapshot)
    warehouse_stock = dict(warehouse_opening_stock)

    weekly_results: List[WeeklySimulationResult] = []

    for W in range(config.start_week, config.end_week + 1):
        # Step 1: Starting State Accounting for Week W
        starting_store_units = sum(rec["current_stock"] for rec in store_inv.values())
        starting_store_cost = sum(
            rec["current_stock"] * products_by_id[rec["product_id"]]["cost_price"]
            for rec in store_inv.values()
        )
        wh_units_before = sum(warehouse_stock.values())
        wh_cost_before = sum(
            units * products_by_id[p_id]["cost_price"]
            for p_id, units in warehouse_stock.items()
        )

        # Step 2: Strict No-Leakage Historical Data Filter
        historical_sales_df = sales_history_df[sales_history_df["week_number"] < W].copy()

        # Step 3: Shared EOL Portfolio Resolution (Common Operating Environment)
        # Convert store_inv to record list for EOL engine
        inv_records_for_eol = list(store_inv.values())
        assessments, portfolio_resolution = run_eol_portfolio_assessment(
            stores=stores,
            products=products,
            inventory_records=inv_records_for_eol,
            sales_history_df=historical_sales_df,
            current_week=W,
            min_risk_level="MEDIUM",
        )

        # Identify high-risk EOL SKUs to block warehouse replenishment
        high_risk_eol_product_ids = {
            a.product_id for a in assessments if a.risk_level in ("HIGH", "CRITICAL")
        }

        # Step 4: Apply Shared EOL Transfers
        transferred_units, transfer_cost = apply_eol_transfers(
            store_inventory=store_inv,
            portfolio_resolution=portfolio_resolution,
            transfer_cost_per_unit=config.store_transfer_cost_per_unit,
        )

        # Step 5: Apply Shared EOL Markdowns
        markdowned_units, markdown_loss = apply_eol_markdowns(
            store_inventory=store_inv,
            eol_assessments=assessments,
            products_by_id=products_by_id,
        )

        # Step 6: Strategy-Specific Allocation Execution
        inv_records_for_alloc = list(store_inv.values())

        if strategy_name == "BASELINE":
            alloc_map = allocate_baseline_inventory(
                sales_history_df=sales_history_df,
                stores=stores,
                products=products,
                inventory_records=inv_records_for_alloc,
                planning_week=W,
                warehouse_stock=warehouse_stock,
                high_risk_eol_product_ids=high_risk_eol_product_ids,
                capital_budget_limit=config.capital_budget_limit,
                lookback_weeks=config.baseline_lookback_weeks,
            )
            units_allocated = sum(alloc_map.values())
            # For baseline, alloc_map already updated warehouse_stock inside baseline function
            for (s_id, p_id), qty in alloc_map.items():
                if (s_id, p_id) not in store_inv:
                    store_inv[(s_id, p_id)] = {
                        "store_id": s_id,
                        "product_id": p_id,
                        "current_stock": 0,
                        "in_transit_stock": 0,
                    }
                store_inv[(s_id, p_id)]["current_stock"] += qty

        elif strategy_name == "MOBIMART":
            # Pass filtered warehouse stock excluding blocked EOL products
            wh_avail_for_smart = {
                p_id: (0 if p_id in high_risk_eol_product_ids else qty)
                for p_id, qty in warehouse_stock.items()
            }
            smart_result = allocate_inventory(
                sales_history_df=historical_sales_df,
                stores=stores,
                products=products,
                inventory_records=inv_records_for_alloc,
                planning_week=W,
                warehouse_available=wh_avail_for_smart,
                capital_budget_limit=config.capital_budget_limit,
            )
            units_allocated = smart_result.total_units_allocated
            for rec in smart_result.recommendations:
                qty = rec.recommended_qty
                if qty <= 0:
                    continue
                s_id, p_id = rec.store_id, rec.product_id
                key = (s_id, p_id)
                warehouse_stock[p_id] -= qty
                store_inv[key]["current_stock"] += qty

        else:
            raise ValueError(f"Unknown strategy_name: {strategy_name}")

        allocation_cost = units_allocated * config.warehouse_allocation_cost_per_unit

        # Step 7: Realize Week W Customer Demand
        week_sales_df = sales_history_df[sales_history_df["week_number"] == W]
        fulfillment_data = fulfill_weekly_demand(store_inv, week_sales_df, products_by_id)

        ending_store_units = sum(rec["current_stock"] for rec in store_inv.values())
        ending_store_cost = sum(
            rec["current_stock"] * products_by_id[rec["product_id"]]["cost_price"]
            for rec in store_inv.values()
        )

        # Step 8: Strict Inventory Conservation Identity Audit
        verify_inventory_conservation(
            starting_store_units=starting_store_units,
            allocated_units=units_allocated,
            fulfilled_units=fulfillment_data["fulfilled_units"],
            ending_store_units=ending_store_units,
        )

        # Step 9: Weekly Metrics Calculation
        dead_stock_units = calculate_dead_stock_units(
            store_inventory=store_inv,
            sales_history_df=sales_history_df,
            current_week=W,
            lookback_weeks=config.dead_stock_lookback_weeks,
            _precomputed_sales_by_pair=_dead_stock_sales_cache.get(W),
        )

        # Average WoC across active positions (use precomputed cache)
        woc_list: List[float] = []
        sales_recent = _woc_sales_cache.get(W, {})

        for (s_id, p_id), inv_rec in store_inv.items():
            stock = inv_rec["current_stock"]
            avg_d = sales_recent.get((s_id, p_id), 0.5)
            woc = stock / max(0.1, avg_d)
            woc_list.append(woc)

        avg_woc_wk = float(np.mean(woc_list)) if woc_list else 0.0

        wk_res = WeeklySimulationResult(
            week_number=W,
            strategy_name=strategy_name,
            starting_store_units=starting_store_units,
            starting_store_cost=round(starting_store_cost, 2),
            ending_store_units=ending_store_units,
            ending_store_cost=round(ending_store_cost, 2),
            warehouse_units=sum(warehouse_stock.values()),
            warehouse_cost=round(
                sum(qty * products_by_id[p_id]["cost_price"] for p_id, qty in warehouse_stock.items()), 2
            ),
            units_allocated=units_allocated,
            allocation_cost=round(allocation_cost, 2),
            transferred_units=transferred_units,
            transfer_cost=round(transfer_cost, 2),
            markdowned_units=markdowned_units,
            markdown_loss=round(markdown_loss, 2),
            demand_units=fulfillment_data["demand_units"],
            fulfilled_units=fulfillment_data["fulfilled_units"],
            lost_sales_units=fulfillment_data["lost_sales_units"],
            lost_sales_value=fulfillment_data["lost_sales_value"],
            stockout_observations=fulfillment_data["stockout_observations"],
            positive_demand_observations=fulfillment_data["positive_demand_observations"],
            revenue=fulfillment_data["revenue"],
            gross_margin=fulfillment_data["gross_margin"],
            cogs=fulfillment_data["cogs"],
            dead_stock_units=dead_stock_units,
            average_weeks_of_cover=round(avg_woc_wk, 2),
        )
        weekly_results.append(wk_res)

    # Step 10: Aggregate Simulation Metrics
    aggregated = aggregate_simulation_metrics(weekly_results, config)
    elapsed = time.time() - start_time

    return SimulationRunResult(
        strategy_name=strategy_name,
        config=config,
        starting_snapshot=starting_snapshot,
        weekly_results=weekly_results,
        stockout_rate=aggregated["stockout_rate"],
        average_weeks_of_cover=aggregated["average_weeks_of_cover"],
        dead_stock_pct=aggregated["dead_stock_pct"],
        actual_markdown_loss=aggregated["actual_markdown_loss"],
        capital_turns=aggregated["capital_turns"],
        total_revenue=aggregated["total_revenue"],
        total_gross_margin=aggregated["total_gross_margin"],
        total_cogs=aggregated["total_cogs"],
        total_fulfilled_units=aggregated["total_fulfilled_units"],
        total_lost_sales_units=aggregated["total_lost_sales_units"],
        total_lost_sales_value=aggregated["total_lost_sales_value"],
        total_transferred_units=aggregated["total_transferred_units"],
        total_transfer_cost=aggregated["total_transfer_cost"],
        total_allocated_units=aggregated["total_allocated_units"],
        total_allocation_cost=aggregated["total_allocation_cost"],
        total_markdowned_units=aggregated["total_markdowned_units"],
        average_inventory_cost=aggregated["average_inventory_cost"],
        ending_inventory_cost=aggregated["ending_inventory_cost"],
        service_level_pct=aggregated["service_level_pct"],
        runtime_seconds=round(elapsed, 2),
    )
