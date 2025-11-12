# vintrick-backend/app/schemas/fruitintake.py

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime

class ExtIdentifiableEntity(BaseModel):
    extId: Optional[str] = None
    name: Optional[str] = None
    id: Optional[int] = None

class WineryEntity(BaseModel):
    businessUnit: Optional[str] = None
    name: Optional[str] = None
    id: Optional[int] = None

class Measurement(BaseModel):
    value: Optional[float] = None
    unit: Optional[str] = None

class AnalysisResult(BaseModel):
    name: str
    value: Optional[float] = None

class FruitIntakeBase(BaseModel):
    block: Optional[ExtIdentifiableEntity] = None
    vintage: int
    bookingNumber: Optional[str] = None
    owner: Optional[ExtIdentifiableEntity] = None
    dateOccurred: int
    timeIn: Optional[int] = None
    timeOut: Optional[int] = None
    weighTag: Optional[str] = None
    externalWeighTag: Optional[str] = None
    winery: Optional[WineryEntity] = None
    scale: Optional[ExtIdentifiableEntity] = None
    gross: Optional[Measurement] = None
    tare: Optional[Measurement] = None
    net: Measurement
    jobStatus: Optional[str] = None
    intendedProduct: Optional[ExtIdentifiableEntity] = None
    unitPrice: Optional[Measurement] = None
    metrics: Optional[List[AnalysisResult]] = None
    harvestMethod: Optional[str] = None
    weighMasterText: Optional[str] = None
    carrier: Optional[ExtIdentifiableEntity] = None
    consignmentNote: Optional[str] = None
    driverName: Optional[str] = None
    lastLoad: Optional[bool] = None
    operatorNotes: Optional[str] = None
    truckRegistration: Optional[str] = None
    linkEarliestBooking: Optional[bool] = None

class FruitIntakeCreate(FruitIntakeBase):
    pass

class FruitIntakeUpdate(FruitIntakeBase):
    pass

class FruitIntakeOut(FruitIntakeBase):
    id: int
    last_modified: datetime

    class Config:
        from_attributes = True