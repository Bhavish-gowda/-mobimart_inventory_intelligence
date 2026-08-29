"""
Store Service Layer.
"""

from typing import List, Dict, Any, Optional, Tuple
from backend.api.data_loader import load_stores_list

def get_stores(
    city: Optional[str] = None,
    location_type: Optional[str] = None,
) -> Tuple[List[Dict[str, Any]], int]:
    stores = load_stores_list()
    filtered = []

    for s in stores:
        if city and s.get("city", "").lower() != city.lower():
            continue
        if location_type and s.get("location_type", "").lower() != location_type.lower():
            continue
        filtered.append(s)

    return filtered, len(filtered)

def get_store_by_id(store_id: str) -> Dict[str, Any]:
    stores = load_stores_list()
    for s in stores:
        if s.get("id") == store_id:
            return s
    from backend.api.errors import ResourceNotFoundException
    raise ResourceNotFoundException(resource_name="Store", resource_id=store_id)
