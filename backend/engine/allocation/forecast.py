"""
Deterministic Demand Forecasting Engine for MobiMart Allocation.
Combines historical sales velocity, rolling averages, trend factors, seasonality,
product lifecycle stage, and store affinity into an explainable weekly demand forecast.

CRITICAL: Strictly consumes historical sales up to current_week - 1. Never uses future data.
"""

from typing import Dict, List, Any, Optional, Tuple
import numpy as np
import pandas as pd
from backend.engine.allocation.models import ForecastResult

import weakref

# Module-level cache: maps id(df) -> (weakref.ref(df), len(df), sales_dict)
_SALES_CACHE: Dict[int, Tuple[Any, int, Dict[Tuple[str, str, int], int]]] = {}

def _get_sales_dict(sales_history_df: pd.DataFrame) -> Dict[Tuple[str, str, int], int]:
    """Precompute fast lookup mapping (store_id, product_id, week_number) -> units_sold.
    Cached per DataFrame object using id(df) and weakref to avoid recomputation on repeated calls
    and prevent pandas unhashable/setattr warnings."""
    if not isinstance(sales_history_df, pd.DataFrame):
        return {}

    df_id = id(sales_history_df)
    df_len = len(sales_history_df)

    if df_id in _SALES_CACHE:
        ref, cached_len, sales_dict = _SALES_CACHE[df_id]
        if ref() is sales_history_df and cached_len == df_len:
            return sales_dict

    sales_dict: Dict[Tuple[str, str, int], int] = {}
    for row in sales_history_df.itertuples(index=False):
        sales_dict[(str(row.store_id), str(row.product_id), int(row.week_number))] = int(row.units_sold)

    if len(_SALES_CACHE) > 50:
        dead_keys = [k for k, (r, _, _) in _SALES_CACHE.items() if r() is None]
        for k in dead_keys:
            del _SALES_CACHE[k]

    _SALES_CACHE[df_id] = (weakref.ref(sales_history_df), df_len, sales_dict)
    return sales_dict

def get_recent_sales_velocity(
    sales_history_df: pd.DataFrame,
    store_id: str,
    product_id: str,
    current_week: int,
    window: int = 3,
) -> float:
    """Calculate average units sold over the past `window` weeks (weeks < current_week)."""
    start_wk = max(1, current_week - window)
    if start_wk >= current_week or not isinstance(sales_history_df, pd.DataFrame):
        return 0.0

    sales_dict = _get_sales_dict(sales_history_df)
    vals = [sales_dict[(store_id, product_id, w)] for w in range(start_wk, current_week) if (store_id, product_id, w) in sales_dict]
    if not vals:
        return 0.0
    return float(sum(vals) / len(vals))

def get_rolling_average(
    sales_history_df: pd.DataFrame,
    store_id: str,
    product_id: str,
    current_week: int,
    window: int = 6,
) -> float:
    """Calculate rolling average units sold over the past `window` weeks."""
    start_wk = max(1, current_week - window)
    if start_wk >= current_week or not isinstance(sales_history_df, pd.DataFrame):
        return 0.0

    sales_dict = _get_sales_dict(sales_history_df)
    vals = [sales_dict[(store_id, product_id, w)] for w in range(start_wk, current_week) if (store_id, product_id, w) in sales_dict]
    if not vals:
        return 0.0
    return float(sum(vals) / len(vals))

def get_trend_factor(recent_velocity: float, rolling_avg: float) -> float:
    """Calculate trend factor ratio of recent sales velocity to rolling average."""
    if rolling_avg <= 0.0:
        return 1.0
    ratio = recent_velocity / rolling_avg
    return float(np.clip(ratio, 0.50, 1.80))

def get_seasonal_factor(week: int) -> float:
    """Return seasonal factor wave for given planning week."""
    # Dussehra W41, Diwali W42, New Year W52 surges
    if week == 41:
        return 2.5
    elif week == 42:
        return 3.0
    elif week == 52:
        return 1.7
    return float(1.0 + 0.08 * np.sin(2.0 * np.pi * week / 52.0))

def get_lifecycle_factor(product: Dict[str, Any], current_week: int) -> float:
    """Calculate product lifecycle stage factor for planning week."""
    stage = product.get("lifecycle_stage", "Peak")
    if stage == "Launch":
        return 1.35
    elif stage == "Growth":
        return 1.15
    elif stage == "Peak":
        return 1.00
    elif stage == "Decline":
        return 0.55
    elif stage == "EOL":
        return 0.20
    return 1.00

def forecast_weekly_demand(
    sales_history_df: pd.DataFrame,
    store: Dict[str, Any],
    product: Dict[str, Any],
    current_week: int,
) -> ForecastResult:
    """
    Master explainable demand forecast equation for store-product pair.
    Forecast = RecentVelocity * TrendFactor * SeasonalFactor * LifecycleFactor * StoreAffinity
    """
    store_id = store["id"]
    product_id = product["id"]
    segment = product["segment"]

    recent_velocity = get_recent_sales_velocity(sales_history_df, store_id, product_id, current_week, window=3)
    rolling_avg = get_rolling_average(sales_history_df, store_id, product_id, current_week, window=6)
    trend_factor = get_trend_factor(recent_velocity, rolling_avg)
    seasonal_factor = get_seasonal_factor(current_week)
    lifecycle_factor = get_lifecycle_factor(product, current_week)

    # Store affinity factor
    key_map = {
        "Budget": "budget_affinity",
        "Mid-Range": "mid_range_affinity",
        "Premium": "premium_affinity",
        "Flagship": "flagship_affinity",
    }
    affinity_key = key_map.get(segment, "mid_range_affinity")
    affinity_factor = float(store.get(affinity_key, 1.0))

    # Base baseline demand calculation
    sales_dict = _get_sales_dict(sales_history_df)
    has_observed_history = any((store_id, product_id, w) in sales_dict for w in range(1, current_week))
    stage = product.get("lifecycle_stage", "Peak")

    if not has_observed_history:
        # Cold start: no completed historical weeks observed yet for this pair
        if stage == "Launch":
            base_demand = 0.5 * affinity_factor
        else:
            base_demand = 0.2 * affinity_factor
    elif rolling_avg == 0.0 and recent_velocity == 0.0:
        # Observed historical weeks exist and sales were zero
        if stage == "Launch":
            base_demand = 0.2 * affinity_factor
        else:
            base_demand = 0.0
    else:
        # Exponentially weighted blend (70% 3-week velocity, 30% 6-week rolling avg)
        blended_velocity = 0.70 * recent_velocity + 0.30 * rolling_avg
        base_demand = blended_velocity * trend_factor

    forecasted_demand = base_demand * seasonal_factor * lifecycle_factor

    # Confidence score (0.0 to 1.0)
    sales_dict = _get_sales_dict(sales_history_df)
    data_points = sum(1 for w in range(1, current_week) if (store_id, product_id, w) in sales_dict)
    confidence = float(np.clip(data_points / 12.0, 0.30, 1.00))

    return ForecastResult(
        store_id=store_id,
        product_id=product_id,
        forecast_weekly_demand=float(max(0.0, forecasted_demand)),
        recent_sales_velocity=round(recent_velocity, 2),
        rolling_avg=round(rolling_avg, 2),
        trend_factor=round(trend_factor, 2),
        seasonal_factor=round(seasonal_factor, 2),
        lifecycle_factor=round(lifecycle_factor, 2),
        affinity_factor=round(affinity_factor, 2),
        confidence=round(confidence, 2),
    )
