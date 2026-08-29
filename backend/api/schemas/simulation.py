"""
Pydantic Schemas for Simulation & Benchmark Endpoints.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

class SimulationConfigRequestSchema(BaseModel):
    start_week: int = Field(1, ge=1, le=52)
    end_week: int = Field(52, ge=1, le=52)
    capital_budget_limit: float = Field(40000000.0, ge=0.0)
    starting_capital_target: float = Field(38000000.0, ge=0.0)
    warehouse_cover_weeks: float = Field(8.0, ge=1.0)
    baseline_lookback_weeks: int = Field(4, ge=1)

class SimulationRunRequest(BaseModel):
    strategy_name: str = Field(..., description="Strategy name: 'BASELINE' or 'MOBIMART'", example="MOBIMART")
    config: Optional[SimulationConfigRequestSchema] = None

class StartingInventorySnapshotSchema(BaseModel):
    raw_inventory_cost: float
    operational_inventory_cost: float
    raw_total_units: int
    operational_total_units: int
    units_retained: int
    units_removed: int
    capital_headroom: float
    methodology: str

class MetricResultSchema(BaseModel):
    metric_name: str
    baseline_value: float
    mobimart_value: float
    absolute_difference: float
    percentage_difference: float
    unit: str

class SimulationRunResultSchema(BaseModel):
    strategy_name: str
    starting_snapshot: StartingInventorySnapshotSchema
    stockout_rate: float
    average_weeks_of_cover: float
    dead_stock_pct: float
    actual_markdown_loss: float
    capital_turns: float
    total_revenue: float
    total_gross_margin: float
    total_cogs: float
    total_fulfilled_units: int
    total_lost_sales_units: int
    total_lost_sales_value: float
    total_transferred_units: int
    total_transfer_cost: float
    total_allocated_units: int
    total_allocation_cost: float
    total_markdowned_units: int
    average_inventory_cost: float
    ending_inventory_cost: float
    service_level_pct: float
    runtime_seconds: float

class BenchmarkResponse(BaseModel):
    baseline: SimulationRunResultSchema
    mobimart: SimulationRunResultSchema
    metrics: Dict[str, MetricResultSchema]
    summary_text: str
