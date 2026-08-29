"""
Pydantic Schemas for EOL Risk & Portfolio Transfer Endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class EOLAssessRequest(BaseModel):
    store_id: str = Field(..., description="Store ID", example="STORE_01")
    product_id: str = Field(..., description="Product SKU ID", example="PROD_058")
    current_week: int = Field(24, ge=1, le=52, description="Current week number", example=24)

class EOLActionOptionSchema(BaseModel):
    action: str
    expected_cost: float
    expected_recovery: float
    net_financial_loss: float
    units_affected: int
    target_store_id: Optional[str] = None
    assumptions: Dict[str, Any]
    explanation: str

class EOLRiskAssessmentSchema(BaseModel):
    assessment_id: str
    store_id: str
    product_id: str
    product_name: str
    lifecycle_stage: str
    risk_score: float
    risk_level: str
    inventory_units: int
    inventory_value: float
    weeks_of_cover: float
    successor_id: Optional[str] = None
    successor_confidence: Optional[float] = None
    weeks_to_successor: Optional[float] = None
    weeks_to_eol: Optional[float] = None
    risk_factors: List[str]
    markdown_option: EOLActionOptionSchema
    transfer_option: EOLActionOptionSchema
    hold_option: EOLActionOptionSchema
    recommended_action: str
    expected_financial_impact: float
    explanation: str

class EOLTransferRouteSchema(BaseModel):
    source_store_id: str
    destination_store_id: str
    product_id: str
    requested_units: int
    approved_units: int
    source_excess_units: int
    destination_shortfall_units: int
    expected_cost: float
    expected_loss: float
    savings_vs_hold: float
    status: str
    rejection_reason: Optional[str] = None

class PortfolioTransferResolutionSchema(BaseModel):
    approved_routes: List[EOLTransferRouteSchema]
    rejected_routes: List[EOLTransferRouteSchema]
    candidate_transfer_opportunity: float = Field(..., description="Theoretical raw candidate transfer savings")
    approved_transfer_opportunity: float = Field(..., description="Actual portfolio-approved executable transfer savings")
    source_capacity_ledger: Dict[str, Dict[str, int]]
    destination_capacity_ledger: Dict[str, Dict[str, int]]

class EOLRiskPortfolioResponse(BaseModel):
    current_week: int
    min_risk_level: str
    assessments_count: int
    assessments: List[EOLRiskAssessmentSchema]
    portfolio_resolution: PortfolioTransferResolutionSchema
