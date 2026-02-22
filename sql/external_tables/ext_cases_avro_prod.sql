CREATE OR REPLACE EXTERNAL TABLE `<PROJECT_ID>.<DATASET_ANALYTICS>.ext_cases_avro_prod`
WITH CONNECTION `<REGION>.<CONNECTION_ID>`
OPTIONS (
  format = 'AVRO',
  uris = ['gs://bkt-tla-operations-billing-svc-prod-use4/cases/*'],
  hive_partition_uri_prefix = 'gs://bkt-tla-operations-billing-svc-prod-use4/cases/',
  require_hive_partition_filter = TRUE
);

-- TODO: Replace prod bucket if naming differs in target environment.
