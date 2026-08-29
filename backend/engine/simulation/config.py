"""
Configuration constants for MobiMart 52-Week Simulator.
"""

from backend.engine.simulation.models import SimulationConfig

# Central configuration instance
DEFAULT_SIMULATION_CONFIG = SimulationConfig(
    start_week=1,
    end_week=52,
    capital_budget_limit=40000000.0,  # ₹4 Crore
    starting_capital_target=38000000.0,  # ₹3.80 Crore
    warehouse_cover_weeks=8.0,
    store_transfer_cost_per_unit=500.0,  # ₹500
    warehouse_allocation_cost_per_unit=250.0,  # ₹250
    baseline_lookback_weeks=4,
    dead_stock_lookback_weeks=4,
    block_high_risk_eol_replenishment=True,
)
