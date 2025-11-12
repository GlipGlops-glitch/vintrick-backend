# vintrick-backend/app/schemas/trans_sum.py

from pydantic import BaseModel, field_validator
from typing import Optional, List

class VesselDetailsOut(BaseModel):
    id: Optional[int] = None
    contentsId: Optional[int] = None
    batch: Optional[str] = None
    batchId: Optional[int] = None
    volume: Optional[float] = None
    volumeUnit: Optional[str] = None
    dip: Optional[str] = None
    state: Optional[str] = None
    rawTaxClass: Optional[str] = None
    federalTaxClass: Optional[str] = None
    stateTaxClass: Optional[str] = None
    program: Optional[str] = None

class VesselsOut(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    beforeDetailsId: Optional[int] = None
    afterDetailsId: Optional[int] = None
    volOut: Optional[float] = None
    volOutUnit: Optional[str] = None
    volIn: Optional[float] = None
    volInUnit: Optional[str] = None
    beforeDetails: Optional[VesselDetailsOut] = None
    afterDetails: Optional[VesselDetailsOut] = None

class LossDetailsOut(BaseModel):
    id: Optional[int] = None
    volume: Optional[float] = None
    volumeUnit: Optional[str] = None
    reason: Optional[str] = None

class AdditivesOut(BaseModel):
    id: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None

class AdditionOpsOut(BaseModel):
    id: Optional[int] = None
    vesselId: Optional[int] = None
    vesselName: Optional[str] = None
    batchId: Optional[int] = None
    batchName: Optional[str] = None
    templateId: Optional[int] = None
    templateName: Optional[str] = None
    changeToState: Optional[str] = None
    volume: Optional[float] = None
    amount: Optional[float] = None
    unit: Optional[str] = None
    lotNumbers: Optional[str] = None
    additiveId: Optional[int] = None
    additive: Optional[AdditivesOut] = None

class MetricAnalysisOut(BaseModel):
    id: Optional[int] = None
    analysisOpsId: Optional[int] = None
    name: Optional[str] = None
    value: Optional[float] = None
    txtValue: Optional[str] = None
    unit: Optional[str] = None

class AnalysisOpsOut(BaseModel):
    id: Optional[int] = None
    vesselId: Optional[int] = None
    vesselName: Optional[str] = None
    batchId: Optional[int] = None
    batchName: Optional[str] = None
    templateId: Optional[int] = None
    templateName: Optional[str] = None
    metrics: Optional[List[MetricAnalysisOut]] = None

class TransSumOut(BaseModel):
    id: int
    formattedDate: Optional[str] = None
    date: Optional[int] = None
    operationId: Optional[int] = None
    operationTypeId: Optional[int] = None
    operationTypeName: Optional[str] = None
    subOperationTypeId: Optional[int] = None
    subOperationTypeName: Optional[str] = None
    workorder: Optional[str] = None
    jobNumber: Optional[str] = None
    treatment: Optional[str] = None
    assignedBy: Optional[str] = None
    completedBy: Optional[str] = None
    winery: Optional[str] = None
    fromVessel: Optional[VesselsOut] = None
    toVessel: Optional[VesselsOut] = None
    lossDetails: Optional[LossDetailsOut] = None
    additionOps: Optional[AdditionOpsOut] = None
    analysisOps: Optional[AnalysisOpsOut] = None
    additionalDetails: Optional[str] = None

    class Config:
        from_attributes = True

class TransSumCreate(BaseModel):
    formattedDate: Optional[str] = None
    date: Optional[int] = None
    operationId: Optional[int] = None
    operationTypeId: Optional[int] = None
    operationTypeName: Optional[str] = None
    subOperationTypeId: Optional[int] = None
    subOperationTypeName: Optional[str] = None
    workorder: Optional[str] = None
    jobNumber: Optional[str] = None
    treatment: Optional[str] = None
    assignedBy: Optional[str] = None
    completedBy: Optional[str] = None
    winery: Optional[str] = None
    fromVessel: Optional[VesselsOut] = None
    toVessel: Optional[VesselsOut] = None
    lossDetails: Optional[LossDetailsOut] = None
    additionOps: Optional[AdditionOpsOut] = None
    analysisOps: Optional[AnalysisOpsOut] = None
    additionalDetails: Optional[str] = None

    @field_validator('jobNumber', mode='before')
    def coerce_job_number(cls, v):
        if v is not None:
            return str(v)
        return v

    class Config:
        from_attributes = True