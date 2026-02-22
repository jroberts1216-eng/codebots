-- Parameters expected by job runner:
-- @tenant_id STRING
-- @env STRING ('dev' or 'prod')
-- @project_id STRING
-- @dataset_analytics STRING
-- @dataset_ops STRING

DECLARE src_view STRING;
DECLARE source_sql STRING;
DECLARE merge_sql STRING;
DECLARE state_sql STRING;

SET src_view = IF(
  @env = 'prod',
  FORMAT('`%s.%s.vw_cases_current_prod`', @project_id, @dataset_analytics),
  FORMAT('`%s.%s.vw_cases_current_dev`', @project_id, @dataset_analytics)
);

SET source_sql = FORMAT("""
  SELECT
    ABS(FARM_FINGERPRINT(CONCAT(tenant_id, '|', case_id))) AS case_key,
    tenant_id,
    case_id,
    case_name,
    org_name,
    clockify_case_name,
    invoice_memo,
    source_created_at,
    source_updated_at,
    cdc_commit_ts,
    cdc_seq,
    op
  FROM %s
  WHERE tenant_id = @tenant_id
""", src_view);

SET merge_sql = FORMAT("""
MERGE `%s.%s.dim_case` AS T
USING (
  %s
) AS S
ON T.tenant_id = S.tenant_id
AND T.case_id = S.case_id
WHEN MATCHED AND (S.op IS NOT NULL AND LOWER(S.op) = 'd') THEN
  UPDATE SET
    T.is_active = FALSE,
    T.case_retired_at = CURRENT_TIMESTAMP(),
    T.updated_at = CURRENT_TIMESTAMP()
WHEN MATCHED AND (
  IFNULL(T.case_name, '') != IFNULL(S.case_name, '') OR
  IFNULL(T.org_name, '') != IFNULL(S.org_name, '') OR
  IFNULL(T.clockify_case_name, '') != IFNULL(S.clockify_case_name, '') OR
  IFNULL(T.invoice_memo, '') != IFNULL(S.invoice_memo, '') OR
  IFNULL(T.case_created_at, TIMESTAMP('1970-01-01')) != IFNULL(S.source_created_at, TIMESTAMP('1970-01-01')) OR
  IFNULL(T.is_active, TRUE) != TRUE
) THEN
  UPDATE SET
    T.case_key = S.case_key,
    T.case_name = S.case_name,
    T.org_name = S.org_name,
    T.clockify_case_name = S.clockify_case_name,
    T.invoice_memo = S.invoice_memo,
    T.case_created_at = S.source_created_at,
    T.updated_at = CURRENT_TIMESTAMP(),
    T.is_active = TRUE,
    T.case_retired_at = NULL
WHEN NOT MATCHED AND (S.op IS NULL OR LOWER(S.op) != 'd') THEN
  INSERT (
    case_key,
    tenant_id,
    case_id,
    case_name,
    org_name,
    clockify_case_name,
    invoice_memo,
    created_at,
    updated_at,
    case_created_at,
    case_retired_at,
    is_active,
    is_billable
  )
  VALUES (
    S.case_key,
    S.tenant_id,
    S.case_id,
    S.case_name,
    S.org_name,
    S.clockify_case_name,
    S.invoice_memo,
    CURRENT_TIMESTAMP(),
    CURRENT_TIMESTAMP(),
    S.source_created_at,
    NULL,
    TRUE,
    TRUE
  )
""", @project_id, @dataset_analytics, source_sql);

EXECUTE IMMEDIATE merge_sql USING @tenant_id AS tenant_id;

SET state_sql = FORMAT("""
MERGE `%s.%s.pipeline_state` AS PS
USING (
  SELECT
    'dim_case_merge' AS pipeline_name,
    @env AS env,
    @tenant_id AS tenant_id,
    CURRENT_DATE() AS last_success_dt,
    CURRENT_TIMESTAMP() AS last_success_ts,
    CURRENT_TIMESTAMP() AS updated_at
) AS S
ON PS.pipeline_name = S.pipeline_name
AND PS.env = S.env
AND PS.tenant_id = S.tenant_id
WHEN MATCHED THEN
  UPDATE SET
    PS.last_success_dt = S.last_success_dt,
    PS.last_success_ts = S.last_success_ts,
    PS.updated_at = S.updated_at
WHEN NOT MATCHED THEN
  INSERT (pipeline_name, env, tenant_id, last_success_dt, last_success_ts, updated_at)
  VALUES (S.pipeline_name, S.env, S.tenant_id, S.last_success_dt, S.last_success_ts, S.updated_at)
""", @project_id, @dataset_ops);

EXECUTE IMMEDIATE state_sql USING @env AS env, @tenant_id AS tenant_id;
