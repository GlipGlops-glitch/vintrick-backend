-- Transactions table
CREATE TABLE transactions (
    ts_id VARCHAR(36) PRIMARY KEY,
    ts_operationId INT,
    ts_operationTypeId INT,
    ts_operationTypeName VARCHAR(100),
    ts_subOperationId INT,
    ts_subOperationTypeName VARCHAR(100),
    ts_formattedDate VARCHAR(20),
    ts_date BIGINT,
    ts_lastModified BIGINT,
    ts_reversed BOOLEAN,
    ts_workorder VARCHAR(50),
    ts_jobNumber INT,
    ts_treatment VARCHAR(100),
    ts_assignedBy VARCHAR(100),
    ts_completedBy VARCHAR(100),
    ts_winery VARCHAR(100),
    ts_subOperationTypeId INT,
    ts_from_vessel_id VARCHAR(36),
    ts_to_vessel_id VARCHAR(36),
    ts_loss_details_id VARCHAR(36),
    ts_analysis_ops_id VARCHAR(36)
);

-- From Vessel table
CREATE TABLE transactions_from_vessel (
    ts_from_vessel_id VARCHAR(36) PRIMARY KEY,
    ts_id VARCHAR(36) REFERENCES transactions(ts_id),
    ts_name VARCHAR(50),
    ts_vessel_id INT,
    ts_volOut FLOAT,
    ts_volOutUnit VARCHAR(10),
    ts_before_details_id VARCHAR(36),
    ts_after_details_id VARCHAR(36)
);

CREATE TABLE transactions_from_vessel_before_details (
    ts_before_details_id VARCHAR(36) PRIMARY KEY,
    ts_from_vessel_id VARCHAR(36) REFERENCES transactions_from_vessel(ts_from_vessel_id),
    ts_contentsId INT,
    ts_batch VARCHAR(50),
    ts_batchId INT,
    ts_volume FLOAT,
    ts_volumeUnit VARCHAR(10),
    ts_dip VARCHAR(20),
    ts_state VARCHAR(50),
    ts_rawTaxClass VARCHAR(30),
    ts_federalTaxClass VARCHAR(30),
    ts_stateTaxClass VARCHAR(30),
    ts_program VARCHAR(30),
    ts_grading VARCHAR(30),
    ts_productCategory VARCHAR(30),
    ts_batchOwner VARCHAR(100),
    ts_serviceOrder VARCHAR(50),
    ts_alcoholicFermentState VARCHAR(30),
    ts_malolacticFermentState VARCHAR(30),
    ts_revisionName VARCHAR(50),
    ts_physicalStateText VARCHAR(50),
    ts_batchDetails_id VARCHAR(36)
);

CREATE TABLE transactions_from_vessel_after_details (
    ts_after_details_id VARCHAR(36) PRIMARY KEY,
    ts_from_vessel_id VARCHAR(36) REFERENCES transactions_from_vessel(ts_from_vessel_id),
    ts_contentsId INT,
    ts_batch VARCHAR(50),
    ts_batchId INT,
    ts_volume FLOAT,
    ts_volumeUnit VARCHAR(10),
    ts_dip VARCHAR(20),
    ts_state VARCHAR(50),
    ts_rawTaxClass VARCHAR(30),
    ts_federalTaxClass VARCHAR(30),
    ts_stateTaxClass VARCHAR(30),
    ts_program VARCHAR(30),
    ts_grading VARCHAR(30),
    ts_productCategory VARCHAR(30),
    ts_batchOwner VARCHAR(100),
    ts_serviceOrder VARCHAR(50),
    ts_alcoholicFermentState VARCHAR(30),
    ts_malolacticFermentState VARCHAR(30),
    ts_revisionName VARCHAR(50),
    ts_physicalStateText VARCHAR(50),
    ts_batchDetails_id VARCHAR(36)
);

-- To Vessel table
CREATE TABLE transactions_to_vessel (
    ts_to_vessel_id VARCHAR(36) PRIMARY KEY,
    ts_id VARCHAR(36) REFERENCES transactions(ts_id),
    ts_name VARCHAR(50),
    ts_vessel_id INT,
    ts_volIn FLOAT,
    ts_volInUnit VARCHAR(10),
    ts_before_details_id VARCHAR(36),
    ts_after_details_id VARCHAR(36)
);

CREATE TABLE transactions_to_vessel_before_details (
    ts_before_details_id VARCHAR(36) PRIMARY KEY,
    ts_to_vessel_id VARCHAR(36) REFERENCES transactions_to_vessel(ts_to_vessel_id),
    ts_contentsId INT,
    ts_batch VARCHAR(50),
    ts_batchId INT,
    ts_volume FLOAT,
    ts_volumeUnit VARCHAR(10),
    ts_dip VARCHAR(20),
    ts_state VARCHAR(50),
    ts_rawTaxClass VARCHAR(30),
    ts_federalTaxClass VARCHAR(30),
    ts_stateTaxClass VARCHAR(30),
    ts_program VARCHAR(30),
    ts_grading VARCHAR(30),
    ts_productCategory VARCHAR(30),
    ts_batchOwner VARCHAR(100),
    ts_serviceOrder VARCHAR(50),
    ts_alcoholicFermentState VARCHAR(30),
    ts_malolacticFermentState VARCHAR(30),
    ts_revisionName VARCHAR(50),
    ts_physicalStateText VARCHAR(50),
    ts_batchDetails_id VARCHAR(36)
);

CREATE TABLE transactions_to_vessel_after_details (
    ts_after_details_id VARCHAR(36) PRIMARY KEY,
    ts_to_vessel_id VARCHAR(36) REFERENCES transactions_to_vessel(ts_to_vessel_id),
    ts_contentsId INT,
    ts_batch VARCHAR(50),
    ts_batchId INT,
    ts_volume FLOAT,
    ts_volumeUnit VARCHAR(10),
    ts_dip VARCHAR(20),
    ts_state VARCHAR(50),
    ts_rawTaxClass VARCHAR(30),
    ts_federalTaxClass VARCHAR(30),
    ts_stateTaxClass VARCHAR(30),
    ts_program VARCHAR(30),
    ts_grading VARCHAR(30),
    ts_productCategory VARCHAR(30),
    ts_batchOwner VARCHAR(100),
    ts_serviceOrder VARCHAR(50),
    ts_alcoholicFermentState VARCHAR(30),
    ts_malolacticFermentState VARCHAR(30),
    ts_revisionName VARCHAR(50),
    ts_physicalStateText VARCHAR(50),
    ts_batchDetails_id VARCHAR(36)
);

-- Batch Details (used by before/after details)
CREATE TABLE transactions_batch_details (
    ts_batchDetails_id VARCHAR(36) PRIMARY KEY,
    ts_name VARCHAR(50),
    ts_description VARCHAR(255),
    ts_vintage_id INT,
    ts_vintage_name VARCHAR(20),
    ts_variety_id INT,
    ts_variety_name VARCHAR(50),
    ts_region_id INT,
    ts_region_name VARCHAR(50)
);

-- Loss Details table
CREATE TABLE transactions_loss_details (
    ts_loss_details_id VARCHAR(36) PRIMARY KEY,
    ts_id VARCHAR(36) REFERENCES transactions(ts_id),
    ts_volume FLOAT,
    ts_volumeUnit VARCHAR(10),
    ts_reason VARCHAR(100)
);

-- Analysis Ops table
CREATE TABLE transactions_analysis_ops (
    ts_analysis_ops_id VARCHAR(36) PRIMARY KEY,
    ts_id VARCHAR(36) REFERENCES transactions(ts_id),
    ts_vesselId INT,
    ts_vesselName VARCHAR(50),
    ts_batchId INT,
    ts_batchName VARCHAR(50),
    ts_templateId INT,
    ts_templateName VARCHAR(100)
);

-- Metrics table (inside analysis ops)
CREATE TABLE transactions_metrics (
    ts_metrics_id VARCHAR(36) PRIMARY KEY,
    ts_analysis_ops_id VARCHAR(36) REFERENCES transactions_analysis_ops(ts_analysis_ops_id),
    ts_id VARCHAR(36) REFERENCES transactions(ts_id),
    ts_metric_id INT,
    ts_metric_name VARCHAR(50),
    ts_metric_value FLOAT,
    ts_metric_txtValue VARCHAR(20),
    ts_metric_unit VARCHAR(20)
);