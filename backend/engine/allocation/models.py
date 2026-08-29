"""
Structured Data Models for Allocation & Financial Explanation Engine.
Provides strong type safety and explicit fields for forecasts, inventory metrics,
financial impact, candidates, recommendations, and allocation run results.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class ForecastResult:
    store_id: str
    product_id: str
    forecast_weekly_demand: float
    recent_sales_velocity: float
    rolling_avg: float
    trend_factor: float
    seasonal_factor: float
    lifecycle_factor: float
    affinity_factor: float
    confidence: float

@dataclass
class InventoryMetrics:
    store_id: str
    product_id: str
    current_stock: int
    in_transit_stock: int
    projected_stock: int
    weeks_of_cover: float
    projected_weeks_of_cover: float
    inventory_value: float
    stockout_risk_score: float
    potential_lost_sales_units: float

@dataclass
class FinancialImpact:
    store_id: str
    product_id: str
    unit_cost: float
    unit_retail: float
    unit_margin: float
    expected_incremental_margin: float
    avoided_goodwill_benefit: float
    allocation_cost: float
    markdown_risk_cost: float
    net_marginal_value: float

    @property
    def expected_avoided_stockout_loss(self) -> float:
        """Backward compatibility alias for avoided_goodwill_benefit."""
        return self.avoided_goodwill_benefit

@dataclass
class AllocationCandidate:
    store_id: str
    product_id: str
    unit_number: int
    marginal_value: float
    unit_cost: float
    forecast: ForecastResult
    metrics: InventoryMetrics
    financials: FinancialImpact

@dataclass
class AllocationRecommendation:
    recommendation_id: str
    planning_week: int
    store_id: str
    product_id: str
    product_name: str
    recommended_qty: int
    current_stock: int
    projected_stock: int
    forecast_weekly_demand: float
    current_woc: float
    projected_woc: float
    unit_marginal_value: float
    total_net_benefit: float
    total_avoided_goodwill_benefit: float
    total_margin_contribution: float
    total_allocation_cost: float
    reason_code: str
    headline: str
    explanation_text: str
    explanation_json: Dict[str, Any]

    @property
    def total_avoided_stockout_loss(self) -> float:
        """Backward compatibility alias for total_avoided_goodwill_benefit."""
        return self.total_avoided_goodwill_benefit

@dataclass
class AllocationRunResult:
    run_id: str
    planning_week: int
    initial_capital_deployed: float
    new_capital_allocated: float
    resulting_capital_deployed: float
    budget_limit: float
    capital_headroom: float
    utilization_pct: float
    total_units_allocated: int
    total_expected_net_benefit: float
    recommendations: List[AllocationRecommendation] = field(default_factory=list)
