CREATE TABLE ts_ad_dispatches (
    ts_dispatchNo      VARCHAR(20) PRIMARY KEY,
    ts_subOperationId  BIGINT NOT NULL,
    ts_formattedDate   DATE NOT NULL,
    ts_workorder       VARCHAR(20),
    ts_jobNumber       INTEGER,
    ts_treatment       VARCHAR(100),
    ts_completedBy     VARCHAR(100),
    ts_winery          VARCHAR(100)
);