CREATE TABLE IF NOT EXISTS `<PROJECT_ID>.<DATASET_OPS>.stream_config` (
  env STRING NOT NULL,
  tenant_id STRING NOT NULL,
  is_active BOOL NOT NULL,
  gcs_bucket STRING NOT NULL,
  cases_prefix STRING NOT NULL,
  notes STRING
);

-- Seed dev with one tenant. Replace TENANT_DEV_001 with real tenant id.
INSERT INTO `<PROJECT_ID>.<DATASET_OPS>.stream_config` (
  env,
  tenant_id,
  is_active,
  gcs_bucket,
  cases_prefix,
  notes
)
VALUES (
  'dev',
  'TENANT_DEV_001',
  TRUE,
  'bkt-tla-operations-billing-svc-dev-use4',
  'cases/',
  'TODO: replace with real tenant'
);
