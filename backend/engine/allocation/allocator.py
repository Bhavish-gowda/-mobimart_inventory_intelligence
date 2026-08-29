"""
Constrained Greedy Allocation Engine for MobiMart.
Optimizes weekly store-product stock allocations under a strict ₹4 Crore (₹4,00,00,000)
chain-wide capital budget limit and finite warehouse inventory availability.

Algorithm:
1. Forecast demand for all (store, product) pairs using historical sales up to current_week - 1.
2. Evaluate candidate marginal unit allocations for each pair.
3. Calculate Net Marginal Value (Expected Margin + Avoided Goodwill Benefit - Allocation Cost - Risk).
4. Filter out any candidates with Net Marginal Value <= 0 or projected WoC > 8.0.
5. Sort candidate unit queue by Net Marginal Value in descending order.
6. Iteratively allocate unit by unit while Total Deployed Capital <= ₹4,00,00,000 and Warehouse Stock > 0.
7. Aggregate allocations into structured AllocationRecommendation objects.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd

from backend.engine.allocation.models import (
    ForecastResult,
    InventoryMetrics,
    FinancialImpact,
    AllocationCandidate,
    AllocationRecommendation,
    AllocationRunResult,
)
from backend.engine.allocation.config import (
    MAX_CAPITAL_BUDGET,
    MAX_ALLOWABLE_WEEKS_OF_COVER,
    WAREHOUSE_ALLOCATION_COST_PER_UNIT,
)
from backend.engine.allocation.forecast import forecast_weekly_demand
from backend.engine.allocation.inventory_metrics import calculate_inventory_metrics
from backend.engine.allocation.financials import calculate_financial_impact
from backend.engine.allocation.explanations import generate_financial_explanation

def allocate_inventory(
    sales_history_df: pd.DataFrame,
    stores: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    inventory_records: List[Dict[str, Any]],
    planning_week: int,
    warehouse_available: Optional[Dict[str, int]] = None,
    capital_budget_limit: float = MAX_CAPITAL_BUDGET,
) -> AllocationRunResult:
    """
    Execute constrained greedy allocation run for planning_week.
    """
    stores_by_id = {s["id"]: s for s in stores}
    products_by_id = {p["id"]: p for p in products}

    # Maps for operational tracking during allocation loop
    inv_by_key: Dict[Tuple[str, str], Dict[str, Any]] = {
        (inv["store_id"], inv["product_id"]): dict(inv) for inv in inventory_records
    }

    # Initial warehouse availability (default: 50 units per SKU if not specified or placeholder)
    default_wh_stock = {p["id"]: 50 for p in products}
    if warehouse_available is None:
        warehouse_stock = dict(default_wh_stock)
    else:
        valid_overrides = {k: v for k, v in warehouse_available.items() if k in products_by_id}
        if not valid_overrides:
            warehouse_stock = dict(default_wh_stock)
        else:
            warehouse_stock = {p["id"]: warehouse_available.get(p["id"], default_wh_stock[p["id"]]) for p in products}

    # Initial Capital Deployed across all stores (Current Stock * Cost Price)
    initial_capital_deployed = 0.0
    for key, inv in inv_by_key.items():
        cost = products_by_id[key[1]]["cost_price"]
        stock = inv.get("current_stock", 0) + inv.get("in_transit_stock", 0)
        initial_capital_deployed += stock * cost

    # Effective budget limit for NEW capital allocation
    if capital_budget_limit >= initial_capital_deployed:
        effective_new_capital_budget = capital_budget_limit - initial_capital_deployed
    else:
        effective_new_capital_budget = capital_budget_limit

    # Step 1 & 2: Build candidate queue of marginal unit allocations
    candidates: List[AllocationCandidate] = []

    for store in stores:
        for product in products:
            key = (store["id"], product["id"])
            inv = inv_by_key.get(key, {"store_id": store["id"], "product_id": product["id"], "current_stock": 0, "in_transit_stock": 0})
            
            # Forecast weekly demand (Zero future leakage!)
            fc = forecast_weekly_demand(sales_history_df, store, product, planning_week)
            
            # Evaluate up to 15 candidate units per store-product pair
            max_units_eval = min(15, max(1, int(np.ceil(fc.forecast_weekly_demand * 2.5))))
            
            for unit_idx in range(1, max_units_eval + 1):
                metrics = calculate_inventory_metrics(inv, fc, product, additional_units=unit_idx)
                
                # Reject if projected WoC exceeds max allowable cover
                if metrics.projected_weeks_of_cover > MAX_ALLOWABLE_WEEKS_OF_COVER:
                    break

                fin = calculate_financial_impact(product, fc, metrics, additional_unit_index=unit_idx)
                
                # Reject if marginal value <= 0
                if fin.net_marginal_value <= 0.0:
                    break

                candidate = AllocationCandidate(
                    store_id=store["id"],
                    product_id=product["id"],
                    unit_number=unit_idx,
                    marginal_value=fin.net_marginal_value,
                    unit_cost=fin.unit_cost,
                    forecast=fc,
                    metrics=metrics,
                    financials=fin,
                )
                candidates.append(candidate)

    # Step 3: Sort candidate queue in descending order of marginal value
    candidates.sort(key=lambda c: c.marginal_value, reverse=True)

    # Step 4: Greedy Allocation Execution
    allocated_units_by_key: Dict[Tuple[str, str], int] = {}
    new_capital_allocated = 0.0

    for cand in candidates:
        key = (cand.store_id, cand.product_id)
        prod_id = cand.product_id

        # Check warehouse stock availability
        if warehouse_stock.get(prod_id, 0) <= 0:
            continue

        # Check capital budget constraint
        if new_capital_allocated + cand.unit_cost > effective_new_capital_budget:
            continue  # Capital budget bound!

        # Check sequential unit ordering (must allocate unit 1 before unit 2 for same pair)
        current_alloc = allocated_units_by_key.get(key, 0)
        if cand.unit_number != current_alloc + 1:
            continue

        # Commit unit allocation!
        allocated_units_by_key[key] = current_alloc + 1
        warehouse_stock[prod_id] -= 1
        new_capital_allocated += cand.unit_cost

    # Step 5: Build final AllocationRecommendation objects
    recommendations: List[AllocationRecommendation] = []
    rec_counter = 1
    total_net_benefit = 0.0

    for key, qty in allocated_units_by_key.items():
        if qty <= 0:
            continue

        store_id, product_id = key
        store = stores_by_id[store_id]
        product = products_by_id[product_id]
        inv = inv_by_key[key]

        fc = forecast_weekly_demand(sales_history_df, store, product, planning_week)
        metrics = calculate_inventory_metrics(inv, fc, product, additional_units=qty)

        # Calculate total accumulated financial metrics for qty units
        total_avoided_goodwill = 0.0
        total_margin_contrib = 0.0
        total_cost = qty * WAREHOUSE_ALLOCATION_COST_PER_UNIT

        for unit_idx in range(1, qty + 1):
            m_unit = calculate_inventory_metrics(inv, fc, product, additional_units=unit_idx)
            fin_unit = calculate_financial_impact(product, fc, m_unit, additional_unit_index=unit_idx)
            total_avoided_goodwill += fin_unit.avoided_goodwill_benefit
            total_margin_contrib += fin_unit.expected_incremental_margin

        tot_net = total_avoided_goodwill + total_margin_contrib - total_cost
        total_net_benefit += tot_net

        exp_data = generate_financial_explanation(
            store=store,
            product=product,
            recommended_qty=qty,
            current_stock=metrics.current_stock,
            projected_stock=metrics.projected_stock,
            forecast_demand=fc.forecast_weekly_demand,
            current_woc=metrics.weeks_of_cover,
            projected_woc=metrics.projected_weeks_of_cover,
            net_benefit=tot_net,
            avoided_goodwill_benefit=total_avoided_goodwill,
            margin_contribution=total_margin_contrib,
            allocation_cost=total_cost,
        )

        rec = AllocationRecommendation(
            recommendation_id=f"REC_W{planning_week:02d}_{rec_counter:04d}",
            planning_week=planning_week,
            store_id=store_id,
            product_id=product_id,
            product_name=product.get("model_name", product_id),
            recommended_qty=qty,
            current_stock=metrics.current_stock,
            projected_stock=metrics.projected_stock,
            forecast_weekly_demand=round(fc.forecast_weekly_demand, 2),
            current_woc=metrics.weeks_of_cover,
            projected_woc=metrics.projected_weeks_of_cover,
            unit_marginal_value=round(tot_net / qty, 2),
            total_net_benefit=round(tot_net, 2),
            total_avoided_goodwill_benefit=round(total_avoided_goodwill, 2),
            total_margin_contribution=round(total_margin_contrib, 2),
            total_allocation_cost=round(total_cost, 2),
            reason_code=exp_data["reason_code"],
            headline=exp_data["headline"],
            explanation_text=exp_data["explanation_text"],
            explanation_json=exp_data,
        )
        recommendations.append(rec)
        rec_counter += 1

    # Sort recommendations by total net benefit
    recommendations.sort(key=lambda r: r.total_net_benefit, reverse=True)

    resulting_capital_deployed = initial_capital_deployed + new_capital_allocated
    headroom = max(0.0, effective_new_capital_budget - new_capital_allocated)
    utilization_pct = (new_capital_allocated / effective_new_capital_budget * 100.0) if effective_new_capital_budget > 0 else 0.0
    total_units_alloc = sum(r.recommended_qty for r in recommendations)

    return AllocationRunResult(
        run_id=f"RUN_W{planning_week:02d}_SMART",
        planning_week=planning_week,
        initial_capital_deployed=round(initial_capital_deployed, 2),
        new_capital_allocated=round(new_capital_allocated, 2),
        resulting_capital_deployed=round(resulting_capital_deployed, 2),
        budget_limit=round(capital_budget_limit, 2),
        capital_headroom=round(headroom, 2),
        utilization_pct=round(utilization_pct, 2),
        total_units_allocated=total_units_alloc,
        total_expected_net_benefit=round(total_net_benefit, 2),
        recommendations=recommendations,
    )
