# vintrick-backend/app/schemas/shipment.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any

class ShipmentParty(BaseModel):
    id: Optional[int] = None
    name: str
    businessUnit: Optional[str] = None

class ShipmentDestination(BaseModel):
    id: Optional[int] = None
    winery: Optional[str] = None
    party: Optional[ShipmentParty] = None

class ShipmentDispatchType(BaseModel):
    id: Optional[int] = None
    name: str

class ShipmentCarrier(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

class DesignatedRegion(BaseModel):
    id: Optional[int] = None
    name: str
    code: Optional[str] = None

class DesignatedVariety(BaseModel):
    id: Optional[int] = None
    name: str
    code: Optional[str] = None

class DesignatedProduct(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None

class ProductCategory(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    code: Optional[str] = None

class Grading(BaseModel):
    id: Optional[int] = None
    scaleId: Optional[int] = None
    scaleName: Optional[str] = None
    valueId: Optional[int] = None
    valueName: Optional[str] = None

class WineryBuilding(BaseModel):
    id: Optional[int] = None
    name: str

class WineCost(BaseModel):
    id: Optional[int] = None
    total: Optional[float] = None
    fruit: Optional[float] = None
    overhead: Optional[float] = None
    storage: Optional[float] = None
    additive: Optional[float] = None
    bulk: Optional[float] = None
    packaging: Optional[float] = None
    operation: Optional[float] = None
    freight: Optional[float] = None
    other: Optional[float] = None
    average: Optional[float] = None

class CompositionBlock(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    extId: Optional[str] = None

class CompositionRegion(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

class CompositionVariety(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None

class CompositionItem(BaseModel):
    percentage: float
    vintage: int
    block: CompositionBlock
    region: CompositionRegion
    subRegion: Optional[str] = None
    variety: CompositionVariety

class WineBatch(BaseModel):
    id: Optional[int] = None
    name: str
    description: Optional[str] = None
    vintage: Optional[str] = None
    designatedRegion: Optional[DesignatedRegion] = None
    designatedVariety: Optional[DesignatedVariety] = None
    designatedProduct: Optional[DesignatedProduct] = None
    productCategory: Optional[ProductCategory] = None
    program: Optional[str] = None
    grading: Optional[Grading] = None

class WineDetail(BaseModel):
    id: Optional[int] = None
    vessel: Optional[str] = None
    batch: Optional[str] = None
    wineBatch: Optional[WineBatch] = None
    wineryBuilding: Optional[WineryBuilding] = None
    volume: Optional[Dict[str, Any]] = None   # {unit, value}
    loss: Optional[float] = None
    bottlingDetails: Optional[Dict[str, Any]] = None
    cost: Optional[WineCost] = None
    allocations: Optional[List[Any]] = None
    metrics: Optional[List[Any]] = None
    composition: Optional[List[CompositionItem]] = None
    weight: Optional[float] = None

class ShipmentBase(BaseModel):
    workOrderNumber: Optional[str] = None
    jobNumber: Optional[str] = None
    shipmentNumber: Optional[str] = None
    type: Optional[str] = None
    source: Optional[ShipmentParty] = None
    destination: Optional[ShipmentDestination] = None
    occurredTime: Optional[int] = None
    modifiedTime: Optional[int] = None
    wineDetails: Optional[List[WineDetail]] = None
    carrier: Optional[ShipmentCarrier] = None
    reference: Optional[str] = None
    dispatchType: Optional[ShipmentDispatchType] = None
    freightCode: Optional[str] = None
    reversed: Optional[bool] = None

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentOut(ShipmentBase):
    id: int

    class Config:
        from_attributes = True