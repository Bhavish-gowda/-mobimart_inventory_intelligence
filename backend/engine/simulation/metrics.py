"""
Evaluation & Scorecard Metrics Engine for MobiMart Simulator.
Implements stockout rate, weeks of cover, dead stock %, actual markdown loss,
and capital turns (COGS / Avg Inventory Cost) per Correction 3.
"""

from typing import Dict, List, Any, Optional, Tuple
import pandas as pd
import numpy as np

from backend.engine.simulation.models import WeeklySimulationResult, SimulationRunResult, SimulationConfig

def calculate_dead_stock_units(
    store_inventory: Dict,
    sales_history_df: pd.DataFrame,
    current_week: int,
    lookback_weeks: int = 4,
    _precomputed_sales_by_pair: Optional[Dict] = None,
) -> int:
    """
    Calculate inventory units sitting in positions with 0 sales over previous lookback_weeks.
    Accepts an optional pre-computed sales_by_pair dict to avoid repeated DataFrame groupby.
    """
    if current_week <= 1:
        return 0

    if _precomputed_sales_by_pair is not None:
        sales_by_pair = _precomputed_sales_by_pair
    else:
        start_wk = max(1, current_week - lookback_weeks)
        end_wk = max(1, current_week - 1)
        hist_df = sales_history_df[
            (sales_history_df["week_number"] >= start_wk) &
            (sales_history_df["week_number"] <= end_wk)
        ]
        sales_by_pair = hist_df.groupby(["store_id", "product_id"])["units_sold"].sum().to_dict()

    dead_units = 0
    for (s_id, p_id), inv_rec in store_inventory.items():
        stock = inv_rec["current_stock"]
        if stock <= 0:
            continue
        sales = sales_by_pair.get((s_id, p_id), 0)
        if sales <= 0:
            dead_units += stock

    return dead_units

def aggregate_simulation_metrics(
    weekly_results: List[WeeklySimulationResult],
    config: SimulationConfig,
) -> Dict[str, Any]:
    """
    Aggregate weekly simulation results into final run metrics.
    Capital Turns = Total COGS / Average Inventory Cost (Correction 3).
    """
    if not weekly_results:
        return {}

    num_weeks = len(weekly_results)

    total_stockout_obs = sum(r.stockout_observations for r in weekly_results)
    total_pos_demand_obs = sum(r.positive_demand_observations for r in weekly_results)

    stockout_rate = (total_stockout_obs / float(total_pos_demand_obs)) * 100.0 if total_pos_demand_obs > 0 else 0.0

    avg_woc = sum(r.average_weeks_of_cover for r in weekly_results) / float(num_weeks)

    ending_store_units = weekly_results[-1].ending_store_units
    last_dead_stock_units = weekly_results[-1].dead_stock_units
    dead_stock_pct = (last_dead_stock_units / float(ending_store_units)) * 100.0 if ending_store_units > 0 else 0.0

    total_markdown_loss = sum(r.markdown_loss for r in weekly_results)
    total_cogs = sum(r.cogs for r in weekly_results)
    avg_inventory_cost = sum(r.ending_store_cost for r in weekly_results) / float(num_weeks)

    # Correction 3: Capital Turns = COGS / Average Inventory Cost
    capital_turns = (total_cogs / avg_inventory_cost) if avg_inventory_cost > 0 else 0.0

    total_revenue = sum(r.revenue for r in weekly_results)
    total_gross_margin = sum(r.gross_margin for r in weekly_results)
    total_fulfilled = sum(r.fulfilled_units for r in weekly_results)
    total_demand = sum(r.demand_units for r in weekly_results)
    total_lost_units = sum(r.lost_sales_units for r in weekly_results)
    total_lost_val = sum(r.lost_sales_value for r in weekly_results)
    total_transferred = sum(r.transferred_units for r in weekly_results)
    total_transfer_cost = sum(r.transfer_cost for r in weekly_results)
    total_allocated = sum(r.units_allocated for r in weekly_results)
    total_allocation_cost = sum(r.allocation_cost for r in weekly_results)
    total_markdowned = sum(r.markdowned_units for r in weekly_results)
    service_level_pct = (total_fulfilled / float(total_demand)) * 100.0 if total_demand > 0 else 0.0

    return {
        "stockout_rate": round(stockout_rate, 2),
        "average_weeks_of_cover": round(avg_woc, 2),
        "dead_stock_pct": round(dead_stock_pct, 2),
        "actual_markdown_loss": round(total_markdown_loss, 2),
        "capital_turns": round(capital_turns, 2),
        "total_revenue": round(total_revenue, 2),
        "total_gross_margin": round(total_gross_margin, 2),
        "total_cogs": round(total_cogs, 2),
        "total_fulfilled_units": total_fulfilled,
        "total_lost_sales_units": total_lost_units,
        "total_lost_sales_value": round(total_lost_val, 2),
        "total_transferred_units": total_transferred,
        "total_transfer_cost": round(total_transfer_cost, 2),
        "total_allocated_units": total_allocated,
        "total_allocation_cost": round(total_allocation_cost, 2),
        "total_markdowned_units": total_markdowned,
        "average_inventory_cost": round(avg_inventory_cost, 2),
        "ending_inventory_cost": round(weekly_results[-1].ending_store_cost, 2),
        "service_level_pct": round(service_level_pct, 2),
    }
