"""
EOL Inventory Summary Engine for MobiMart.
Aggregates individual EOL risk assessments into a portfolio-wide summary
for dashboard use and executive reporting.
"""

from typing import List, Dict
from backend.engine.eol.models import EOLInventorySummary, EOLRiskAssessment, PortfolioTransferResolution


def generate_eol_summary(
    assessments: List[EOLRiskAssessment],
    resolution: PortfolioTransferResolution | None = None,
) -> EOLInventorySummary:
    """
    Aggregate all EOL risk assessments into a portfolio-wide summary.
    """
    if not assessments:
        return EOLInventorySummary(
            total_eol_risk_units=0,
            total_inventory_value_at_risk=0.0,
            risky_sku_count=0,
            risky_store_count=0,
            markdown_exposure=0.0,
            transfer_opportunity=0.0,
            hold_exposure=0.0,
            recommended_markdown_units=0,
            recommended_markdown_cost=0.0,
            recommended_transfer_units=0,
            recommended_transfer_cost=0.0,
            recommended_hold_units=0,
            recommended_hold_cost=0.0,
            action_breakdown={},
        )

    total_units = sum(a.inventory_units for a in assessments)
    total_value = sum(a.inventory_value for a in assessments)
    unique_skus = len({a.product_id for a in assessments})
    unique_stores = len({a.store_id for a in assessments})

    markdown_exposure = sum(
        a.markdown_option.net_financial_loss
        for a in assessments
        if a.markdown_option.net_financial_loss != float("inf")
    )
    hold_exposure = sum(
        a.hold_option.net_financial_loss
        for a in assessments
        if a.hold_option.net_financial_loss != float("inf")
    )

    # With a resolution, only portfolio-approved routes count as opportunity.
    candidate_transfer_opportunity = 0.0
    approved_transfer_opportunity = 0.0
    approved_transfer_units = 0
    approved_transfer_cost = 0.0
    approved_transfer_routes = 0
    rejected_destination = 0
    rejected_source = 0
    if resolution is not None:
        candidate_transfer_opportunity = resolution.candidate_transfer_opportunity
        approved_transfer_opportunity = sum(
            max(0.0, a.hold_option.net_financial_loss - a.transfer_option.net_financial_loss)
            for a in assessments
            if a.recommended_action == "TRANSFER"
        )
        approved_transfer_units = sum(route.approved_units for route in resolution.approved_routes)
        approved_transfer_cost = sum(route.approved_units * 500.0 for route in resolution.approved_routes)
        approved_transfer_routes = len(resolution.approved_routes)
        rejected_destination = sum(
            r.rejection_reason == "DESTINATION_CAPACITY" for r in resolution.rejected_routes
        )
        rejected_source = sum(
            r.rejection_reason == "SOURCE_CAPACITY" for r in resolution.rejected_routes
        )
    else:
        approved_transfer_opportunity = sum(
            max(0.0, a.hold_option.net_financial_loss - a.transfer_option.net_financial_loss)
            for a in assessments
            if a.transfer_option.net_financial_loss != float("inf") and a.transfer_option.units_affected > 0
        )

    # Recommended action aggregation
    action_breakdown: Dict[str, int] = {"MARKDOWN": 0, "TRANSFER": 0, "HOLD": 0}
    recommended_markdown_units = 0
    recommended_markdown_cost = 0.0
    recommended_transfer_units = 0
    recommended_transfer_cost = 0.0
    recommended_hold_units = 0
    recommended_hold_cost = 0.0

    for a in assessments:
        action = a.recommended_action
        action_breakdown[action] = action_breakdown.get(action, 0) + 1

        if action == "MARKDOWN":
            recommended_markdown_units += a.inventory_units
            recommended_markdown_cost += a.markdown_option.net_financial_loss
        elif action == "TRANSFER":
            recommended_transfer_units += a.transfer_option.units_affected
            recommended_transfer_cost += a.transfer_option.expected_cost
        elif action == "HOLD":
            recommended_hold_units += a.inventory_units
            recommended_hold_cost += a.hold_option.net_financial_loss

    return EOLInventorySummary(
        total_eol_risk_units=total_units,
        total_inventory_value_at_risk=round(total_value, 2),
        risky_sku_count=unique_skus,
        risky_store_count=unique_stores,
        markdown_exposure=round(markdown_exposure, 2),
        transfer_opportunity=round(approved_transfer_opportunity, 2),
        hold_exposure=round(hold_exposure, 2),
        recommended_markdown_units=recommended_markdown_units,
        recommended_markdown_cost=round(recommended_markdown_cost, 2),
        recommended_transfer_units=recommended_transfer_units,
        recommended_transfer_cost=round(recommended_transfer_cost, 2),
        recommended_hold_units=recommended_hold_units,
        recommended_hold_cost=round(recommended_hold_cost, 2),
        action_breakdown=action_breakdown,
        candidate_transfer_opportunity=round(candidate_transfer_opportunity, 2),
        approved_transfer_opportunity=round(approved_transfer_opportunity, 2),
        approved_transfer_units=approved_transfer_units,
        approved_transfer_cost=round(approved_transfer_cost, 2),
        approved_transfer_routes=approved_transfer_routes,
        rejected_due_to_destination_capacity=rejected_destination,
        rejected_due_to_source_capacity=rejected_source,
    )
