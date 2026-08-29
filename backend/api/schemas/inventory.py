"""
Pydantic Schemas for Inventory Endpoints.
"""

from typing import List, Optional
from pydantic import BaseModel, Field

class InventoryRecordSchema(BaseModel):
    store_id: str = Field(..., description="Store ID", example="STORE_01")
    product_id: str = Field(..., description="Product SKU ID", example="PROD_001")
    current_stock: int = Field(..., description="Current available stock units", example=45)
    in_transit_stock: int = Field(0, description="In transit stock units", example=0)
    reserved_stock: int = Field(0, description="Reserved stock units", example=0)
    target_stock_level: Optional[int] = Field(None, description="Target stock level", example=50)
    reorder_point: Optional[int] = Field(None, description="Reorder point threshold", example=20)
    capital_allocated: Optional[float] = Field(None, description="Capital allocated in INR", example=225000.0)
    weeks_of_cover: Optional[float] = Field(None, description="Current weeks of cover", example=4.5)

class InventoryListResponse(BaseModel):
    records: List[InventoryRecordSchema]
    count: int = Field(..., description="Total inventory records matching criteria", json_schema_extra={"example": 1500})
    page: Optional[int] = Field(None, description="Current page number if paginated", json_schema_extra={"example": 1})
    page_size: Optional[int] = Field(None, description="Page size if paginated", json_schema_extra={"example": 50})

class InventorySummaryResponse(BaseModel):
    total_units: int = Field(..., description="Total physical inventory units across chain", example=4612)
    raw_cost_value: float = Field(..., description="Raw dataset total cost value in INR", example=101311600.0)
    operational_cost_value: float = Field(..., description="Operational starting inventory cost value in INR", example=37998800.0)
    total_retail_value: float = Field(..., description="Total retail value in INR", example=125400000.0)
    store_count: int = Field(..., description="Total stores in chain", example=25)
    sku_count: int = Field(..., description="Total SKUs in catalog", example=60)
    capital_budget_limit: float = Field(..., description="Capital budget limit in INR", example=40000000.0)
    capital_headroom: float = Field(..., description="Operational capital headroom in INR", example=2001200.0)
    capital_utilization_pct: float = Field(..., description="Capital utilization percentage", example=95.0)
    four_week_sales_units: Optional[int] = Field(None, description="Units sold over past 4 weeks", example=941)
    four_week_demand_units: Optional[int] = Field(None, description="Total demand units over past 4 weeks", example=947)
    four_week_revenue: Optional[float] = Field(None, description="Revenue earned over past 4 weeks in INR", example=27593500.0)
    four_week_margin: Optional[float] = Field(None, description="Gross margin earned over past 4 weeks in INR", example=5508700.0)
    four_week_fill_rate: Optional[float] = Field(None, description="Fill rate percentage over past 4 weeks", example=99.4)
