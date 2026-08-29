"""
Allocation Engine Configuration Constants & Financial Weights.
Centralizes capital budget caps, target weeks of cover, lost-sale penalty factors,
and unit handling logistics costs.
"""

from typing import Dict

# Chain-wide Hard Capital Budget Cap (INR)
MAX_CAPITAL_BUDGET: float = 40000000.0  # ₹4,00,00,000 (₹4 Crore)

# Inventory Cover Guidelines
TARGET_WEEKS_OF_COVER: float = 3.5
MAX_ALLOWABLE_WEEKS_OF_COVER: float = 8.0

# Logistics & Handling Costs per Unit (INR)
WAREHOUSE_ALLOCATION_COST_PER_UNIT: float = 250.0  # Warehouse -> Store allocation
STORE_TRANSFER_COST_PER_UNIT: float = 500.0         # Store -> Store inter-city transfer (midpoint of ₹300-₹800 range)

# Backward-compatibility alias
UNIT_ALLOCATION_COST: float = WAREHOUSE_ALLOCATION_COST_PER_UNIT

# Lost Sale Immediate Purchase Loss Probability by Segment
LOST_SALE_PROBABILITIES: Dict[str, float] = {
    "Budget": 0.80,
    "Mid-Range": 0.65,
    "Premium": 0.45,
    "Flagship": 0.30,
}

# Goodwill Dissatisfaction Loss Factor (% of Unit Margin)
GOODWILL_PENALTY_FACTORS: Dict[str, float] = {
    "Budget": 0.15,
    "Mid-Range": 0.12,
    "Premium": 0.08,
    "Flagship": 0.05,
}
