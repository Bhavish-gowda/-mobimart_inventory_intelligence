"""
Data Models for MobiMart 52-Week Rolling Simulator & Baseline Benchmark.
Provides typed definitions for configuration, state, snapshots, weekly results,
run results, metrics, and strategy comparison scorecards.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional

@dataclass
class SimulationConfig:
    start_week: int = 1
    end_week: int = 52
    capital_budget_limit: float = 40000000.0  # ₹4 Crore
    starting_capital_target: float = 38000000.0  # ₹3.80 Crore target for store stock
    warehouse_cover_weeks: float = 8.0  # Opening warehouse inventory multiplier (weeks of supply)
    store_transfer_cost_per_unit: float = 500.0  # ₹500/unit
    warehouse_allocation_cost_per_unit: float = 250.0  # ₹250/unit
    baseline_lookback_weeks: int = 4  # Last 4 completed weeks
    dead_stock_lookback_weeks: int = 4  # 4 weeks of zero observed sales
    block_high_risk_eol_replenishment: bool = True

@dataclass
class SimulationState:
    week_number: int
    store_inventory: Dict[Tuple[str, str], Dict[str, Any]] = field(default_factory=dict)
    warehouse_stock: Dict[str, int] = field(default_factory=dict)
    capital_deployed: float = 0.0

@dataclass
class StartingInventorySnapshot:
    raw_inventory_cost: float
    operational_inventory_cost: float
    raw_total_units: int
    operational_total_units: int
    units_retained: int
    units_removed: int
    capital_headroom: float
    methodology: str = "Priority-Based Operational Cover Pruning v1"
    store_product_stock: Dict[str, int] = field(default_factory=dict)

@dataclass
class WarehouseState:
    available_stock: Dict[str, int] = field(default_factory=dict)  # product_id -> units

@dataclass
class WeeklySimulationResult:
    week_number: int
    strategy_name: str
    starting_store_units: int
    starting_store_cost: float
    ending_store_units: int
    ending_store_cost: float
    warehouse_units: int
    warehouse_cost: float
    units_allocated: int
    allocation_cost: float
    transferred_units: int
    transfer_cost: float
    markdowned_units: int
    markdown_loss: float
    demand_units: int
    fulfilled_units: int
    lost_sales_units: int
    lost_sales_value: float
    stockout_observations: int
    positive_demand_observations: int
    revenue: float
    gross_margin: float
    cogs: float
    dead_stock_units: int
    average_weeks_of_cover: float

@dataclass
class MetricResult:
    metric_name: str
    baseline_value: float
    mobimart_value: float
    absolute_difference: float
    percentage_difference: float
    unit: str = ""

@dataclass
class SimulationRunResult:
    strategy_name: str
    config: SimulationConfig
    starting_snapshot: StartingInventorySnapshot
    weekly_results: List[WeeklySimulationResult] = field(default_factory=list)
    
    # Aggregated Scorecard Metrics
    stockout_rate: float = 0.0
    average_weeks_of_cover: float = 0.0
    dead_stock_pct: float = 0.0
    actual_markdown_loss: float = 0.0
    capital_turns: float = 0.0
    
    # Supporting Metrics
    total_revenue: float = 0.0
    total_gross_margin: float = 0.0
    total_cogs: float = 0.0
    total_fulfilled_units: int = 0
    total_lost_sales_units: int = 0
    total_lost_sales_value: float = 0.0
    total_transferred_units: int = 0
    total_transfer_cost: float = 0.0
    total_allocated_units: int = 0
    total_allocation_cost: float = 0.0
    total_markdowned_units: int = 0
    average_inventory_cost: float = 0.0
    ending_inventory_cost: float = 0.0
    service_level_pct: float = 0.0
    runtime_seconds: float = 0.0

@dataclass
class StrategyComparison:
    baseline_run: SimulationRunResult
    mobimart_run: SimulationRunResult
    metrics: Dict[str, MetricResult] = field(default_factory=dict)
    summary_text: str = ""
