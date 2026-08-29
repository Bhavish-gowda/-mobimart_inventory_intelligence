"""
Unit tests for Evaluation & Scorecard Metrics.
"""

import pytest
from backend.engine.simulation.models import WeeklySimulationResult, SimulationConfig
from backend.engine.simulation.metrics import aggregate_simulation_metrics

def test_capital_turns_formula_correction_3():
    # Correction 3: Capital Turns = COGS / Avg Inventory Cost
    wk1 = WeeklySimulationResult(
        week_number=1, strategy_name="TEST", starting_store_units=100, starting_store_cost=10000.0,
        ending_store_units=90, ending_store_cost=9000.0, warehouse_units=50, warehouse_cost=5000.0,
        units_allocated=0, allocation_cost=0.0, transferred_units=0, transfer_cost=0.0,
        markdowned_units=0, markdown_loss=0.0, demand_units=10, fulfilled_units=10,
        lost_sales_units=0, lost_sales_value=0.0, stockout_observations=0, positive_demand_observations=1,
        revenue=1500.0, gross_margin=500.0, cogs=1000.0, dead_stock_units=0, average_weeks_of_cover=4.0
    )
    wk2 = WeeklySimulationResult(
        week_number=2, strategy_name="TEST", starting_store_units=90, starting_store_cost=9000.0,
        ending_store_units=80, ending_store_cost=8000.0, warehouse_units=50, warehouse_cost=5000.0,
        units_allocated=0, allocation_cost=0.0, transferred_units=0, transfer_cost=0.0,
        markdowned_units=0, markdown_loss=0.0, demand_units=10, fulfilled_units=10,
        lost_sales_units=0, lost_sales_value=0.0, stockout_observations=0, positive_demand_observations=1,
        revenue=1500.0, gross_margin=500.0, cogs=1000.0, dead_stock_units=0, average_weeks_of_cover=4.0
    )

    config = SimulationConfig()
    metrics = aggregate_simulation_metrics([wk1, wk2], config)

    # Total COGS = 1000 + 1000 = 2000
    # Avg Inventory Cost = (9000 + 8000) / 2 = 8500
    # Capital Turns = 2000 / 8500 = 0.23529... -> 0.24
    assert metrics["total_cogs"] == 2000.0
    assert metrics["average_inventory_cost"] == 8500.0
    assert metrics["capital_turns"] == round(2000.0 / 8500.0, 2)

def test_stockout_rate_calculation():
    wk1 = WeeklySimulationResult(
        week_number=1, strategy_name="TEST", starting_store_units=10, starting_store_cost=100.0,
        ending_store_units=0, ending_store_cost=0.0, warehouse_units=0, warehouse_cost=0.0,
        units_allocated=0, allocation_cost=0.0, transferred_units=0, transfer_cost=0.0,
        markdowned_units=0, markdown_loss=0.0, demand_units=5, fulfilled_units=0,
        lost_sales_units=5, lost_sales_value=50.0, stockout_observations=2, positive_demand_observations=10,
        revenue=0.0, gross_margin=0.0, cogs=0.0, dead_stock_units=0, average_weeks_of_cover=0.0
    )
    config = SimulationConfig()
    metrics = aggregate_simulation_metrics([wk1], config)

    # Stockout Rate = 2 / 10 = 20.0%
    assert metrics["stockout_rate"] == 20.0
