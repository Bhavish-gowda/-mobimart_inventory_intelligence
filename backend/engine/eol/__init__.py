"""
MobiMart End-of-Life (EOL) Risk Engine Package.
Provides risk scoring, markdown economics, store transfer economics, hold economics,
option decision optimization, non-LLM explanation generation, and aggregate risk summaries.
"""

from backend.engine.eol.models import (
    EOLActionOption,
    EOLRiskAssessment,
    EOLInventorySummary,
)
from backend.engine.eol.risk import calculate_eol_risk_score
from backend.engine.eol.markdown import evaluate_markdown_option
from backend.engine.eol.transfer import evaluate_transfer_option
from backend.engine.eol.hold import evaluate_hold_option
from backend.engine.eol.decision import assess_eol_risk_position
from backend.engine.eol.summary import generate_eol_summary

__all__ = [
    "EOLActionOption",
    "EOLRiskAssessment",
    "EOLInventorySummary",
    "calculate_eol_risk_score",
    "evaluate_markdown_option",
    "evaluate_transfer_option",
    "evaluate_hold_option",
    "assess_eol_risk_position",
    "generate_eol_summary",
]
