"""
Allocation Engine API Router.
"""

from fastapi import APIRouter
from backend.api.schemas.allocation import (
    AllocationRunRequest,
    AllocationRunResponse,
    AllocationRecommendationSchema,
)
from backend.api.services.allocation_service import run_allocation

router = APIRouter(tags=["Allocation"])

@router.post(
    "/allocation/run",
    response_model=AllocationRunResponse,
    summary="Run Constrained Greedy Allocation Engine",
    description="Execute constrained greedy stock allocation under ₹4 Crore budget cap and warehouse inventory limits for planning week W.",
)
def execute_allocation(request: AllocationRunRequest) -> AllocationRunResponse:
    res = run_allocation(
        planning_week=request.planning_week,
        capital_budget_limit=request.capital_budget_limit or 40000000.0,
        warehouse_available=request.warehouse_available,
    )

    recs = [
        AllocationRecommendationSchema(
            recommendation_id=r.recommendation_id,
            planning_week=r.planning_week,
            store_id=r.store_id,
            product_id=r.product_id,
            product_name=r.product_name,
            recommended_qty=r.recommended_qty,
            current_stock=r.current_stock,
            projected_stock=r.projected_stock,
            forecast_weekly_demand=r.forecast_weekly_demand,
            current_woc=r.current_woc,
            projected_woc=r.projected_woc,
            unit_marginal_value=r.unit_marginal_value,
            total_net_benefit=r.total_net_benefit,
            total_avoided_goodwill_benefit=r.total_avoided_goodwill_benefit,
            total_margin_contribution=r.total_margin_contribution,
            total_allocation_cost=r.total_allocation_cost,
            reason_code=r.reason_code,
            headline=r.headline,
            explanation_text=r.explanation_text,
            explanation_json=r.explanation_json,
        )
        for r in res.recommendations
    ]

    return AllocationRunResponse(
        run_id=res.run_id,
        planning_week=res.planning_week,
        initial_capital_deployed=res.initial_capital_deployed,
        new_capital_allocated=res.new_capital_allocated,
        resulting_capital_deployed=res.resulting_capital_deployed,
        budget_limit=res.budget_limit,
        capital_headroom=res.capital_headroom,
        utilization_pct=res.utilization_pct,
        total_units_allocated=res.total_units_allocated,
        total_expected_net_benefit=res.total_expected_net_benefit,
        recommendations=recs,
    )
