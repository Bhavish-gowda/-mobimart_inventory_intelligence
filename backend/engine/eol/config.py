"""
Configuration & Constants for End-of-Life (EOL) Risk Engine.
Defines business rules, risk scoring weights, risk level thresholds,
and transfer cost parameters.
"""

from typing import Dict

# Store-to-store transfer logistics cost per unit (Rupees)
# Specification Section 7: STORE_TRANSFER_COST_PER_UNIT = ₹500
STORE_TRANSFER_COST_PER_UNIT: float = 500.0

# Target inventory weeks of cover baseline
TARGET_WEEKS_OF_COVER: float = 4.0

# Risk level thresholds for 0.0 - 100.0 risk score
RISK_THRESHOLDS: Dict[str, float] = {
    "LOW": 0.0,
    "MEDIUM": 30.0,
    "HIGH": 60.0,
    "CRITICAL": 80.0,
}

# Configurable weights for EOL risk score components (sums to 1.0)
RISK_WEIGHTS: Dict[str, float] = {
    "lifecycle": 0.30,
    "successor": 0.25,
    "excess_woc": 0.25,
    "demand_decline": 0.20,
}

# Base expected markdown discount percentages by lifecycle stage
STAGE_MARKDOWN_RATES: Dict[str, float] = {
    "Launch": 0.00,
    "Growth": 0.00,
    "Peak": 0.05,
    "Decline": 0.15,
    "EOL": 0.30,
}

# Successor launch proximity penalty windows (in weeks)
IMMINENT_SUCCESSOR_WEEKS: float = 4.0
MODERATE_SUCCESSOR_WEEKS: float = 8.0
