# vintrick-backend/app/models/fruitintake.py

import uuid
from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, JSON
from app.core.db import Base

class FruitIntake(Base):
    __tablename__ = "fruitintakes"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    uid = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    block_extid = Column(String(50), nullable=True)
    block_name = Column(String(50), nullable=True)
    vintage = Column(Integer, nullable=False)
    bookingNumber = Column(String(50), nullable=True)
    owner_extid = Column(String(50), nullable=True)
    owner_name = Column(String(50), nullable=True)
    dateOccurred = Column(Integer, nullable=False)
    timeIn = Column(Integer, nullable=True)
    timeOut = Column(Integer, nullable=True)
    weighTag = Column(String(100), nullable=True)
    externalWeighTag = Column(String(100), nullable=True)
    winery_bu = Column(String(50), nullable=True)
    winery_name = Column(String(100), nullable=True)
    scale_name = Column(String(100), nullable=True)
    gross_value = Column(Float, nullable=True)
    gross_unit = Column(String(20), nullable=True)
    tare_value = Column(Float, nullable=True)
    tare_unit = Column(String(20), nullable=True)
    net_value = Column(Float, nullable=False)
    net_unit = Column(String(20), nullable=True)
    jobStatus = Column(String(20), nullable=True)
    intendedProduct_name = Column(String(100), nullable=True)
    unitPrice_value = Column(Float, nullable=True)
    unitPrice_unit = Column(String(20), nullable=True)
    metrics = Column(JSON, nullable=True)
    harvestMethod = Column(String(20), nullable=True)
    weighMasterText = Column(String(100), nullable=True)
    carrier_name = Column(String(100), nullable=True)
    carrier_extid = Column(String(50), nullable=True)
    consignmentNote = Column(String(100), nullable=True)
    driverName = Column(String(100), nullable=True)
    lastLoad = Column(Boolean, nullable=True)
    operatorNotes = Column(String(300), nullable=True)
    truckRegistration = Column(String(50), nullable=True)
    linkEarliestBooking = Column(Boolean, nullable=True, default=False)
    # Timestamps
    last_modified = Column(DateTime, nullable=False)
    synced = Column(Boolean, default=False)