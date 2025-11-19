from pydantic import BaseModel, Field
from typing import List, Literal, Optional, Any


class LyrInfoInCtlgSave(BaseModel):
    layer_id: str
    points_color: str = Field(
        ..., description="Color name for the layer points, e.g., 'red'"
    )


class UserId(BaseModel):
    user_id: str


class CtlgMetaData(UserId):
    prdcer_ctlg_name: str
    ctlg_description: str
    total_records: int


class ViewportParams(BaseModel):
    top_lng: float
    top_lat: float
    bottom_lng: float
    bottom_lat: float
    zoom_level: int
    population: Optional[bool]
    income: Optional[bool]


class CtlgItems(CtlgMetaData):
    lyrs: List[LyrInfoInCtlgSave] = Field(..., description="list of layer objects.")
    display_elements: dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible field for frontend to store arbitrary key-value pairs",
    )
    intelligence_viewport: ViewportParams = Field(
        ...,
        description="Flexible field for frontend to store arbitrary key-value pairs for intelligence viewport",
    )


class ResUserCatalogInfo(CtlgMetaData):
    prdcer_ctlg_id: str
    thumbnail_url: str


class ResPrdcerCtlg(ResUserCatalogInfo):
    lyrs: List[LyrInfoInCtlgSave] = Field(..., description="list of layer objects.")
    display_elements: dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible field for frontend to store arbitrary key-value pairs",
    )
    intelligence_viewport: dict[str, Any] = Field(
        default_factory=dict,
        description="Flexible field for frontend to store arbitrary key-value pairs for intelligence viewport",
    )


class BooleanQuery(BaseModel):
    boolean_query: Optional[str] = ""


class Geometry(BaseModel):
    type: Literal["Point", "Polygon", "MultiPolygon"]
    coordinates: Any


class Feature(BaseModel):
    type: Literal["Feature"]
    properties: dict
    geometry: Geometry


class PurchaseItem(UserId):
    city_name: str
    country_name: str
    cost: int
    expiration: Optional[str] = None
    explanation: Optional[str] = None
    is_currently_owned: Optional[bool] = None
    free_as_part_of_package: Optional[bool] = None


class ReportPurchaseItem(PurchaseItem):
    report_tier: str
    report_potential_business_type: Optional[str] = ""


class IntelligencePurchaseItem(PurchaseItem):
    intelligence_name: str


class DatasetPurchaseItem(PurchaseItem):
    dataset_name: str


class TotalPurchaseItems(BaseModel):
    total_cost: int
    report_purchase_items: List[ReportPurchaseItem] = []
    intelligence_purchase_items: List[IntelligencePurchaseItem] = []
    dataset_purchase_items: List[DatasetPurchaseItem] = []