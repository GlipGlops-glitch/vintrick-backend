# vintrick-backend/app/models/shipment.py

from sqlalchemy import Column, Integer, String, Boolean, BigInteger, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.core.db import Base

class Shipment(Base):
    __tablename__ = "shipments"
    id = Column(Integer, primary_key=True, index=True)
    workOrderNumber = Column(String(50), nullable=True)
    jobNumber = Column(String(50), nullable=True)
    shipmentNumber = Column(String(50), nullable=True)
    type = Column(String(50), nullable=True)
    occurredTime = Column(BigInteger, nullable=True)
    modifiedTime = Column(BigInteger, nullable=True)
    reference = Column(String(50), nullable=True)
    freightCode = Column(String(50), nullable=True)
    reversed = Column(Boolean, nullable=True)

    source_id = Column(Integer, ForeignKey("shipment_party.id"))
    source = relationship("ShipmentParty", foreign_keys=[source_id], back_populates="source_shipments")
    destination_id = Column(Integer, ForeignKey("shipment_destination.id"))
    destination = relationship("ShipmentDestination", foreign_keys=[destination_id], back_populates="destination_shipments")
    dispatchType_id = Column(Integer, ForeignKey("shipment_dispatch_type.id"))
    dispatchType = relationship("ShipmentDispatchType", foreign_keys=[dispatchType_id], back_populates="shipments")
    carrier_id = Column(Integer, ForeignKey("shipment_carrier.id"))
    carrier = relationship("ShipmentCarrier", foreign_keys=[carrier_id], back_populates="shipments")

    wineDetails = relationship("WineDetail", back_populates="shipment", cascade="all, delete-orphan")

class ShipmentParty(Base):
    __tablename__ = "shipment_party"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    businessUnit = Column(String(100), nullable=True)
    source_shipments = relationship("Shipment", foreign_keys="[Shipment.source_id]", back_populates="source")

class ShipmentDestination(Base):
    __tablename__ = "shipment_destination"
    id = Column(Integer, primary_key=True)
    winery = Column(String(100), nullable=True)
    party_id = Column(Integer, ForeignKey("shipment_party.id"))
    party = relationship("ShipmentParty")
    destination_shipments = relationship("Shipment", foreign_keys="[Shipment.destination_id]", back_populates="destination")

class ShipmentDispatchType(Base):
    __tablename__ = "shipment_dispatch_type"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    shipments = relationship("Shipment", back_populates="dispatchType")

class ShipmentCarrier(Base):
    __tablename__ = "shipment_carrier"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    shipments = relationship("Shipment", back_populates="carrier")

class WineDetail(Base):
    __tablename__ = "wine_detail"
    id = Column(Integer, primary_key=True)
    shipment_id = Column(Integer, ForeignKey("shipments.id"))
    vessel = Column(String(50), nullable=True)
    batch = Column(String(50), nullable=True)
    volume_unit = Column(String(10), nullable=True)
    volume_value = Column(Float, nullable=True)
    loss = Column(Float, nullable=True)
    bottlingDetails = Column(String(255), nullable=True)
    weight = Column(Float, nullable=True)

    wineBatch_id = Column(Integer, ForeignKey("wine_batch.id"))
    wineBatch = relationship("WineBatch", back_populates="wine_details")
    wineryBuilding_id = Column(Integer, ForeignKey("winery_building.id"))
    wineryBuilding = relationship("WineryBuilding", back_populates="wine_details")
    cost_id = Column(Integer, ForeignKey("wine_cost.id"))
    cost = relationship("WineCost", back_populates="wine_details")

    shipment = relationship("Shipment", back_populates="wineDetails")
    # Normalized relationships:
    allocations = relationship("Allocation", back_populates="wine_detail", cascade="all, delete-orphan")
    metrics = relationship("Metric", back_populates="wine_detail", cascade="all, delete-orphan")
    composition_items = relationship("CompositionItem", back_populates="wine_detail", cascade="all, delete-orphan")

class Allocation(Base):
    __tablename__ = "allocation"
    id = Column(Integer, primary_key=True)
    wine_detail_id = Column(Integer, ForeignKey("wine_detail.id"))
    type = Column(String(100), nullable=True)
    quantity = Column(Float, nullable=True)
    recipient = Column(String(100), nullable=True)
    # Add more allocation-specific fields as needed
    wine_detail = relationship("WineDetail", back_populates="allocations")

class Metric(Base):
    __tablename__ = "metric"
    id = Column(Integer, primary_key=True)
    wine_detail_id = Column(Integer, ForeignKey("wine_detail.id"))
    metric_type = Column(String(100), nullable=True)
    value = Column(Float, nullable=True)
    unit = Column(String(50), nullable=True)
    # Add more metric-specific fields as needed
    wine_detail = relationship("WineDetail", back_populates="metrics")

class CompositionItem(Base):
    __tablename__ = "composition_item"
    id = Column(Integer, primary_key=True)
    wine_detail_id = Column(Integer, ForeignKey("wine_detail.id"))
    percentage = Column(Float, nullable=True)
    vintage = Column(String(10), nullable=True)
    block_name = Column(String(100), nullable=True)
    block_extId = Column(String(100), nullable=True)
    region_name = Column(String(100), nullable=True)
    subRegion = Column(String(100), nullable=True)
    variety_name = Column(String(100), nullable=True)
    # Add more composition-specific fields as needed
    wine_detail = relationship("WineDetail", back_populates="composition_items")

class WineBatch(Base):
    __tablename__ = "wine_batch"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(String(255), nullable=True)
    vintage = Column(String(10), nullable=True)
    designatedRegion_id = Column(Integer, ForeignKey("designated_region.id"))
    designatedRegion = relationship("DesignatedRegion")
    designatedVariety_id = Column(Integer, ForeignKey("designated_variety.id"))
    designatedVariety = relationship("DesignatedVariety")
    designatedProduct_id = Column(Integer, ForeignKey("designated_product.id"))
    designatedProduct = relationship("DesignatedProduct")
    productCategory_id = Column(Integer, ForeignKey("product_category.id"))
    productCategory = relationship("ProductCategory")
    program = Column(String(100), nullable=True)
    grading_id = Column(Integer, ForeignKey("grading.id"))
    grading = relationship("Grading")
    wine_details = relationship("WineDetail", back_populates="wineBatch")

class DesignatedRegion(Base):
    __tablename__ = "designated_region"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=True)

class DesignatedVariety(Base):
    __tablename__ = "designated_variety"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    code = Column(String(10), nullable=True)

class DesignatedProduct(Base):
    __tablename__ = "designated_product"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    code = Column(String(10), nullable=True)

class ProductCategory(Base):
    __tablename__ = "product_category"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=True)
    code = Column(String(10), nullable=True)

class Grading(Base):
    __tablename__ = "grading"
    id = Column(Integer, primary_key=True)
    scaleId = Column(Integer, nullable=True)
    scaleName = Column(String(100), nullable=True)
    valueId = Column(Integer, nullable=True)
    valueName = Column(String(100), nullable=True)

class WineryBuilding(Base):
    __tablename__ = "winery_building"
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    wine_details = relationship("WineDetail", back_populates="wineryBuilding")

class WineCost(Base):
    __tablename__ = "wine_cost"
    id = Column(Integer, primary_key=True)
    total = Column(Float, nullable=True)
    fruit = Column(Float, nullable=True)
    overhead = Column(Float, nullable=True)
    storage = Column(Float, nullable=True)
    additive = Column(Float, nullable=True)
    bulk = Column(Float, nullable=True)
    packaging = Column(Float, nullable=True)
    operation = Column(Float, nullable=True)
    freight = Column(Float, nullable=True)
    other = Column(Float, nullable=True)
    average = Column(Float, nullable=True)
    wine_details = relationship("WineDetail", back_populates="cost")