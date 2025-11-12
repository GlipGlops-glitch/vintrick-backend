-- vintrick-backend/tools/SQL/schemas/shipments_schema.sql

-- Main Shipment Table
CREATE TABLE shipments (
    id INT PRIMARY KEY IDENTITY(1,1),
    workOrderNumber NVARCHAR(50) NULL,
    jobNumber NVARCHAR(50) NULL,
    shipmentNumber NVARCHAR(50) NULL,
    type NVARCHAR(50) NULL,
    occurredTime BIGINT NULL,
    modifiedTime BIGINT NULL,
    reference NVARCHAR(50) NULL,
    freightCode NVARCHAR(50) NULL,
    reversed BIT NULL,
    source_id INT NULL,
    destination_id INT NULL,
    dispatchType_id INT NULL,
    carrier_id INT NULL
);

-- Party (Source)
CREATE TABLE shipment_party (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    businessUnit NVARCHAR(100) NULL
);

-- Destination
CREATE TABLE shipment_destination (
    id INT PRIMARY KEY IDENTITY(1,1),
    winery NVARCHAR(100) NULL,
    party_id INT NULL FOREIGN KEY REFERENCES shipment_party(id)
);

-- Dispatch Type
CREATE TABLE shipment_dispatch_type (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL
);

-- Carrier
CREATE TABLE shipment_carrier (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NULL
);

-- Wine Details
CREATE TABLE wine_detail (
    id INT PRIMARY KEY IDENTITY(1,1),
    shipment_id INT NOT NULL FOREIGN KEY REFERENCES shipments(id) ON DELETE CASCADE,
    vessel NVARCHAR(50) NULL,
    batch NVARCHAR(50) NULL,
    volume_unit NVARCHAR(10) NULL,
    volume_value FLOAT NULL,
    loss FLOAT NULL,
    bottlingDetails NVARCHAR(255) NULL,
    wineryBuilding_id INT NULL,
    wineBatch_id INT NULL,
    cost_id INT NULL,
    weight FLOAT NULL
);

-- Wine Batch
CREATE TABLE wine_batch (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    description NVARCHAR(255) NULL,
    vintage NVARCHAR(10) NULL,
    designatedRegion_id INT NULL,
    designatedVariety_id INT NULL,
    designatedProduct_id INT NULL,
    productCategory_id INT NULL,
    program NVARCHAR(100) NULL,
    grading_id INT NULL
);

-- Designated Region
CREATE TABLE designated_region (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    code NVARCHAR(10) NULL
);

-- Designated Variety
CREATE TABLE designated_variety (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL,
    code NVARCHAR(10) NULL
);

-- Designated Product
CREATE TABLE designated_product (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NULL,
    code NVARCHAR(10) NULL
);

-- Product Category
CREATE TABLE product_category (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NULL,
    code NVARCHAR(10) NULL
);

-- Grading
CREATE TABLE grading (
    id INT PRIMARY KEY IDENTITY(1,1),
    scaleId INT NULL,
    scaleName NVARCHAR(100) NULL,
    valueId INT NULL,
    valueName NVARCHAR(100) NULL
);

-- Winery Building
CREATE TABLE winery_building (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NOT NULL
);

-- Wine Cost
CREATE TABLE wine_cost (
    id INT PRIMARY KEY IDENTITY(1,1),
    total FLOAT NULL,
    fruit FLOAT NULL,
    overhead FLOAT NULL,
    storage FLOAT NULL,
    additive FLOAT NULL,
    [bulk] FLOAT NULL,
    packaging FLOAT NULL,
    operation FLOAT NULL,
    freight FLOAT NULL,
    other FLOAT NULL,
    average FLOAT NULL
);

-- WineDetail to Composition (One-to-many)
CREATE TABLE wine_composition (
    id INT PRIMARY KEY IDENTITY(1,1),
    wine_detail_id INT NOT NULL FOREIGN KEY REFERENCES wine_detail(id) ON DELETE CASCADE,
    percentage FLOAT NOT NULL,
    vintage INT NOT NULL,
    block_id INT NULL,
    region_id INT NULL,
    subRegion NVARCHAR(100) NULL,
    variety_id INT NULL
);

-- Block
CREATE TABLE composition_block (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NULL,
    extId NVARCHAR(100) NULL
);

-- Region
CREATE TABLE composition_region (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NULL
);

-- Variety
CREATE TABLE composition_variety (
    id INT PRIMARY KEY IDENTITY(1,1),
    name NVARCHAR(100) NULL
);

-- WineDetail Allocations/metrics (as JSON or text for now)
ALTER TABLE wine_detail ADD allocations NVARCHAR(MAX) NULL;
ALTER TABLE wine_detail ADD metrics NVARCHAR(MAX) NULL;

-- Foreign Key Relationships
ALTER TABLE shipments
    ADD FOREIGN KEY (source_id) REFERENCES shipment_party(id),
        FOREIGN KEY (destination_id) REFERENCES shipment_destination(id),
        FOREIGN KEY (dispatchType_id) REFERENCES shipment_dispatch_type(id),
        FOREIGN KEY (carrier_id) REFERENCES shipment_carrier(id);

ALTER TABLE wine_detail
    ADD FOREIGN KEY (wineryBuilding_id) REFERENCES winery_building(id),
        FOREIGN KEY (wineBatch_id) REFERENCES wine_batch(id),
        FOREIGN KEY (cost_id) REFERENCES wine_cost(id);

ALTER TABLE wine_batch
    ADD FOREIGN KEY (designatedRegion_id) REFERENCES designated_region(id),
        FOREIGN KEY (designatedVariety_id) REFERENCES designated_variety(id),
        FOREIGN KEY (designatedProduct_id) REFERENCES designated_product(id),
        FOREIGN KEY (productCategory_id) REFERENCES product_category(id),
        FOREIGN KEY (grading_id) REFERENCES grading(id);

ALTER TABLE wine_composition
    ADD FOREIGN KEY (block_id) REFERENCES composition_block(id),
        FOREIGN KEY (region_id) REFERENCES composition_region(id),
        FOREIGN KEY (variety_id) REFERENCES composition_variety(id);
