CREATE OR REPLACE EXTERNAL TABLE `<PROJECT_ID>.<DATASET_ANALYTICS>.ext_cases_avro_dev`
WITH CONNECTION `<REGION>.<CONNECTION_ID>`
OPTIONS (
  format = 'AVRO',
  uris = ['gs://bkt-tla-operations-billing-svc-dev-use4/cases/*'],
  hive_partition_uri_prefix = 'gs://bkt-tla-operations-billing-svc-dev-use4/cases/',
  require_hive_partition_filter = TRUE
);

-- Expected hive path example:
-- gs://.../cases/tenant_id=<TENANT>/dt=<YYYYMMDD>/<uuid>.avro
-- TODO: If current layout differs, adjust uris and partition strategy.
