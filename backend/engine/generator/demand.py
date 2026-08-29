"""
Causal demand calculation functions for MobiMart Synthetic Data Generator.
Calculates realistic weekly demand based on store catchment, segment affinity, product lifecycle,
festive events, seasonality, and successor cannibalization.
"""

from typing import Dict, List, Any
import numpy as np
from backend.engine.generator.config import (
    SEGMENT_BASE_DEMAND,
    FESTIVE_WEEKS,
    FESTIVE_MULTIPLIERS,
)

def calculate_base_demand(product: Dict[str, Any]) -> float:
    """Return central base weekly chain-wide demand for product segment."""
    segment = product["segment"]
    min_d, max_d = SEGMENT_BASE_DEMAND.get(segment, (10.0, 25.0))
    # Midpoint base demand for product tier
    return (min_d + max_d) / 2.0 / 25.0  # Per store average base

def calculate_store_multiplier(store: Dict[str, Any]) -> float:
    """Calculate store footfall and income catchment multiplier."""
    footfall_factor = store["monthly_footfall"] / 40000.0
    income_factor = store["income_index"]
    return footfall_factor * income_factor

def calculate_segment_affinity(store: Dict[str, Any], product: Dict[str, Any]) -> float:
    """Return store's affinity for product's segment."""
    segment = product["segment"]
    key_map = {
        "Budget": "budget_affinity",
        "Mid-Range": "mid_range_affinity",
        "Premium": "premium_affinity",
        "Flagship": "flagship_affinity",
    }
    affinity_key = key_map.get(segment, "mid_range_affinity")
    return store.get(affinity_key, 1.0)

def calculate_lifecycle_factor(product: Dict[str, Any], week: int) -> float:
    """Calculate product lifecycle stage multiplier for given week."""
    launch_w = product["launch_week"]
    stage = product["lifecycle_stage"]

    if week < launch_w:
        return 0.0  # Product not yet launched

    weeks_since_launch = week - launch_w

    if stage == "Launch":
        # Launch surge curve
        if weeks_since_launch <= 2:
            return 1.4
        elif weeks_since_launch <= 4:
            return 1.2
        return 1.0
    elif stage == "Growth":
        return 1.15
    elif stage == "Peak":
        return 1.0
    elif stage == "Decline":
        # Gradual decline
        decay = max(0.25, 0.70 - (weeks_since_launch * 0.02))
        return decay
    elif stage == "EOL":
        return 0.12
    return 1.0

def calculate_seasonality(week: int) -> float:
    """Calculate mild continuous annual seasonality factor."""
    # Smooth annual sine wave peaking around summer (week 20)
    return 1.0 + 0.08 * np.sin(2.0 * np.pi * week / 52.0)

def calculate_festival_factor(product: Dict[str, Any], week: int) -> float:
    """Calculate festival uplift factor for Dussehra, Diwali, and New Year."""
    if week not in FESTIVE_WEEKS:
        return 1.0

    festival_name = FESTIVE_WEEKS[week]
    segment = product["segment"]
    multiplier = FESTIVE_MULTIPLIERS.get(festival_name, {}).get(segment, 1.0)

    # Scale rumoured launches by launch confidence if applicable
    if product.get("is_rumoured", False):
        confidence = product.get("launch_confidence", 1.0)
        multiplier = 1.0 + ((multiplier - 1.0) * confidence)

    return multiplier

def calculate_cannibalization(product: Dict[str, Any], all_products_by_id: Dict[str, Dict[str, Any]], week: int) -> float:
    """
    Calculate successor cannibalization decay effect.
    When a successor product launches, predecessor demand decays exponentially.
    """
    successor_id = product.get("successor_product_id")
    if not successor_id or successor_id not in all_products_by_id:
        return 1.0

    successor = all_products_by_id[successor_id]
    successor_launch_week = product.get("expected_successor_week")

    if successor_launch_week is None or week < successor_launch_week:
        return 1.0  # Successor not yet launched

    # Rumoured launch confidence adjustment
    confidence = product.get("launch_confidence", 1.0)
    weeks_post_launch = week - successor_launch_week

    # Exponential cannibalization decay curve
    decay_rate = 0.25 * confidence
    cannibalization_factor = np.exp(-decay_rate * weeks_post_launch)

    return float(max(0.05, cannibalization_factor))

def calculate_weekly_demand(
    store: Dict[str, Any],
    product: Dict[str, Any],
    week: int,
    all_products_by_id: Dict[str, Dict[str, Any]],
    rng: np.random.Generator,
) -> float:
    """
    Master demand equation combining all causal factors with controlled noise.
    Guarantees non-negative demand values.
    """
    base_demand = calculate_base_demand(product)
    store_mult = calculate_store_multiplier(store)
    affinity = calculate_segment_affinity(store, product)
    lifecycle = calculate_lifecycle_factor(product, week)
    seasonality = calculate_seasonality(week)
    festival = calculate_festival_factor(product, week)
    cannibalization = calculate_cannibalization(product, all_products_by_id, week)

    expected_demand = (
        base_demand
        * store_mult
        * affinity
        * lifecycle
        * seasonality
        * festival
        * cannibalization
    )

    if expected_demand <= 0.0:
        return 0.0

    # Controlled Gaussian noise (std dev = 12% of expected demand)
    noise = rng.normal(0.0, 0.12 * expected_demand)
    demand = max(0.0, expected_demand + noise)

    return float(demand)
