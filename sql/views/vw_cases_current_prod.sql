CREATE OR REPLACE VIEW `<PROJECT_ID>.<DATASET_ANALYTICS>.vw_cases_current_prod` AS
SELECT * EXCEPT(rn)
FROM (
  SELECT
    CAST(tenant_id AS STRING) AS tenant_id,
    CAST(case_id AS STRING) AS case_id,
    CAST(case_name AS STRING) AS case_name,
    CAST(org_name AS STRING) AS org_name,
    CAST(clockify_case_name AS STRING) AS clockify_case_name,
    CAST(invoice_memo AS STRING) AS invoice_memo,
    CAST(created_at AS TIMESTAMP) AS source_created_at,
    CAST(updated_at AS TIMESTAMP) AS source_updated_at,
    CAST(cdc_commit_ts AS TIMESTAMP) AS cdc_commit_ts,
    CAST(cdc_seq AS INT64) AS cdc_seq,
    CAST(op AS STRING) AS op,
    CURRENT_TIMESTAMP() AS loaded_at_utc,
    ROW_NUMBER() OVER (
      PARTITION BY tenant_id, case_id
      ORDER BY cdc_commit_ts DESC, cdc_seq DESC
    ) AS rn
  FROM `<PROJECT_ID>.<DATASET_ANALYTICS>.ext_cases_avro_prod`
  WHERE dt >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 7 DAY))
)
WHERE rn = 1
  AND (op IS NULL OR LOWER(op) != 'd');
