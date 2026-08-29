"""
EOL Decision Engine for MobiMart.
Compares Markdown, Transfer, and Hold economics and selects the financially
preferable action based on lowest expected net financial loss.
Produces a complete EOLRiskAssessment for a single store-product position.
"""

from typing import Dict, List, Any, Optional
from backend.engine.eol.models import EOLActionOption, EOLRiskAssessment
from backend.engine.eol.config import TARGET_WEEKS_OF_COVER
from backend.engine.eol.risk import calculate_eol_risk_score, calculate_weeks_of_cover
from backend.engine.eol.markdown import evaluate_markdown_option
from backend.engine.eol.transfer import evaluate_transfer_option
from backend.engine.eol.hold import evaluate_hold_option
from backend.engine.eol.explanations import generate_eol_explanation
from backend.engine.eol.portfolio import (
    apply_portfolio_transfer_resolution,
    resolve_portfolio_transfers,
)
from backend.engine.allocation.forecast import forecast_weekly_demand, get_recent_sales_velocity, get_rolling_average

def assess_eol_risk_position(
    store: Dict[str, Any],
    product: Dict[str, Any],
    inventory_record: Dict[str, Any],
    all_stores: List[Dict[str, Any]],
    all_inventory: List[Dict[str, Any]],
    sales_history_df: Any,
    current_week: int = 24,
    forecast_func: Any = forecast_weekly_demand,
    historical_demand_positions: Optional[set] = None,
) -> Optional[EOLRiskAssessment]:
    """
    Evaluate end-of-life risk and produce a full EOLRiskAssessment for one store-product pair.

    Steps:
      1. Pull inventory and forecast data (historical data only)
      2. Score EOL risk
      3. Evaluate all three options: MARKDOWN, TRANSFER, HOLD
      4. Compare and select lowest-loss option
      5. Generate deterministic explanation
      6. Return an EOLRiskAssessment

    Returns None if risk_level is LOW and inventory_units <= 0.
    """
    store_id = store["id"]
    product_id = product["id"]
    product_name = product.get("model_name", product_id)

    inventory_units = int(inventory_record.get("current_stock", 0))

    # Forecast demand using only historical data
    forecast_result = forecast_func(sales_history_df, store, product, current_week)
    forecast_demand = forecast_result.forecast_weekly_demand

    # Recent + rolling averages for risk scoring
    recent_velocity = get_recent_sales_velocity(sales_history_df, store_id, product_id, current_week, window=3)
    rolling_avg_6w = get_rolling_average(sales_history_df, store_id, product_id, current_week, window=6)

    woc = calculate_weeks_of_cover(inventory_units, forecast_demand)

    # Successor info
    successor_id = product.get("successor_product_id")
    expected_successor_week = product.get("expected_successor_week")
    launch_confidence = float(product.get("launch_confidence", 1.0))
    is_rumoured = bool(product.get("is_rumoured", False))

    # Adjust confidence for rumoured successors
    if is_rumoured:
        successor_confidence = min(launch_confidence, 0.70)
    else:
        successor_confidence = launch_confidence

    weeks_to_successor: Optional[float] = None
    if expected_successor_week is not None:
        weeks_to_successor = float(expected_successor_week - current_week)

    weeks_to_eol: Optional[float] = None
    if product.get("lifecycle_stage") in ("EOL", "Decline"):
        weeks_to_eol = weeks_to_successor if weeks_to_successor is not None else 4.0

    # 1. Risk Scoring
    risk_score, risk_level, risk_factors, _ = calculate_eol_risk_score(
        product=product,
        inventory_units=inventory_units,
        forecast_weekly_demand=forecast_demand,
        recent_sales_velocity=recent_velocity,
        rolling_avg=rolling_avg_6w,
        current_week=current_week,
    )

    # Skip LOW-risk positions with no stock
    if risk_level == "LOW" and inventory_units <= 0:
        return None

    inventory_value = round(inventory_units * float(product.get("cost_price", 0.0)), 2)

    # 2a. Markdown Option
    markdown_opt = evaluate_markdown_option(
        product=product,
        inventory_units=inventory_units,
    )

    # 2b. Transfer Option
    transfer_opt = evaluate_transfer_option(
        source_store_id=store_id,
        product=product,
        inventory_units=inventory_units,
        source_woc=woc,
        all_stores=all_stores,
        all_inventory=all_inventory,
        sales_history_df=sales_history_df,
        forecast_func=forecast_func,
        current_week=current_week,
        historical_demand_positions=historical_demand_positions,
    )

    # 2c. Hold Option
    hold_opt = evaluate_hold_option(
        product=product,
        inventory_units=inventory_units,
        forecast_weekly_demand=forecast_demand,
        current_week=current_week,
    )

    # 3. Compare all options: pick lowest net_financial_loss
    # Transfer option with no valid destination has net_financial_loss = inf
    options = [
        ("MARKDOWN", markdown_opt.net_financial_loss),
        ("TRANSFER", transfer_opt.net_financial_loss),
        ("HOLD", hold_opt.net_financial_loss),
    ]
    recommended_action, expected_impact = min(options, key=lambda x: x[1])

    # 4. Build explanation
    explanation = generate_eol_explanation(
        risk_level=risk_level,
        risk_score=risk_score,
        store_id=store_id,
        product_name=product_name,
        product_id=product_id,
        inventory_units=inventory_units,
        weeks_of_cover=woc,
        successor_id=successor_id,
        weeks_to_successor=weeks_to_successor,
        risk_factors=risk_factors,
        markdown_opt=markdown_opt,
        transfer_opt=transfer_opt,
        hold_opt=hold_opt,
        recommended_action=recommended_action,
    )

    assessment_id = f"EOL-{store_id}-{product_id}-W{current_week}"

    return EOLRiskAssessment(
        assessment_id=assessment_id,
        store_id=store_id,
        product_id=product_id,
        product_name=product_name,
        lifecycle_stage=product.get("lifecycle_stage", ""),
        risk_score=risk_score,
        risk_level=risk_level,
        inventory_units=inventory_units,
        inventory_value=inventory_value,
        weeks_of_cover=round(woc, 2),
        successor_id=successor_id,
        successor_confidence=round(successor_confidence, 2),
        weeks_to_successor=round(weeks_to_successor, 1) if weeks_to_successor is not None else None,
        weeks_to_eol=round(weeks_to_eol, 1) if weeks_to_eol is not None else None,
        risk_factors=risk_factors,
        markdown_option=markdown_opt,
        transfer_option=transfer_opt,
        hold_option=hold_opt,
        recommended_action=recommended_action,
        expected_financial_impact=round(expected_impact, 2),
        explanation=explanation,
    )


def run_eol_portfolio_assessment(
    stores: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    inventory_records: List[Dict[str, Any]],
    sales_history_df: Any,
    current_week: int = 24,
    min_risk_level: str = "MEDIUM",
) -> tuple[List[EOLRiskAssessment], Any]:
    """
    Run EOL risk assessment across all store-product positions.
    Returns only assessments at or above min_risk_level.
    """
    RISK_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3}
    min_level_val = RISK_ORDER.get(min_risk_level, 1)
    # Work only with observations available at the decision point. This is both
    # the no-leakage boundary and a substantial reduction in repeated forecast
    # filtering during transfer destination searches.
    historical_sales_df = sales_history_df[
        sales_history_df["week_number"] < current_week
    ].copy()

    # Map inventory records for quick lookup
    inv_lookup: Dict[str, Dict[str, Any]] = {}
    for rec in inventory_records:
        key = f"{rec['store_id']}|{rec['product_id']}"
        inv_lookup[key] = rec

    assessments: List[EOLRiskAssessment] = []

    # Transfer searches repeatedly request forecasts for the same store-product
    # pairs. Cache those deterministic, historical-only results for this run.
    forecast_cache: Dict[str, Any] = {}
    historical_demand_positions = {
        (row.store_id, row.product_id)
        for row in historical_sales_df.loc[
            historical_sales_df["units_sold"] > 0,
            ["store_id", "product_id"],
        ].itertuples(index=False)
    }

    def cached_forecast(
        history: Any, store: Dict[str, Any], product: Dict[str, Any], week: int
    ) -> Any:
        key = f"{store['id']}|{product['id']}|{week}"
        if key not in forecast_cache:
            forecast_cache[key] = forecast_weekly_demand(history, store, product, week)
        return forecast_cache[key]

    for store in stores:
        for product in products:
            stage = product.get("lifecycle_stage", "Peak")
            # Peak products have no EOL exposure unless product metadata says
            # otherwise. Limiting the portfolio run to late-lifecycle SKUs
            # keeps the engine focused and avoids unnecessary transfer scans.
            if stage not in ("EOL", "Decline"):
                continue

            key = f"{store['id']}|{product['id']}"
            inv_rec = inv_lookup.get(key, {"store_id": store["id"], "product_id": product["id"], "current_stock": 0, "in_transit_stock": 0})

            result = assess_eol_risk_position(
                store=store,
                product=product,
                inventory_record=inv_rec,
                all_stores=stores,
                all_inventory=inventory_records,
                sales_history_df=historical_sales_df,
                current_week=current_week,
                forecast_func=cached_forecast,
                historical_demand_positions=historical_demand_positions,
            )

            if result is not None and RISK_ORDER.get(result.risk_level, 0) >= min_level_val:
                assessments.append(result)

    resolution = resolve_portfolio_transfers(assessments)
    apply_portfolio_transfer_resolution(assessments, resolution)

    # Sort by risk_score descending
    assessments.sort(key=lambda a: a.risk_score, reverse=True)
    return assessments, resolution


def run_eol_assessment_for_all(
    stores: List[Dict[str, Any]],
    products: List[Dict[str, Any]],
    inventory_records: List[Dict[str, Any]],
    sales_history_df: Any,
    current_week: int = 24,
    min_risk_level: str = "MEDIUM",
) -> List[EOLRiskAssessment]:
    """Backward-compatible list-only EOL assessment API."""
    assessments, _ = run_eol_portfolio_assessment(
        stores, products, inventory_records, sales_history_df, current_week, min_risk_level
    )
    return assessments
