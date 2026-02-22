import argparse
import logging
import os
import pathlib
import sys
from typing import List

from google.cloud import bigquery
from google.cloud.bigquery import QueryJobConfig, ScalarQueryParameter


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="DIM_CASE per-tenant BigQuery MERGE runner")
    parser.add_argument("--env", default=os.getenv("PIPELINE_ENV", "dev"), choices=["dev", "prod"])
    parser.add_argument("--project-id", default=os.getenv("PROJECT_ID", "<PROJECT_ID>"))
    parser.add_argument("--dataset-ops", default=os.getenv("DATASET_OPS", "<DATASET_OPS>"))
    parser.add_argument("--dataset-analytics", default=os.getenv("DATASET_ANALYTICS", "<DATASET_ANALYTICS>"))
    parser.add_argument("--location", default=os.getenv("BQ_REGION", "us-east4"))
    parser.add_argument(
        "--merge-script-path",
        default="/app/sql/merges/merge_dim_case.sql",
        help="Path to merge_dim_case.sql",
    )
    return parser.parse_args()


def fetch_active_tenants(
    client: bigquery.Client,
    project_id: str,
    dataset_ops: str,
    env: str,
) -> List[str]:
    sql = f"""
        SELECT tenant_id
        FROM `{project_id}.{dataset_ops}.stream_config`
        WHERE env = @env
          AND is_active = TRUE
        ORDER BY tenant_id
    """
    job = client.query(
        sql,
        job_config=QueryJobConfig(
            query_parameters=[ScalarQueryParameter("env", "STRING", env)]
        ),
    )
    return [row["tenant_id"] for row in job.result()]


def run_merge_for_tenant(
    client: bigquery.Client,
    merge_sql: str,
    project_id: str,
    dataset_ops: str,
    dataset_analytics: str,
    env: str,
    tenant_id: str,
) -> None:
    params = [
        ScalarQueryParameter("tenant_id", "STRING", tenant_id),
        ScalarQueryParameter("env", "STRING", env),
        ScalarQueryParameter("project_id", "STRING", project_id),
        ScalarQueryParameter("dataset_ops", "STRING", dataset_ops),
        ScalarQueryParameter("dataset_analytics", "STRING", dataset_analytics),
    ]
    job = client.query(merge_sql, job_config=QueryJobConfig(query_parameters=params))
    job.result()


def main() -> int:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )
    args = parse_args()

    merge_script_path = pathlib.Path(args.merge_script_path)
    if not merge_script_path.exists():
        logging.error("merge script not found: %s", merge_script_path)
        logging.error("ensure merge script is included in container image at build time")
        return 2

    merge_sql = merge_script_path.read_text(encoding="utf-8")

    client = bigquery.Client(project=args.project_id, location=args.location)
    tenants = fetch_active_tenants(
        client=client,
        project_id=args.project_id,
        dataset_ops=args.dataset_ops,
        env=args.env,
    )

    if not tenants:
        logging.warning("no active tenants for env=%s", args.env)
        return 0

    failed = []
    for tenant_id in tenants:
        try:
            logging.info("starting tenant=%s env=%s", tenant_id, args.env)
            run_merge_for_tenant(
                client=client,
                merge_sql=merge_sql,
                project_id=args.project_id,
                dataset_ops=args.dataset_ops,
                dataset_analytics=args.dataset_analytics,
                env=args.env,
                tenant_id=tenant_id,
            )
            logging.info("success tenant=%s env=%s", tenant_id, args.env)
        except Exception as exc:  # noqa: BLE001
            logging.exception("failed tenant=%s env=%s err=%s", tenant_id, args.env, exc)
            failed.append(tenant_id)

    if failed:
        logging.error("completed with failures: %s", ",".join(failed))
        return 1

    logging.info("all tenants processed successfully: %d", len(tenants))
    return 0


if __name__ == "__main__":
    sys.exit(main())
