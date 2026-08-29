"""
Product Service Layer.
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.api.data_loader import load_products_list
from backend.api.errors import ResourceNotFoundException

def get_products(
    segment: Optional[str] = None,
    lifecycle_stage: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    products = load_products_list()
    filtered = []

    for p in products:
        if segment and p.get("segment", "").lower() != segment.lower():
            continue
        if lifecycle_stage and p.get("lifecycle_stage", "").lower() != lifecycle_stage.lower():
            continue
        filtered.append(p)

    return filtered, len(filtered)

def get_product_by_id(product_id: str) -> Dict[str, Any]:
    products = load_products_list()
    for p in products:
        if p.get("id") == product_id:
            return p
    raise ResourceNotFoundException(resource_name="Product", resource_id=product_id)
