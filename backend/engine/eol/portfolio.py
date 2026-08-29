"""Portfolio-level capacity resolution for individually evaluated EOL transfers."""

from typing import Dict, List, Tuple

from backend.engine.eol.config import STORE_TRANSFER_COST_PER_UNIT
from backend.engine.eol.explanations import generate_eol_explanation
from backend.engine.eol.models import (
    EOLActionOption,
    EOLRiskAssessment,
    EOLTransferRoute,
    PortfolioTransferResolution,
)


def _route_from_assessment(assessment: EOLRiskAssessment) -> EOLTransferRoute | None:
    """Create a portfolio candidate only when transfer already beats its alternatives."""
    option = assessment.transfer_option
    if (
        option.target_store_id is None
        or option.units_affected <= 0
        or option.net_financial_loss == float("inf")
        or assessment.recommended_action != "TRANSFER"
    ):
        return None

    assumptions = option.assumptions
    return EOLTransferRoute(
        source_store_id=assessment.store_id,
        destination_store_id=option.target_store_id,
        product_id=assessment.product_id,
        requested_units=option.units_affected,
        source_excess_units=int(assumptions["source_excess_units"]),
        destination_shortfall_units=int(assumptions["destination_shortfall_units"]),
        expected_cost=option.expected_cost,
        expected_loss=option.net_financial_loss,
        savings_vs_hold=max(0.0, assessment.hold_option.net_financial_loss - option.net_financial_loss),
        status="CANDIDATE",
    )


def resolve_portfolio_transfers(
    assessments: List[EOLRiskAssessment],
) -> PortfolioTransferResolution:
    """Resolve individually optimal transfer recommendations against shared capacity.

    Candidates are ordered by savings versus hold, savings per requested unit,
    then stable source, destination, and product identifiers.  The two ledgers
    ensure that no source releases more than its excess and no destination
    receives more than its calculated product shortfall.
    """
    candidates = [route for a in assessments if (route := _route_from_assessment(a))]
    candidates.sort(
        key=lambda r: (
            -r.savings_vs_hold,
            -(r.savings_vs_hold / r.requested_units),
            r.source_store_id,
            r.destination_store_id,
            r.product_id,
        )
    )

    source_ledger: Dict[Tuple[str, str], Dict[str, int]] = {}
    destination_ledger: Dict[Tuple[str, str], Dict[str, int]] = {}
    approved: List[EOLTransferRoute] = []
    rejected: List[EOLTransferRoute] = []

    for route in candidates:
        source_key = (route.source_store_id, route.product_id)
        destination_key = (route.product_id, route.destination_store_id)
        source_ledger.setdefault(source_key, {
            "initial_excess": route.source_excess_units,
            "approved_outgoing": 0,
            "remaining_excess": route.source_excess_units,
        })
        destination_ledger.setdefault(destination_key, {
            "initial_shortfall": route.destination_shortfall_units,
            "approved_incoming": 0,
            "remaining_shortfall": route.destination_shortfall_units,
        })

        source_remaining = source_ledger[source_key]["remaining_excess"]
        destination_remaining = destination_ledger[destination_key]["remaining_shortfall"]
        approved_units = min(route.requested_units, source_remaining, destination_remaining)

        if approved_units <= 0:
            reason = (
                "DESTINATION_CAPACITY" if destination_remaining <= 0
                else "SOURCE_CAPACITY"
            )
            rejected.append(EOLTransferRoute(
                **{**route.__dict__, "status": "REJECTED", "rejection_reason": reason}
            ))
            continue

        source_ledger[source_key]["approved_outgoing"] += approved_units
        source_ledger[source_key]["remaining_excess"] -= approved_units
        destination_ledger[destination_key]["approved_incoming"] += approved_units
        destination_ledger[destination_key]["remaining_shortfall"] -= approved_units
        approved.append(EOLTransferRoute(
            **{**route.__dict__, "status": "APPROVED", "approved_units": approved_units}
        ))

    stringify = lambda ledger: {
        f"{key[0]}|{key[1]}": value for key, value in ledger.items()
    }
    candidate_opportunity = sum(route.savings_vs_hold for route in candidates)
    approved_opportunity = sum(
        route.savings_vs_hold * (route.approved_units / route.requested_units)
        for route in approved
    )
    return PortfolioTransferResolution(
        approved_routes=approved,
        rejected_routes=rejected,
        candidate_transfer_opportunity=round(candidate_opportunity, 2),
        approved_transfer_opportunity=round(approved_opportunity, 2),
        source_capacity_ledger=stringify(source_ledger),
        destination_capacity_ledger=stringify(destination_ledger),
    )


def apply_portfolio_transfer_resolution(
    assessments: List[EOLRiskAssessment], resolution: PortfolioTransferResolution
) -> List[EOLRiskAssessment]:
    """Apply approved transfer quantities and reselect actions for constrained routes."""
    approved_by_source = {
        (route.source_store_id, route.product_id): route
        for route in resolution.approved_routes
    }
    constrained_sources = {
        (route.source_store_id, route.product_id)
        for route in resolution.approved_routes + resolution.rejected_routes
    }

    for assessment in assessments:
        key = (assessment.store_id, assessment.product_id)
        if key not in constrained_sources:
            continue

        approved = approved_by_source.get(key)
        if approved is None:
            assessment.transfer_option = EOLActionOption(
                action="TRANSFER", expected_cost=0.0, expected_recovery=0.0,
                net_financial_loss=float("inf"), units_affected=0,
                assumptions={"reason": "Rejected by portfolio capacity resolution"},
                explanation="TRANSFER option: Rejected by portfolio capacity resolution.",
            )
        else:
            quantity = approved.approved_units
            markdown_pct = float(assessment.markdown_option.assumptions["markdown_pct"])
            cost_price = float(assessment.markdown_option.assumptions["cost_price"])
            retail_price = float(assessment.markdown_option.assumptions["retail_price"])
            remaining = assessment.inventory_units - quantity
            logistics_cost = quantity * STORE_TRANSFER_COST_PER_UNIT
            remaining_markdown_loss = remaining * cost_price * markdown_pct
            transfer_loss = round(logistics_cost + remaining_markdown_loss, 2)
            assessment.transfer_option = EOLActionOption(
                action="TRANSFER", expected_cost=round(logistics_cost, 2),
                expected_recovery=round(quantity * retail_price + remaining * retail_price * (1 - markdown_pct), 2),
                net_financial_loss=transfer_loss, units_affected=quantity,
                target_store_id=approved.destination_store_id,
                assumptions={
                    "transfer_cost_per_unit": STORE_TRANSFER_COST_PER_UNIT,
                    "source_excess_units": approved.source_excess_units,
                    "destination_shortfall_units": approved.destination_shortfall_units,
                    "approved_by_portfolio": True,
                    "remaining_units": remaining,
                    "remaining_source_markdown_loss": round(remaining_markdown_loss, 2),
                },
                explanation=(
                    f"TRANSFER option: Portfolio-approved {quantity} units to "
                    f"{approved.destination_store_id} at ₹{STORE_TRANSFER_COST_PER_UNIT:.0f}/unit."
                ),
            )

        options = {
            "MARKDOWN": assessment.markdown_option.net_financial_loss,
            "TRANSFER": assessment.transfer_option.net_financial_loss,
            "HOLD": assessment.hold_option.net_financial_loss,
        }
        assessment.recommended_action = min(options, key=options.get)
        assessment.expected_financial_impact = round(options[assessment.recommended_action], 2)
        assessment.explanation = generate_eol_explanation(
            risk_level=assessment.risk_level, risk_score=assessment.risk_score,
            store_id=assessment.store_id, product_name=assessment.product_name,
            product_id=assessment.product_id, inventory_units=assessment.inventory_units,
            weeks_of_cover=assessment.weeks_of_cover, successor_id=assessment.successor_id,
            weeks_to_successor=assessment.weeks_to_successor,
            risk_factors=assessment.risk_factors,
            markdown_opt=assessment.markdown_option,
            transfer_opt=assessment.transfer_option, hold_opt=assessment.hold_option,
            recommended_action=assessment.recommended_action,
        )
    return assessments
