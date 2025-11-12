# vintrick-backend/app/models/harvestload_agcode.py

import uuid
from sqlalchemy import Column, String, Float, DateTime, Boolean
from app.core.db import Base

class HarvestLoadAgcode(Base):
    __tablename__ = "harvestload_agcode"

    uid = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    season_year = Column(String(10), nullable=True)
    block_short_name = Column(String(50), nullable=True)
    load_status = Column(String(20), nullable=True)
    load_rec_date = Column(String(30), nullable=True)
    weight_cert_id = Column(String(30), nullable=True)
    delivery_ticket = Column(String(30), nullable=True)
    inbound_container_count = Column(String(10), nullable=True)
    outbound_container_count = Column(String(10), nullable=True)
    harvest_date = Column(String(30), nullable=True)
    truck = Column(String(30), nullable=True)
    trailer_01 = Column(String(30), nullable=True)
    trailer_02 = Column(String(30), nullable=True)
    inbound_container_type = Column(String(30), nullable=True)
    outbound_container_type = Column(String(30), nullable=True)
    deliver_to = Column(String(30), nullable=True)
    intended_use = Column(String(30), nullable=True)
    harvest_type = Column(String(30), nullable=True)
    scale_operator = Column(String(50), nullable=True)
    gross_weight_value = Column(Float, nullable=True)
    gross_weight_unit = Column(String(10), nullable=True)
    tare_weight_value = Column(Float, nullable=True)
    tare_weight_unit = Column(String(10), nullable=True)
    net_weight_value = Column(Float, nullable=True)
    net_weight_unit = Column(String(10), nullable=True)
    last_modified = Column(DateTime, nullable=False)
    synced = Column(Boolean, default=False)