"""
Product generator for MobiMart.
Generates exactly 60 smartphone SKUs with realistic cost/retail prices, margins,
lifecycle stages, and predecessor-successor launch relationships.
"""

from typing import Dict, List, Any, Optional
import numpy as np
from backend.engine.generator.config import SEGMENT_PRICING

BRANDS = ["Nova", "Apex", "Zenith", "Vortex", "Aura", "Titan"]

SEGMENT_COUNTS = {
    "Budget": 18,
    "Mid-Range": 20,
    "Premium": 14,
    "Flagship": 8,
}

def generate_products(rng: np.random.Generator) -> List[Dict[str, Any]]:
    """
    Generate exactly 60 products across 4 price segments.
    Assign lifecycle stages, pricing, margins, markdown %, and successor links.
    """
    products: List[Dict[str, Any]] = []
    prod_id_counter = 1

    # Segment definitions with specific models and successors
    segment_templates = {
        "Budget": [
            ("Nova Go 4G", 6500.0, 7800.0, "Peak", None, None, 1.0, False),
            ("Nova Go 5G", 8500.0, 10200.0, "Growth", None, None, 1.0, False),
            ("Apex Lite 10", 7200.0, 8700.0, "Decline", "PROD_004", 22, 1.0, False),  # Successor is Apex Lite 11
            ("Apex Lite 11", 7800.0, 9400.0, "Launch", None, None, 1.0, False),
            ("Vortex Spark A1", 5800.0, 6900.0, "EOL", "PROD_006", 15, 1.0, False),
            ("Vortex Spark A2", 6200.0, 7500.0, "Peak", None, None, 1.0, False),
            ("Aura Play 3", 9000.0, 10900.0, "Peak", None, None, 1.0, False),
            ("Zenith C1", 9500.0, 11500.0, "Growth", None, None, 1.0, False),
            ("Titan Mini 1", 11000.0, 13400.0, "Peak", None, None, 1.0, False),
            ("Nova Go Max", 12000.0, 14600.0, "Growth", None, None, 1.0, False),
            ("Vortex Spark Pro", 10500.0, 12800.0, "Decline", "PROD_012", 30, 0.65, True), # Rumoured successor
            ("Vortex Spark Pro 2", 11200.0, 13700.0, "Launch", None, None, 0.65, True),
            ("Apex Lite Prime", 8200.0, 9900.0, "Peak", None, None, 1.0, False),
            ("Zenith C2", 10200.0, 12400.0, "Growth", None, None, 1.0, False),
            ("Aura Play 4", 9800.0, 11900.0, "Launch", None, None, 1.0, False),
            ("Titan Mini 2", 11500.0, 14000.0, "Growth", None, None, 1.0, False),
            ("Nova Core 1", 6800.0, 8100.0, "EOL", None, None, 1.0, False),
            ("Vortex Beat 2", 7400.0, 8900.0, "Decline", None, None, 1.0, False),
        ],
        "Mid-Range": [
            ("Apex Note 11", 14000.0, 17200.0, "Decline", "PROD_020", 18, 1.0, False),
            ("Apex Note 12", 15500.0, 19100.0, "Peak", None, None, 1.0, False),
            ("Zenith Zone 7", 18000.0, 22200.0, "Peak", None, None, 1.0, False),
            ("Zenith Zone 8", 20500.0, 25300.0, "Growth", None, None, 1.0, False),
            ("Nova Pro 10", 22000.0, 27100.0, "Decline", "PROD_024", 25, 1.0, False),
            ("Nova Pro 11", 24500.0, 30200.0, "Launch", None, None, 1.0, False),
            ("Aura Pulse 5", 16500.0, 20300.0, "Peak", None, None, 1.0, False),
            ("Vortex Velocity 3", 19000.0, 23400.0, "Peak", None, None, 1.0, False),
            ("Titan Edge 2", 26000.0, 32100.0, "Growth", None, None, 1.0, False),
            ("Apex Note 12 Pro", 28000.0, 34600.0, "Growth", None, None, 1.0, False),
            ("Zenith Zone 8 Ultra", 30000.0, 37100.0, "Peak", None, None, 1.0, False),
            ("Nova Pro 10 Plus", 25000.0, 30900.0, "EOL", None, None, 1.0, False),
            ("Aura Pulse 6", 17500.0, 21600.0, "Growth", None, None, 1.0, False),
            ("Vortex Velocity 4", 21000.0, 25900.0, "Launch", None, None, 1.0, False),
            ("Titan Edge 2 SE", 23000.0, 28400.0, "Peak", None, None, 1.0, False),
            ("Apex Speed X", 16000.0, 19700.0, "Decline", "PROD_035", 35, 0.55, True), # Rumoured
            ("Apex Speed X2", 17200.0, 21200.0, "Launch", None, None, 0.55, True),
            ("Zenith Zone Lite", 14500.0, 17900.0, "Peak", None, None, 1.0, False),
            ("Nova Style 5G", 19500.0, 24000.0, "Growth", None, None, 1.0, False),
            ("Aura Pulse Pro", 27000.0, 33300.0, "Peak", None, None, 1.0, False),
        ],
        "Premium": [
            ("Zenith Ultra 23", 38000.0, 47500.0, "Decline", "PROD_040", 12, 1.0, False),
            ("Zenith Ultra 24", 42000.0, 52600.0, "Peak", None, None, 1.0, False),
            ("Apex Master 5", 46000.0, 57600.0, "Peak", None, None, 1.0, False),
            ("Apex Master 6", 50000.0, 62700.0, "Growth", None, None, 1.0, False),
            ("Titan Pro Fold 1", 54000.0, 67800.0, "Decline", "PROD_044", 28, 1.0, False),
            ("Titan Pro Fold 2", 58000.0, 72900.0, "Launch", None, None, 1.0, False),
            ("Nova Flagship Lite", 35000.0, 43700.0, "Peak", None, None, 1.0, False),
            ("Aura Vantage 1", 40000.0, 50100.0, "Peak", None, None, 1.0, False),
            ("Vortex Phantom 8", 44000.0, 55100.0, "Growth", None, None, 1.0, False),
            ("Zenith Ultra 24 Plus", 48000.0, 60200.0, "Growth", None, None, 1.0, False),
            ("Apex Master 6 Pro", 52000.0, 65300.0, "Launch", None, None, 1.0, False),
            ("Aura Vantage 2", 43000.0, 53900.0, "Growth", None, None, 1.0, False),
            ("Nova Flagship SE", 37000.0, 46300.0, "Decline", "PROD_052", 38, 0.45, True), # Rumoured
            ("Nova Flagship SE 2", 39000.0, 48900.0, "Launch", None, None, 0.45, True),
        ],
        "Flagship": [
            ("Titan Fold Ultra 1", 72000.0, 92200.0, "Decline", "PROD_056", 16, 1.0, False),
            ("Titan Fold Ultra 2", 82000.0, 105000.0, "Peak", None, None, 1.0, False),
            ("Zenith Monarch 14", 90000.0, 115200.0, "Decline", "PROD_058", 24, 1.0, False),
            ("Zenith Monarch 15", 102000.0, 130600.0, "Growth", None, None, 1.0, False),
            ("Apex Sovereign 1", 108000.0, 138300.0, "Decline", "PROD_060", 42, 0.50, True), # Rumoured flagship launch!
            ("Apex Sovereign 2", 118000.0, 149500.0, "Launch", None, None, 0.50, True),
            ("Aura Legend Fold", 78000.0, 99800.0, "Peak", None, None, 1.0, False),
            ("Vortex Eclipse Pro", 85000.0, 108800.0, "Growth", None, None, 1.0, False),
        ],
    }

    markdown_by_stage = {
        "Launch": 0.00,
        "Growth": 0.00,
        "Peak": 0.00,
        "Decline": 0.12,
        "EOL": 0.28,
    }

    launch_week_by_stage = {
        "Launch": 42,
        "Growth": 25,
        "Peak": 10,
        "Decline": 1,
        "EOL": -15, # Launched prior to simulated year
    }

    for segment, items in segment_templates.items():
        for item in items:
            name, cost_price, retail_price, stage, successor_id, successor_week, conf, is_rumour = item
            brand = name.split()[0]
            prod_id = f"PROD_{prod_id_counter:03d}"
            margin = retail_price - cost_price
            margin_pct = round(margin / retail_price, 4)

            product_entry = {
                "id": prod_id,
                "brand": brand,
                "model_name": name,
                "segment": segment,
                "cost_price": round(cost_price, 2),
                "retail_price": round(retail_price, 2),
                "margin": round(margin, 2),
                "margin_pct": margin_pct,
                "launch_week": launch_week_by_stage[stage],
                "lifecycle_stage": stage,
                "markdown_percentage": markdown_by_stage[stage],
                "successor_product_id": successor_id,
                "expected_successor_week": successor_week,
                "launch_confidence": conf,
                "is_rumoured": is_rumour,
            }
            products.append(product_entry)
            prod_id_counter += 1

    return products
