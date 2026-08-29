"""Tests for deterministic, capacity-feasible EOL portfolio transfers."""

from backend.engine.eol.models import EOLActionOption, EOLRiskAssessment
from backend.engine.eol.portfolio import (
    apply_portfolio_transfer_resolution,
    resolve_portfolio_transfers,
)
from backend.engine.eol.summary import generate_eol_summary


def make_assessment(source, destination, product="P", source_excess=1, shortfall=1):
    markdown = EOLActionOption(
        action="MARKDOWN", expected_cost=0.0, expected_recovery=1500.0,
        net_financial_loss=1500.0, units_affected=2,
        assumptions={"markdown_pct": 0.5, "cost_price": 1000.0, "retail_price": 1500.0},
    )
    transfer = EOLActionOption(
        action="TRANSFER", expected_cost=500.0, expected_recovery=2000.0,
        net_financial_loss=1000.0, units_affected=1, target_store_id=destination,
        assumptions={"source_excess_units": source_excess, "destination_shortfall_units": shortfall},
    )
    hold = EOLActionOption(
        action="HOLD", expected_cost=0.0, expected_recovery=0.0,
        net_financial_loss=2000.0, units_affected=2,
    )
    return EOLRiskAssessment(
        assessment_id=f"{source}-{product}", store_id=source, product_id=product,
        product_name=product, lifecycle_stage="EOL", risk_score=80.0,
        risk_level="CRITICAL", inventory_units=2, inventory_value=2000.0,
        weeks_of_cover=10.0, successor_id=None, successor_confidence=0.0,
        weeks_to_successor=None, weeks_to_eol=2.0, risk_factors=[],
        markdown_option=markdown, transfer_option=transfer, hold_option=hold,
        recommended_action="TRANSFER", expected_financial_impact=1000.0, explanation="",
    )


def test_destination_shortfall_cannot_be_overcommitted():
    assessments = [make_assessment(source, "DEST") for source in ("A", "B", "C")]
    resolution = resolve_portfolio_transfers(assessments)
    assert sum(route.approved_units for route in resolution.approved_routes) == 1
    assert len(resolution.rejected_routes) == 2
    assert resolution.destination_capacity_ledger["P|DEST"]["remaining_shortfall"] == 0


def test_source_excess_cannot_be_overcommitted():
    assessments = [
        make_assessment("SOURCE", "DEST_A", source_excess=2, shortfall=2),
        make_assessment("SOURCE", "DEST_B", source_excess=2, shortfall=2),
    ]
    for assessment in assessments:
        assessment.transfer_option.units_affected = 2
    resolution = resolve_portfolio_transfers(assessments)
    assert sum(route.approved_units for route in resolution.approved_routes) == 2
    assert resolution.source_capacity_ledger["SOURCE|P"]["remaining_excess"] == 0


def test_portfolio_transfer_resolution_is_deterministic():
    assessments = [make_assessment(source, "DEST") for source in ("C", "A", "B")]
    first = resolve_portfolio_transfers(assessments)
    second = resolve_portfolio_transfers(assessments)
    assert first == second
    assert first.approved_routes[0].source_store_id == "A"


def test_approved_transfer_summary_uses_only_approved_transfers():
    assessments = [make_assessment(source, "DEST") for source in ("A", "B", "C")]
    resolution = resolve_portfolio_transfers(assessments)
    apply_portfolio_transfer_resolution(assessments, resolution)
    summary = generate_eol_summary(assessments, resolution)
    assert summary.candidate_transfer_opportunity == 3000.0
    assert summary.approved_transfer_opportunity == 1000.0
    assert summary.approved_transfer_units == 1
    assert summary.approved_transfer_routes == 1


def test_transfer_reduces_destination_shortfall_and_source_excess():
    assessment = make_assessment("SOURCE", "DEST", source_excess=2, shortfall=1)
    resolution = resolve_portfolio_transfers([assessment])
    assert resolution.destination_capacity_ledger["P|DEST"]["remaining_shortfall"] == 0
    assert resolution.source_capacity_ledger["SOURCE|P"]["remaining_excess"] == 1


def test_allocation_can_consume_residual_demand_only():
    """Structured plan exposes approved units needed for Phase 3C residual demand."""
    assessment = make_assessment("SOURCE", "DEST", source_excess=3, shortfall=3)
    assessment.transfer_option.units_affected = 3
    resolution = resolve_portfolio_transfers([assessment])
    approved_to_destination = sum(route.approved_units for route in resolution.approved_routes)
    destination_demand = 5
    assert max(0, destination_demand - approved_to_destination) == 2
