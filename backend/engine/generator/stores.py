"""
Store profile generator for MobiMart.
Generates exactly 25 Karnataka stores with realistic location, catchment, income, and category segment affinities.
"""

from typing import Dict, List, Any
import numpy as np

def generate_stores(rng: np.random.Generator) -> List[Dict[str, Any]]:
    """
    Generate 25 realistic store profiles across Karnataka.
    8 in Bangalore, 17 in Tier-2/3 cities (Mysore, Hubli, Tumkur, Davangere, Belgaum, Mangalore).
    """
    raw_stores_data = [
        # Bangalore Stores (8)
        {"id": "STORE_01", "name": "MobiMart Indiranagar 100ft Rd", "city": "Bangalore", "location_type": "High Street", "size": 3500, "footfall": 65000, "income": 1.85, "affinities": {"Budget": 0.40, "Mid-Range": 0.80, "Premium": 1.80, "Flagship": 2.20}},
        {"id": "STORE_02", "name": "MobiMart Phoenix Marketcity", "city": "Bangalore", "location_type": "Premium Mall", "size": 4200, "footfall": 85000, "income": 1.95, "affinities": {"Budget": 0.35, "Mid-Range": 0.75, "Premium": 1.90, "Flagship": 2.30}},
        {"id": "STORE_03", "name": "MobiMart Koramangala 80ft Rd", "city": "Bangalore", "location_type": "High Street", "size": 3200, "footfall": 58000, "income": 1.75, "affinities": {"Budget": 0.45, "Mid-Range": 0.90, "Premium": 1.70, "Flagship": 1.95}},
        {"id": "STORE_04", "name": "MobiMart Whitefield Forum Mall", "city": "Bangalore", "location_type": "Premium Mall", "size": 3800, "footfall": 72000, "income": 1.80, "affinities": {"Budget": 0.40, "Mid-Range": 0.85, "Premium": 1.75, "Flagship": 2.10}},
        {"id": "STORE_05", "name": "MobiMart Jayanagar 4th Block", "city": "Bangalore", "location_type": "High Street", "size": 3000, "footfall": 52000, "income": 1.50, "affinities": {"Budget": 0.60, "Mid-Range": 1.10, "Premium": 1.40, "Flagship": 1.50}},
        {"id": "STORE_06", "name": "MobiMart Malleshwaram Sampige", "city": "Bangalore", "location_type": "High Street", "size": 2800, "footfall": 48000, "income": 1.40, "affinities": {"Budget": 0.65, "Mid-Range": 1.20, "Premium": 1.30, "Flagship": 1.35}},
        {"id": "STORE_07", "name": "MobiMart HSR Layout Sector 1", "city": "Bangalore", "location_type": "High Street", "size": 2900, "footfall": 45000, "income": 1.60, "affinities": {"Budget": 0.50, "Mid-Range": 1.00, "Premium": 1.55, "Flagship": 1.70}},
        {"id": "STORE_08", "name": "MobiMart Majestic Bus Stand Rd", "city": "Bangalore", "location_type": "Mass Market", "size": 2200, "footfall": 80000, "income": 0.95, "affinities": {"Budget": 1.80, "Mid-Range": 1.40, "Premium": 0.60, "Flagship": 0.40}},

        # Mysore Stores (3)
        {"id": "STORE_09", "name": "MobiMart Devaraja Market Mysore", "city": "Mysore", "location_type": "Tier-2 Center", "size": 2400, "footfall": 38000, "income": 1.15, "affinities": {"Budget": 1.20, "Mid-Range": 1.30, "Premium": 0.90, "Flagship": 0.70}},
        {"id": "STORE_10", "name": "MobiMart Jayalakshmipuram", "city": "Mysore", "location_type": "Tier-2 Center", "size": 2600, "footfall": 32000, "income": 1.30, "affinities": {"Budget": 0.90, "Mid-Range": 1.25, "Premium": 1.15, "Flagship": 0.95}},
        {"id": "STORE_11", "name": "MobiMart VV Mohalla Mysore", "city": "Mysore", "location_type": "High Street", "size": 2500, "footfall": 35000, "income": 1.25, "affinities": {"Budget": 0.95, "Mid-Range": 1.30, "Premium": 1.10, "Flagship": 0.85}},

        # Hubli Stores (3)
        {"id": "STORE_12", "name": "MobiMart CBT Road Hubli", "city": "Hubli", "location_type": "Tier-2 Center", "size": 2200, "footfall": 36000, "income": 1.05, "affinities": {"Budget": 1.40, "Mid-Range": 1.35, "Premium": 0.75, "Flagship": 0.55}},
        {"id": "STORE_13", "name": "MobiMart Vidyanagar Hubli", "city": "Hubli", "location_type": "Tier-2 Center", "size": 2300, "footfall": 30000, "income": 1.10, "affinities": {"Budget": 1.30, "Mid-Range": 1.30, "Premium": 0.80, "Flagship": 0.60}},
        {"id": "STORE_14", "name": "MobiMart Gokul Road Hubli", "city": "Hubli", "location_type": "Tier-2 Center", "size": 2100, "footfall": 28000, "income": 1.00, "affinities": {"Budget": 1.50, "Mid-Range": 1.30, "Premium": 0.70, "Flagship": 0.50}},

        # Tumkur Stores (3)
        {"id": "STORE_15", "name": "MobiMart BH Road Tumkur", "city": "Tumkur", "location_type": "Tier-3 Center", "size": 1800, "footfall": 25000, "income": 0.85, "affinities": {"Budget": 1.75, "Mid-Range": 1.40, "Premium": 0.55, "Flagship": 0.35}},
        {"id": "STORE_16", "name": "MobiMart SS Puram Tumkur", "city": "Tumkur", "location_type": "Tier-3 Center", "size": 1900, "footfall": 22000, "income": 0.90, "affinities": {"Budget": 1.65, "Mid-Range": 1.35, "Premium": 0.60, "Flagship": 0.40}},
        {"id": "STORE_17", "name": "MobiMart Kyatsandra Tumkur", "city": "Tumkur", "location_type": "Tier-3 Center", "size": 1600, "footfall": 18000, "income": 0.75, "affinities": {"Budget": 1.90, "Mid-Range": 1.25, "Premium": 0.45, "Flagship": 0.25}},

        # Davangere Stores (3)
        {"id": "STORE_18", "name": "MobiMart PB Road Davangere", "city": "Davangere", "location_type": "Tier-3 Center", "size": 1800, "footfall": 24000, "income": 0.80, "affinities": {"Budget": 1.80, "Mid-Range": 1.35, "Premium": 0.50, "Flagship": 0.30}},
        {"id": "STORE_19", "name": "MobiMart MCC B Block Davangere", "city": "Davangere", "location_type": "Tier-3 Center", "size": 2000, "footfall": 26000, "income": 0.95, "affinities": {"Budget": 1.55, "Mid-Range": 1.40, "Premium": 0.65, "Flagship": 0.45}},
        {"id": "STORE_20", "name": "MobiMart Mandipet Davangere", "city": "Davangere", "location_type": "Tier-3 Center", "size": 1600, "footfall": 20000, "income": 0.70, "affinities": {"Budget": 2.10, "Mid-Range": 1.20, "Premium": 0.40, "Flagship": 0.20}},

        # Belgaum Stores (3)
        {"id": "STORE_21", "name": "MobiMart College Road Belgaum", "city": "Belgaum", "location_type": "Tier-2 Center", "size": 2300, "footfall": 31000, "income": 1.10, "affinities": {"Budget": 1.30, "Mid-Range": 1.35, "Premium": 0.85, "Flagship": 0.60}},
        {"id": "STORE_22", "name": "MobiMart Tilakwadi Belgaum", "city": "Belgaum", "location_type": "Tier-2 Center", "size": 2100, "footfall": 27000, "income": 1.05, "affinities": {"Budget": 1.35, "Mid-Range": 1.30, "Premium": 0.80, "Flagship": 0.55}},
        {"id": "STORE_23", "name": "MobiMart Khade Bazar Belgaum", "city": "Belgaum", "location_type": "Mass Market", "size": 2000, "footfall": 34000, "income": 0.95, "affinities": {"Budget": 1.60, "Mid-Range": 1.35, "Premium": 0.65, "Flagship": 0.40}},

        # Mangalore Stores (2)
        {"id": "STORE_24", "name": "MobiMart Hampankatta Mangalore", "city": "Mangalore", "location_type": "Tier-2 Center", "size": 2600, "footfall": 36000, "income": 1.35, "affinities": {"Budget": 0.85, "Mid-Range": 1.20, "Premium": 1.30, "Flagship": 1.10}},
        {"id": "STORE_25", "name": "MobiMart MG Road Mangalore", "city": "Mangalore", "location_type": "High Street", "size": 2700, "footfall": 39000, "income": 1.40, "affinities": {"Budget": 0.80, "Mid-Range": 1.15, "Premium": 1.35, "Flagship": 1.20}},
    ]

    stores = []
    for s in raw_stores_data:
        store_entry = {
            "id": s["id"],
            "name": s["name"],
            "city": s["city"],
            "location_type": s["location_type"],
            "store_size_sqft": s["size"],
            "monthly_footfall": s["footfall"],
            "income_index": s["income"],
            "budget_affinity": s["affinities"]["Budget"],
            "mid_range_affinity": s["affinities"]["Mid-Range"],
            "premium_affinity": s["affinities"]["Premium"],
            "flagship_affinity": s["affinities"]["Flagship"],
        }
        stores.append(store_entry)

    return stores
