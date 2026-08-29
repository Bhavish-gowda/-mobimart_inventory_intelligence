"""
Cached Data Loader Layer for MobiMart API.
Loads static generated CSV datasets once and caches them safely.
Does NOT maintain or leak mutable simulation state across API requests.
"""

from functools import lru_cache
from typing import Dict, List, Any
import pandas as pd
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "generated")

@lru_cache(maxsize=1)
def load_stores_df() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "stores.csv")
    return pd.read_csv(path)

@lru_cache(maxsize=1)
def load_stores_list() -> List[Dict[str, Any]]:
    return load_stores_df().to_dict(orient="records")

@lru_cache(maxsize=1)
def load_products_df() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "products.csv")
    return pd.read_csv(path)

@lru_cache(maxsize=1)
def load_products_list() -> List[Dict[str, Any]]:
    return load_products_df().to_dict(orient="records")

@lru_cache(maxsize=1)
def load_inventory_df() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "inventory.csv")
    return pd.read_csv(path)

@lru_cache(maxsize=1)
def load_inventory_list() -> List[Dict[str, Any]]:
    return load_inventory_df().to_dict(orient="records")

@lru_cache(maxsize=1)
def load_sales_history_df() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "sales_history.csv")
    return pd.read_csv(path)

@lru_cache(maxsize=1)
def load_product_events_df() -> pd.DataFrame:
    path = os.path.join(DATA_DIR, "product_events.csv")
    return pd.read_csv(path)
