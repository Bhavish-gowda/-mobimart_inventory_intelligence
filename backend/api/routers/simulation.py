"""
Simulation & Benchmark API Router.
"""

from fastapi import APIRouter
from backend.api.schemas.simulation import (
    SimulationRunRequest,
    SimulationRunResultSchema,
    StartingInventorySnapshotSchema,
    BenchmarkResponse,
    MetricResultSchema,
)
from backend.api.services.simulation_service import (
    execute_simulation_run,
    execute_benchmark_comparison,
)

from fastapi import APIRouter, Response

router = APIRouter(tags=["Simulation & Benchmark"])

def _to_run_result_schema(res) -> SimulationRunResultSchema:
    snap = res.starting_snapshot
    snap_schema = StartingInventorySnapshotSchema(
        raw_inventory_cost=snap.raw_inventory_cost,
        operational_inventory_cost=snap.operational_inventory_cost,
        raw_total_units=snap.raw_total_units,
        operational_total_units=snap.operational_total_units,
        units_retained=snap.units_retained,
        units_removed=snap.units_removed,
        capital_headroom=snap.capital_headroom,
        methodology=snap.methodology,
    )
    return SimulationRunResultSchema(
        strategy_name=res.strategy_name,
        starting_snapshot=snap_schema,
        stockout_rate=res.stockout_rate,
        average_weeks_of_cover=res.average_weeks_of_cover,
        dead_stock_pct=res.dead_stock_pct,
        actual_markdown_loss=res.actual_markdown_loss,
        capital_turns=res.capital_turns,
        total_revenue=res.total_revenue,
        total_gross_margin=res.total_gross_margin,
        total_cogs=res.total_cogs,
        total_fulfilled_units=res.total_fulfilled_units,
        total_lost_sales_units=res.total_lost_sales_units,
        total_lost_sales_value=res.total_lost_sales_value,
        total_transferred_units=res.total_transferred_units,
        total_transfer_cost=res.total_transfer_cost,
        total_allocated_units=res.total_allocated_units,
        total_allocation_cost=res.total_allocation_cost,
        total_markdowned_units=res.total_markdowned_units,
        average_inventory_cost=res.average_inventory_cost,
        ending_inventory_cost=res.ending_inventory_cost,
        service_level_pct=res.service_level_pct,
        runtime_seconds=res.runtime_seconds,
    )

@router.post(
    "/simulation/run",
    response_model=SimulationRunResultSchema,
    summary="Run 52-Week Rolling Strategy Simulation",
    description="Runs a 52-week rolling simulation for strategy 'BASELINE' or 'MOBIMART'.",
)
def run_simulation_endpoint(request: SimulationRunRequest) -> SimulationRunResultSchema:
    config_dict = request.config.model_dump() if request.config else {}
    res = execute_simulation_run(
        strategy_name=request.strategy_name,
        start_week=config_dict.get("start_week", 1),
        end_week=config_dict.get("end_week", 52),
        capital_budget_limit=config_dict.get("capital_budget_limit", 40000000.0),
        starting_capital_target=config_dict.get("starting_capital_target", 38000000.0),
        warehouse_cover_weeks=config_dict.get("warehouse_cover_weeks", 8.0),
        baseline_lookback_weeks=config_dict.get("baseline_lookback_weeks", 4),
    )
    return _to_run_result_schema(res)

@router.post(
    "/simulation/benchmark",
    response_model=BenchmarkResponse,
    summary="Execute Baseline vs MobiMart Benchmark Comparison",
    description="Executes benchmark comparison between Strategy A (Baseline) and Strategy B (MobiMart). Defaults to full 52 weeks.",
)
def run_benchmark_post(
    response: Response,
    start_week: int = 1,
    end_week: int = 52,
) -> BenchmarkResponse:
    comp, is_cached = execute_benchmark_comparison(start_week=start_week, end_week=end_week)
    response.headers["X-Benchmark-Cache"] = "HIT" if is_cached else "MISS"
    
    metrics_map = {
        k: MetricResultSchema(
            metric_name=m.metric_name,
            baseline_value=m.baseline_value,
            mobimart_value=m.mobimart_value,
            absolute_difference=m.absolute_difference,
            percentage_difference=m.percentage_difference,
            unit=m.unit,
        )
        for k, m in comp.metrics.items()
    }

    return BenchmarkResponse(
        baseline=_to_run_result_schema(comp.baseline_run),
        mobimart=_to_run_result_schema(comp.mobimart_run),
        metrics=metrics_map,
        summary_text=comp.summary_text,
    )

@router.get(
    "/simulation/benchmark",
    response_model=BenchmarkResponse,
    summary="Get Baseline vs MobiMart Benchmark Comparison (GET Convenience)",
    description="Convenience GET endpoint executing full 52-week benchmark comparison.",
)
def run_benchmark_get(
    response: Response,
    start_week: int = 1,
    end_week: int = 52,
) -> BenchmarkResponse:
    return run_benchmark_post(response=response, start_week=start_week, end_week=end_week)
