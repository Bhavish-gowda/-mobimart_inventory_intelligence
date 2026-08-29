"""
Configuration constants and parameters for MobiMart Synthetic Data Generator.
All random generation must use RANDOM_SEED to ensure 100% deterministic reproducibility.
"""

from typing import Dict, List, Tuple

# Deterministic Seed
RANDOM_SEED: int = 42

# Scale Constants
NUM_STORES: int = 25
NUM_PRODUCTS: int = 60
NUM_WEEKS: int = 52

# Product Segment Price Ranges (Cost Price, Retail Price Range) in INR
SEGMENT_PRICING: Dict[str, Tuple[float, float, float, float]] = {
    # Segment: (min_cost, max_cost, min_margin_pct, max_margin_pct)
    "Budget": (5000.0, 12000.0, 0.15, 0.22),
    "Mid-Range": (12000.0, 32000.0, 0.18, 0.25),
    "Premium": (32000.0, 62000.0, 0.20, 0.28),
    "Flagship": (65000.0, 120000.0, 0.22, 0.32),
}

# Base Weekly Chain Demand per Segment (units/week across all stores)
SEGMENT_BASE_DEMAND: Dict[str, Tuple[float, float]] = {
    "Budget": (30.0, 60.0),
    "Mid-Range": (15.0, 35.0),
    "Premium": (8.0, 18.0),
    "Flagship": (3.0, 10.0),
}

# Festive Event Weeks (1-indexed 1..52)
FESTIVE_WEEKS: Dict[int, str] = {
    41: "Dussehra",
    42: "Diwali",
    52: "New Year / Year-End Sale",
}

# Festive Multipliers per Segment
# Budget & Mid-Range see higher relative volume surges during Indian festivals
FESTIVE_MULTIPLIERS: Dict[str, Dict[str, float]] = {
    "Dussehra": {
        "Budget": 3.0,
        "Mid-Range": 2.8,
        "Premium": 2.2,
        "Flagship": 1.8,
    },
    "Diwali": {
        "Budget": 3.5,
        "Mid-Range": 3.2,
        "Premium": 2.5,
        "Flagship": 2.0,
    },
    "New Year / Year-End Sale": {
        "Budget": 1.8,
        "Mid-Range": 1.8,
        "Premium": 1.6,
        "Flagship": 1.5,
    },
}

# Lost Sale Probabilities by Price Tier (Customer willingness to wait/transfer)
LOST_SALE_PROBABILITIES: Dict[str, float] = {
    "Budget": 0.80,    # Customer buys alternative immediately if out of stock
    "Mid-Range": 0.65,
    "Premium": 0.45,
    "Flagship": 0.30,   # Customer willing to wait for transfer/replenishment
}

# Goodwill Penalty Factor (% of product margin lost as customer dissatisfaction)
GOODWILL_PENALTY_FACTORS: Dict[str, float] = {
    "Budget": 0.15,
    "Mid-Range": 0.12,
    "Premium": 0.08,
    "Flagship": 0.05,
}

# Inter-store transfer cost per unit by distance classification (INR)
TRANSFER_COST_MATRIX: Dict[Tuple[str, str], float] = {
    ("Same_City", "Same_City"): 300.0,
    ("Bangalore", "Tier2"): 500.0,
    ("Tier2", "Tier3"): 800.0,
    ("Default", "Default"): 600.0,
}
