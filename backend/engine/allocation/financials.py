"""
Financial Explanation Model for MobiMart Allocation Engine.
Calculates rupee-denominated expected incremental margin, avoided goodwill benefit,
warehouse allocation costs, and net marginal financial value per unit.

GUARANTEES ZERO DOUBLE-COUNTING:
- Expected Gross Margin = Expected Fulfilled Units * Unit Gross Margin
- Avoided Goodwill Benefit = Incremental Prevented Unmet Demand * Goodwill Dissatisfaction Penalty
- Net Marginal Value = Expected Gross Margin + Avoided Goodwill Benefit - Allocation Cost - Markdown Risk Cost
"""

from typing import Dict, Any
import numpy as np
from backend.engine.allocation.models import FinancialImpact, ForecastResult, InventoryMetrics
from backend.engine.allocation.config import (
    WAREHOUSE_ALLOCATION_COST_PER_UNIT,
    GOODWILL_PENALTY_FACTORS,
)

def calculate_avoided_goodwill_benefit(product: Dict[str, Any], unmet_demand_units: float) -> float:
    """
    Calculate avoided goodwill dissatisfaction loss for unmet customer demand.
    Formula: UnmetDemand * (UnitMargin * GoodwillPenaltyFactor)
    
    GUARANTEES ZERO DOUBLE-COUNTING:
    - Gross margin earned on fulfilled sales is calculated separately in expected_incremental_margin.
    - Avoided goodwill benefit represents purely the non-margin customer dissatisfaction penalty.
    """
    if unmet_demand_units <= 0.0:
        return 0.0

    segment = product["segment"]
    unit_retail = float(product["retail_price"])
    unit_cost = float(product["cost_price"])
    unit_margin = unit_retail - unit_cost

    goodwill_factor = GOODWILL_PENALTY_FACTORS.get(segment, 0.10)
    goodwill_benefit_per_unit = unit_margin * goodwill_factor

    return float(max(0.0, unmet_demand_units * goodwill_benefit_per_unit))

def calculate_avoided_stockout_loss(product: Dict[str, Any], unmet_demand_units: float) -> float:
    """Backward-compatibility wrapper for calculate_avoided_goodwill_benefit."""
    return calculate_avoided_goodwill_benefit(product, unmet_demand_units)

def calculate_financial_impact(
    product: Dict[str, Any],
    forecast_result: ForecastResult,
    inventory_metrics: InventoryMetrics,
    additional_unit_index: int = 1,
) -> FinancialImpact:
    """
    Calculate marginal financial value of allocating ONE additional unit to store-product pair.
    
    Net Marginal Value = Expected Incremental Margin + Avoided Goodwill Benefit - Allocation Cost - Markdown Risk Cost
    """
    unit_cost = float(product["cost_price"])
    unit_retail = float(product["retail_price"])
    unit_margin = unit_retail - unit_cost
    stage = product.get("lifecycle_stage", "Peak")

    current_stock = inventory_metrics.current_stock
    demand = forecast_result.forecast_weekly_demand

    # Stock position before and after this single unit
    prior_stock = current_stock + additional_unit_index - 1
    new_stock = prior_stock + 1

    # Probability that this specific incremental unit will be sold
    if demand > prior_stock:
        sale_probability = min(1.0, demand - prior_stock)
    else:
        sale_probability = 0.0

    # 1. Expected Incremental Margin Contribution
    expected_margin = sale_probability * unit_margin

    # 2. Avoided Goodwill Benefit (Prevented Customer Dissatisfaction)
    unmet_demand_before = max(0.0, demand - prior_stock)
    unmet_demand_after = max(0.0, demand - new_stock)
    unmet_demand_delta = unmet_demand_before - unmet_demand_after

    avoided_goodwill = calculate_avoided_goodwill_benefit(product, unmet_demand_delta)

    # 3. Unit Warehouse Allocation Cost
    allocation_cost = WAREHOUSE_ALLOCATION_COST_PER_UNIT

    # 4. Markdown / Overstock Risk Cost
    woc_after = inventory_metrics.projected_weeks_of_cover
    markdown_risk = 0.0

    if stage in ["Decline", "EOL"] or woc_after > 5.0:
        markdown_pct = float(product.get("markdown_percentage", 0.20))
        risk_probability = max(0.10, (woc_after - 4.0) * 0.15)
        markdown_risk = unit_cost * markdown_pct * min(1.0, risk_probability)

    # Calculate Net Marginal Financial Value
    net_marginal_value = expected_margin + avoided_goodwill - allocation_cost - markdown_risk

    return FinancialImpact(
        store_id=inventory_metrics.store_id,
        product_id=inventory_metrics.product_id,
        unit_cost=round(unit_cost, 2),
        unit_retail=round(unit_retail, 2),
        unit_margin=round(unit_margin, 2),
        expected_incremental_margin=round(expected_margin, 2),
        avoided_goodwill_benefit=round(avoided_goodwill, 2),
        allocation_cost=round(allocation_cost, 2),
        markdown_risk_cost=round(markdown_risk, 2),
        net_marginal_value=round(net_marginal_value, 2),
    )
