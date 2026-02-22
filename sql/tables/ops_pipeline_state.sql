CREATE TABLE IF NOT EXISTS `<PROJECT_ID>.<DATASET_OPS>.pipeline_state` (
  pipeline_name STRING NOT NULL,
  env STRING NOT NULL,
  tenant_id STRING NOT NULL,
  last_success_dt DATE,
  last_success_ts TIMESTAMP,
  updated_at TIMESTAMP NOT NULL
);
