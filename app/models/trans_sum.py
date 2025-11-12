# vintrick-backend/app/models/trans_sum.py

from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.db import Base

class VesselDetails(Base):
    __tablename__ = "vessel_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    contentsId = Column(Integer, nullable=True)
    batch = Column(String, nullable=True)
    batchId = Column(Integer, nullable=True)
    volume = Column(Float, nullable=True)
    volumeUnit = Column(String, nullable=True)
    dip = Column(String, nullable=True)
    state = Column(String, nullable=True)
    rawTaxClass = Column(String, nullable=True)
    federalTaxClass = Column(String, nullable=True)
    stateTaxClass = Column(String, nullable=True)
    program = Column(String, nullable=True)

class Vessels(Base):
    __tablename__ = "vessels"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    beforeDetailsId = Column(Integer, ForeignKey("vessel_details.id"), nullable=True)
    afterDetailsId = Column(Integer, ForeignKey("vessel_details.id"), nullable=True)
    volOut = Column(Float, nullable=True)
    volOutUnit = Column(String, nullable=True)
    volIn = Column(Float, nullable=True)
    volInUnit = Column(String, nullable=True)
    beforeDetails = relationship("VesselDetails", foreign_keys=[beforeDetailsId])
    afterDetails = relationship("VesselDetails", foreign_keys=[afterDetailsId])

class LossDetails(Base):
    __tablename__ = "loss_details"
    id = Column(Integer, primary_key=True, autoincrement=True)
    volume = Column(Float, nullable=True)
    volumeUnit = Column(String, nullable=True)
    reason = Column(String, nullable=True)

class Additives(Base):
    __tablename__ = "additives"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=True)
    description = Column(String, nullable=True)

class AdditionOps(Base):
    __tablename__ = "addition_ops"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vesselId = Column(Integer, nullable=True)
    vesselName = Column(String, nullable=True)
    batchId = Column(Integer, nullable=True)
    batchName = Column(String, nullable=True)
    templateId = Column(Integer, nullable=True)
    templateName = Column(String, nullable=True)
    changeToState = Column(String, nullable=True)
    volume = Column(Float, nullable=True)
    amount = Column(Float, nullable=True)
    unit = Column(String, nullable=True)
    lotNumbers = Column(String, nullable=True)
    additiveId = Column(Integer, ForeignKey("additives.id"), nullable=True)
    additive = relationship("Additives", foreign_keys=[additiveId])

class AnalysisOps(Base):
    __tablename__ = "analysis_ops"
    id = Column(Integer, primary_key=True, autoincrement=True)
    vesselId = Column(Integer, nullable=True)
    vesselName = Column(String, nullable=True)
    batchId = Column(Integer, nullable=True)
    batchName = Column(String, nullable=True)
    templateId = Column(Integer, nullable=True)
    templateName = Column(String, nullable=True)
    metrics = relationship("MetricAnalysis", back_populates="analysisOps", cascade="all, delete-orphan")

class MetricAnalysis(Base):
    __tablename__ = "metric_analysis"
    id = Column(Integer, primary_key=True, autoincrement=True)
    analysisOpsId = Column(Integer, ForeignKey("analysis_ops.id"), nullable=True)
    name = Column(String, nullable=True)
    value = Column(Float, nullable=True)
    txtValue = Column(String, nullable=True)
    unit = Column(String, nullable=True)
    analysisOps = relationship("AnalysisOps", back_populates="metrics")

class TransSum(Base):
    __tablename__ = "trans_sum"
    id = Column(Integer, primary_key=True, autoincrement=True)
    formattedDate = Column(String, nullable=True)
    date = Column(Integer, nullable=True)
    operationId = Column(Integer, nullable=True)
    operationTypeId = Column(Integer, nullable=True)
    operationTypeName = Column(String, nullable=True)
    subOperationTypeId = Column(Integer, nullable=True)
    subOperationTypeName = Column(String, nullable=True)
    workorder = Column(String, nullable=True)
    jobNumber = Column(String, nullable=True)
    treatment = Column(String, nullable=True)
    assignedBy = Column(String, nullable=True)
    completedBy = Column(String, nullable=True)
    winery = Column(String, nullable=True)
    fromVesselId = Column(Integer, ForeignKey("vessels.id"), nullable=True)
    toVesselId = Column(Integer, ForeignKey("vessels.id"), nullable=True)
    lossDetailsId = Column(Integer, ForeignKey("loss_details.id"), nullable=True)
    additionOpsId = Column(Integer, ForeignKey("addition_ops.id"), nullable=True)
    analysisOpsId = Column(Integer, ForeignKey("analysis_ops.id"), nullable=True)
    additionalDetails = Column(String, nullable=True)

    fromVessel = relationship("Vessels", foreign_keys=[fromVesselId])
    toVessel = relationship("Vessels", foreign_keys=[toVesselId])
    lossDetails = relationship("LossDetails", foreign_keys=[lossDetailsId])
    additionOps = relationship("AdditionOps", foreign_keys=[additionOpsId])
    analysisOps = relationship("AnalysisOps", foreign_keys=[analysisOpsId])