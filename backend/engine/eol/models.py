"""
Structured Data Models for End-of-Life (EOL) Risk Engine.
Provides strong type safety and explicit schemas for EOL action options,
risk assessments, and portfolio-wide EOL inventory summaries.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class EOLActionOption:
    """
    Represents a specific evaluated action option (MARKDOWN, TRANSFER, or HOLD).
    """
    action: str  # "MARKDOWN", "TRANSFER", "HOLD"
    expected_cost: float  # Out-of-pocket transaction cost (e.g. transfer logistics cost)
    expected_recovery: float  # Expected revenue / value recovered
    net_financial_loss: float  # Net financial exposure / loss (lower is better)
    units_affected: int
    target_store_id: Optional[str] = None  # Destination store ID if TRANSFER
    assumptions: Dict[str, Any] = field(default_factory=dict)
    explanation: str = ""

@dataclass
class EOLRiskAssessment:
    """
    Complete risk assessment for a single store-product inventory position.
    """
    assessment_id: str
    store_id: str
    product_id: str
    product_name: str
    lifecycle_stage: str
    risk_score: float  # 0.0 to 100.0
    risk_level: str  # "LOW", "MEDIUM", "HIGH", "CRITICAL"
    inventory_units: int
    inventory_value: float  # inventory_units * cost_price
    weeks_of_cover: float
    successor_id: Optional[str]
    successor_confidence: float
    weeks_to_successor: Optional[float]
    weeks_to_eol: Optional[float]
    risk_factors: List[str]
    markdown_option: EOLActionOption
    transfer_option: EOLActionOption
    hold_option: EOLActionOption
    recommended_action: str  # "MARKDOWN", "TRANSFER", or "HOLD"
    expected_financial_impact: float  # Expected net financial loss/cost of recommended action
    explanation: str

@dataclass
class EOLInventorySummary:
    """
    Aggregate portfolio-level summary of EOL inventory risk.
    """
    total_eol_risk_units: int
    total_inventory_value_at_risk: float
    risky_sku_count: int
    risky_store_count: int
    markdown_exposure: float  # Total loss if all risky units were marked down
    transfer_opportunity: float  # Approved transfer savings versus holding (legacy alias)
    hold_exposure: float  # Total loss if all risky units were held
    recommended_markdown_units: int
    recommended_markdown_cost: float  # Total loss for recommended markdown positions
    recommended_transfer_units: int
    recommended_transfer_cost: float  # Total transfer logistics cost
    recommended_hold_units: int
    recommended_hold_cost: float  # Total loss for recommended hold positions
    action_breakdown: Dict[str, int] = field(default_factory=dict)
    candidate_transfer_opportunity: float = 0.0
    approved_transfer_opportunity: float = 0.0
    approved_transfer_units: int = 0
    approved_transfer_cost: float = 0.0
    approved_transfer_routes: int = 0
    rejected_due_to_destination_capacity: int = 0
    rejected_due_to_source_capacity: int = 0


@dataclass(frozen=True)
class EOLTransferRoute:
    """A candidate or approved EOL store-to-store transfer route."""
    source_store_id: str
    destination_store_id: str
    product_id: str
    requested_units: int
    source_excess_units: int
    destination_shortfall_units: int
    expected_cost: float
    expected_loss: float
    savings_vs_hold: float
    status: str  # "APPROVED" or "REJECTED"
    approved_units: int = 0
    rejection_reason: Optional[str] = None


@dataclass
class PortfolioTransferResolution:
    """Deterministic, capacity-feasible EOL transfer plan for one planning run."""
    approved_routes: List[EOLTransferRoute] = field(default_factory=list)
    rejected_routes: List[EOLTransferRoute] = field(default_factory=list)
    candidate_transfer_opportunity: float = 0.0
    approved_transfer_opportunity: float = 0.0
    source_capacity_ledger: Dict[str, Dict[str, int]] = field(default_factory=dict)
    destination_capacity_ledger: Dict[str, Dict[str, int]] = field(default_factory=dict)
