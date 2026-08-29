"""
Pydantic Schemas for Allocation Endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class AllocationRunRequest(BaseModel):
    planning_week: int = Field(..., ge=1, le=52, description="Planning week W", example=24)
    capital_budget_limit: Optional[float] = Field(40000000.0, description="Capital budget limit in INR", example=40000000.0)
    warehouse_available: Optional[Dict[str, int]] = Field(None, description="Optional warehouse stock override dict per SKU", json_schema_extra={"example": {"PROD_001": 50, "PROD_002": 50}})

class AllocationRecommendationSchema(BaseModel):
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

class AllocationRunResponse(BaseModel):
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
    recommendations: List[AllocationRecommendationSchema]
