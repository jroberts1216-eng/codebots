CREATE TABLE IF NOT EXISTS `<PROJECT_ID>.<DATASET_ANALYTICS>.dim_case` (
  case_key INT64 NOT NULL,
  tenant_id STRING NOT NULL,
  case_id STRING NOT NULL,
  case_name STRING,
  org_name STRING,
  clockify_case_name STRING,
  invoice_memo STRING,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  case_created_at TIMESTAMP,
  case_retired_at TIMESTAMP,
  is_active BOOL NOT NULL,
  is_billable BOOL
)
PARTITION BY DATE(updated_at)
CLUSTER BY tenant_id, case_id;

-- NOTE: BigQuery does not enforce unique constraints for this natural key,
-- so uniqueness is maintained by MERGE key logic.
