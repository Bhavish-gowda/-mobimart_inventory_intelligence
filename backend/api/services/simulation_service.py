"""
Simulation Service Layer.
Delegates directly to Phase 3C simulation engine (`run_simulation`, `compare_strategies`).
Does NOT duplicate simulation logic or maintain shared mutable state.
"""

from typing import Dict, List, Any, Optional
from backend.api.data_loader import (
    load_sales_history_df,
    load_stores_list,
    load_products_list,
    load_inventory_list,
)
from backend.engine.simulation.models import SimulationConfig, SimulationRunResult, StrategyComparison
from backend.engine.simulation.state import (
    build_starting_inventory_snapshot,
    build_warehouse_opening_state,
)
from backend.engine.simulation.runner import run_simulation
from backend.engine.simulation.comparison import compare_strategies

# In-memory result cache for simulation and benchmark runs
_BENCHMARK_CACHE: Dict[Tuple[int, int, float, float, float, int], StrategyComparison] = {}
_SIMULATION_CACHE: Dict[Tuple[str, int, int, float, float, float, int], SimulationRunResult] = {}

def clear_simulation_caches() -> None:
    """Utility to clear in-memory caches if needed."""
    _BENCHMARK_CACHE.clear()
    _SIMULATION_CACHE.clear()

def execute_simulation_run(
    strategy_name: str,
    start_week: int = 1,
    end_week: int = 52,
    capital_budget_limit: float = 40000000.0,
    starting_capital_target: float = 38000000.0,
    warehouse_cover_weeks: float = 8.0,
    baseline_lookback_weeks: int = 4,
) -> SimulationRunResult:
    strategy_upper = strategy_name.upper()
    if strategy_upper not in ("BASELINE", "MOBIMART"):
        from backend.api.errors import InvalidRequestException
        raise InvalidRequestException(
            f"Invalid strategy_name '{strategy_name}'. Must be 'BASELINE' or 'MOBIMART'.",
        )

    cache_key = (
        strategy_upper,
        start_week,
        end_week,
        capital_budget_limit,
        starting_capital_target,
        warehouse_cover_weeks,
        baseline_lookback_weeks,
    )
    if cache_key in _SIMULATION_CACHE:
        return _SIMULATION_CACHE[cache_key]

    stores = load_stores_list()
    products = load_products_list()
    inventory_records = load_inventory_list()
    sales_df = load_sales_history_df()

    config = SimulationConfig(
        start_week=start_week,
        end_week=end_week,
        capital_budget_limit=capital_budget_limit,
        starting_capital_target=starting_capital_target,
        warehouse_cover_weeks=warehouse_cover_weeks,
        baseline_lookback_weeks=baseline_lookback_weeks,
    )

    snapshot = build_starting_inventory_snapshot(
        inventory_df_or_records=inventory_records,
        products=products,
        stores=stores,
        target_capital=config.starting_capital_target,
    )

    warehouse_opening = build_warehouse_opening_state(
        products=products,
        sales_history_df=sales_df,
        cover_weeks=config.warehouse_cover_weeks,
    )

    run_result = run_simulation(
        strategy_name=strategy_upper,
        sales_history_df=sales_df,
        stores=stores,
        products=products,
        starting_snapshot=snapshot,
        warehouse_opening_stock=warehouse_opening,
        config=config,
    )

    _SIMULATION_CACHE[cache_key] = run_result
    return run_result

def execute_benchmark_comparison(
    start_week: int = 1,
    end_week: int = 52,
    capital_budget_limit: float = 40000000.0,
    starting_capital_target: float = 38000000.0,
    warehouse_cover_weeks: float = 8.0,
    baseline_lookback_weeks: int = 4,
) -> Tuple[StrategyComparison, bool]:
    """
    Execute benchmark comparison between Strategy A (Baseline) and Strategy B (MobiMart).
    Cached per unique configuration parameters. Returns (StrategyComparison, is_cached).
    """
    cache_key = (
        start_week,
        end_week,
        capital_budget_limit,
        starting_capital_target,
        warehouse_cover_weeks,
        baseline_lookback_weeks,
    )
    if cache_key in _BENCHMARK_CACHE:
        return _BENCHMARK_CACHE[cache_key], True

    baseline_run = execute_simulation_run(
        strategy_name="BASELINE",
        start_week=start_week,
        end_week=end_week,
        capital_budget_limit=capital_budget_limit,
        starting_capital_target=starting_capital_target,
        warehouse_cover_weeks=warehouse_cover_weeks,
        baseline_lookback_weeks=baseline_lookback_weeks,
    )

    mobimart_run = execute_simulation_run(
        strategy_name="MOBIMART",
        start_week=start_week,
        end_week=end_week,
        capital_budget_limit=capital_budget_limit,
        starting_capital_target=starting_capital_target,
        warehouse_cover_weeks=warehouse_cover_weeks,
        baseline_lookback_weeks=baseline_lookback_weeks,
    )

    comparison = compare_strategies(baseline_run, mobimart_run)
    _BENCHMARK_CACHE[cache_key] = comparison
    return comparison, False
