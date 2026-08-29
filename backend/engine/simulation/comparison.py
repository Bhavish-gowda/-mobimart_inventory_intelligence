"""
Strategy Comparison Scorecard Engine for MobiMart Simulator.
Compares Baseline (Strategy A) vs MobiMart (Strategy B) on all mandatory
and supporting evaluation metrics.
Handles absolute difference, percentage difference, and percentage-point difference.
Reports baseline wins honestly if baseline outperforms MobiMart on any metric.
"""

from typing import Dict, Any
from backend.engine.simulation.models import SimulationRunResult, MetricResult, StrategyComparison

def compare_strategies(
    baseline_run: SimulationRunResult,
    mobimart_run: SimulationRunResult,
) -> StrategyComparison:
    """
    Generate structured comparison scorecard.
    """
    metrics: Dict[str, MetricResult] = {}

    def add_metric(
        name: str, base_val: float, mobi_val: float, unit: str = "", is_pct_pt: bool = False
    ):
        abs_diff = round(mobi_val - base_val, 2)
        if base_val != 0:
            pct_diff = round(((mobi_val - base_val) / abs(base_val)) * 100.0, 2)
        else:
            pct_diff = 0.0

        metrics[name] = MetricResult(
            metric_name=name,
            baseline_value=round(base_val, 2),
            mobimart_value=round(mobi_val, 2),
            absolute_difference=abs_diff,
            percentage_difference=pct_diff,
            unit=unit if not is_pct_pt else "pp",
        )

    # Core 5 Mandatory Metrics
    add_metric("Stockout Rate", baseline_run.stockout_rate, mobimart_run.stockout_rate, "%", is_pct_pt=True)
    add_metric("Average Weeks of Cover", baseline_run.average_weeks_of_cover, mobimart_run.average_weeks_of_cover, "wks")
    add_metric("Dead Stock %", baseline_run.dead_stock_pct, mobimart_run.dead_stock_pct, "%", is_pct_pt=True)
    add_metric("Actual Markdown Loss", baseline_run.actual_markdown_loss, mobimart_run.actual_markdown_loss, "₹")
    add_metric("Capital Turns", baseline_run.capital_turns, mobimart_run.capital_turns, "x")

    # Supporting Financial & Operational Metrics
    add_metric("Total Revenue", baseline_run.total_revenue, mobimart_run.total_revenue, "₹")
    add_metric("Total Gross Margin", baseline_run.total_gross_margin, mobimart_run.total_gross_margin, "₹")
    add_metric("Service Level", baseline_run.service_level_pct, mobimart_run.service_level_pct, "%", is_pct_pt=True)
    add_metric("Total Lost Sales Value", baseline_run.total_lost_sales_value, mobimart_run.total_lost_sales_value, "₹")
    add_metric("Total Units Allocated", baseline_run.total_allocated_units, mobimart_run.total_allocated_units, "units")
    add_metric("Total Allocation Cost", baseline_run.total_allocation_cost, mobimart_run.total_allocation_cost, "₹")
    add_metric("Average Inventory Cost", baseline_run.average_inventory_cost, mobimart_run.average_inventory_cost, "₹")

    # Construct summary text
    wins: List[str] = []
    baseline_wins: List[str] = []

    if mobimart_run.stockout_rate < baseline_run.stockout_rate:
        wins.append(f"Stockout Rate (-{abs(baseline_run.stockout_rate - mobimart_run.stockout_rate):.1f} pp)")
    elif baseline_run.stockout_rate < mobimart_run.stockout_rate:
        baseline_wins.append(f"Stockout Rate (Baseline lower by {abs(baseline_run.stockout_rate - mobimart_run.stockout_rate):.1f} pp)")

    if mobimart_run.dead_stock_pct < baseline_run.dead_stock_pct:
        wins.append(f"Dead Stock % (-{abs(baseline_run.dead_stock_pct - mobimart_run.dead_stock_pct):.1f} pp)")
    elif baseline_run.dead_stock_pct < mobimart_run.dead_stock_pct:
        baseline_wins.append(f"Dead Stock % (Baseline lower by {abs(baseline_run.dead_stock_pct - mobimart_run.dead_stock_pct):.1f} pp)")

    if mobimart_run.total_gross_margin > baseline_run.total_gross_margin:
        wins.append(f"Gross Margin (+₹{mobimart_run.total_gross_margin - baseline_run.total_gross_margin:,.2f})")
    elif baseline_run.total_gross_margin > mobimart_run.total_gross_margin:
        baseline_wins.append(f"Gross Margin (Baseline higher by ₹{baseline_run.total_gross_margin - mobimart_run.total_gross_margin:,.2f})")

    if mobimart_run.capital_turns > baseline_run.capital_turns:
        wins.append(f"Capital Turns (+{mobimart_run.capital_turns - baseline_run.capital_turns:.2f}x)")
    elif baseline_run.capital_turns > mobimart_run.capital_turns:
        baseline_wins.append(f"Capital Turns (Baseline higher by {baseline_run.capital_turns - mobimart_run.capital_turns:.2f}x)")

    summary = (
        f"MobiMart Engine vs Baseline Summary:\n"
        f"Key MobiMart Improvements: {', '.join(wins) if wins else 'None'}\n"
        f"Baseline Advantages: {', '.join(baseline_wins) if baseline_wins else 'None'}"
    )

    return StrategyComparison(
        baseline_run=baseline_run,
        mobimart_run=mobimart_run,
        metrics=metrics,
        summary_text=summary,
    )
