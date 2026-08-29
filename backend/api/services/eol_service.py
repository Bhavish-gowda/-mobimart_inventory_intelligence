"""
EOL Service Layer.
Delegates directly to Phase 3B EOL decision engine (`assess_eol_risk_position`, `run_eol_portfolio_assessment`).
Does NOT duplicate EOL risk scoring or portfolio transfer logic.
"""

from typing import List, Dict, Any, Tuple, Optional
from backend.api.data_loader import (
    load_sales_history_df,
    load_stores_list,
    load_products_list,
    load_inventory_list,
)
from backend.api.errors import ResourceNotFoundException
from backend.engine.eol.decision import (
    assess_eol_risk_position,
    run_eol_portfolio_assessment,
)
from backend.engine.eol.models import EOLRiskAssessment, PortfolioTransferResolution

def get_eol_risk_portfolio(
    current_week: int = 24,
    min_risk_level: str = "MEDIUM",
) -> Tuple[List[EOLRiskAssessment], PortfolioTransferResolution]:
    stores = load_stores_list()
    products = load_products_list()
    inventory_records = load_inventory_list()
    sales_df = load_sales_history_df()

    hist_df = sales_df[sales_df["week_number"] < current_week].copy()

    # Delegate directly to Phase 3B engine
    assessments, portfolio_resolution = run_eol_portfolio_assessment(
        stores=stores,
        products=products,
        inventory_records=inventory_records,
        sales_history_df=hist_df,
        current_week=current_week,
        min_risk_level=min_risk_level,
    )

    return assessments, portfolio_resolution

def assess_single_eol_position(
    store_id: str,
    product_id: str,
    current_week: int = 24,
) -> Optional[EOLRiskAssessment]:
    stores = load_stores_list()
    products = load_products_list()
    inventory_records = load_inventory_list()

    store = next((s for s in stores if s["id"] == store_id), None)
    if not store:
        raise ResourceNotFoundException("Store", store_id)

    product = next((p for p in products if p["id"] == product_id), None)
    if not product:
        raise ResourceNotFoundException("Product", product_id)

    key = f"{store_id}|{product_id}"
    inv_lookup = {f"{rec['store_id']}|{rec['product_id']}": rec for rec in inventory_records}
    inv_rec = inv_lookup.get(key, {"store_id": store_id, "product_id": product_id, "current_stock": 0, "in_transit_stock": 0})

    sales_df = load_sales_history_df()
    hist_df = sales_df[sales_df["week_number"] < current_week].copy()

    assessment = assess_eol_risk_position(
        store=store,
        product=product,
        inventory_record=inv_rec,
        all_stores=stores,
        all_inventory=inventory_records,
        sales_history_df=hist_df,
        current_week=current_week,
    )

    return assessment
