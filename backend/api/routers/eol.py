"""
EOL Risk & Portfolio Transfer API Router.
"""

from typing import Optional, List
import math
from fastapi import APIRouter, Query
from backend.api.schemas.eol import (
    EOLAssessRequest,
    EOLRiskAssessmentSchema,
    EOLRiskPortfolioResponse,
    PortfolioTransferResolutionSchema,
    EOLTransferRouteSchema,
    EOLActionOptionSchema,
)
from backend.api.services.eol_service import (
    get_eol_risk_portfolio,
    assess_single_eol_position,
)

router = APIRouter(tags=["EOL Risk & Transfers"])

def _nan_to_none(value):
    """Convert NaN float values (produced by pandas/numpy) to None for Pydantic safety."""
    if value is None:
        return None
    try:
        if isinstance(value, float) and math.isnan(value):
            return None
    except (TypeError, ValueError):
        pass
    return value

def _to_action_schema(opt) -> EOLActionOptionSchema:
    return EOLActionOptionSchema(
        action=opt.action,
        expected_cost=opt.expected_cost,
        expected_recovery=opt.expected_recovery,
        net_financial_loss=opt.net_financial_loss,
        units_affected=opt.units_affected,
        target_store_id=opt.target_store_id,
        assumptions=opt.assumptions,
        explanation=opt.explanation,
    )

def _to_assessment_schema(a) -> EOLRiskAssessmentSchema:
    return EOLRiskAssessmentSchema(
        assessment_id=a.assessment_id,
        store_id=a.store_id,
        product_id=a.product_id,
        product_name=a.product_name,
        lifecycle_stage=a.lifecycle_stage,
        risk_score=a.risk_score,
        risk_level=a.risk_level,
        inventory_units=a.inventory_units,
        inventory_value=a.inventory_value,
        weeks_of_cover=a.weeks_of_cover,
        successor_id=_nan_to_none(a.successor_id),
        successor_confidence=_nan_to_none(a.successor_confidence),
        weeks_to_successor=_nan_to_none(a.weeks_to_successor),
        weeks_to_eol=_nan_to_none(a.weeks_to_eol),
        risk_factors=a.risk_factors,
        markdown_option=_to_action_schema(a.markdown_option),
        transfer_option=_to_action_schema(a.transfer_option),
        hold_option=_to_action_schema(a.hold_option),
        recommended_action=a.recommended_action,
        expected_financial_impact=a.expected_financial_impact,
        explanation=a.explanation,
    )

@router.get(
    "/eol/risk",
    response_model=EOLRiskPortfolioResponse,
    summary="Get EOL Portfolio Risk Assessments & Capacity Resolution",
    description="Evaluates late-lifecycle SKU risk across chain and resolves transfer capacity ledgers.",
)
def get_eol_risk(
    current_week: int = Query(24, ge=1, le=52, description="Current week number", examples=[24]),
    min_risk_level: str = Query("MEDIUM", description="Minimum risk level filter (MEDIUM, HIGH, CRITICAL)", examples=["MEDIUM"]),
) -> EOLRiskPortfolioResponse:
    assessments, resolution = get_eol_risk_portfolio(current_week=current_week, min_risk_level=min_risk_level)

    app_routes = [
        EOLTransferRouteSchema(
            source_store_id=r.source_store_id,
            destination_store_id=r.destination_store_id,
            product_id=r.product_id,
            requested_units=r.requested_units,
            approved_units=r.approved_units,
            source_excess_units=r.source_excess_units,
            destination_shortfall_units=r.destination_shortfall_units,
            expected_cost=r.expected_cost,
            expected_loss=r.expected_loss,
            savings_vs_hold=r.savings_vs_hold,
            status=r.status,
            rejection_reason=r.rejection_reason,
        )
        for r in resolution.approved_routes
    ]

    rej_routes = [
        EOLTransferRouteSchema(
            source_store_id=r.source_store_id,
            destination_store_id=r.destination_store_id,
            product_id=r.product_id,
            requested_units=r.requested_units,
            approved_units=r.approved_units,
            source_excess_units=r.source_excess_units,
            destination_shortfall_units=r.destination_shortfall_units,
            expected_cost=r.expected_cost,
            expected_loss=r.expected_loss,
            savings_vs_hold=r.savings_vs_hold,
            status=r.status,
            rejection_reason=r.rejection_reason,
        )
        for r in resolution.rejected_routes
    ]

    res_schema = PortfolioTransferResolutionSchema(
        approved_routes=app_routes,
        rejected_routes=rej_routes,
        candidate_transfer_opportunity=resolution.candidate_transfer_opportunity,
        approved_transfer_opportunity=resolution.approved_transfer_opportunity,
        source_capacity_ledger=resolution.source_capacity_ledger,
        destination_capacity_ledger=resolution.destination_capacity_ledger,
    )

    return EOLRiskPortfolioResponse(
        current_week=current_week,
        min_risk_level=min_risk_level,
        assessments_count=len(assessments),
        assessments=[_to_assessment_schema(a) for a in assessments],
        portfolio_resolution=res_schema,
    )

@router.post(
    "/eol/assess",
    response_model=Optional[EOLRiskAssessmentSchema],
    summary="Assess Single Store-Product EOL Risk Position",
    description="Evaluate Markdown, Transfer, and Hold economics for a single store-product position.",
)
def assess_eol_position(request: EOLAssessRequest) -> Optional[EOLRiskAssessmentSchema]:
    assessment = assess_single_eol_position(
        store_id=request.store_id,
        product_id=request.product_id,
        current_week=request.current_week,
    )
    if not assessment:
        return None
    return _to_assessment_schema(assessment)
