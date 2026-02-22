terraform {
  required_version = ">= 1.5.0"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = ">= 5.30.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

locals {
  analytics_dataset_id = var.dataset_analytics
  ops_dataset_id       = var.dataset_ops
  job_name             = "dim-case-updater"
}

resource "google_service_account" "dim_case_runner" {
  account_id   = "dim-case-runner"
  display_name = "DIM_CASE pipeline runner"
}

resource "google_bigquery_dataset" "ops" {
  dataset_id  = local.ops_dataset_id
  description = "Ops/config metadata for CDC pipelines"
  location    = var.region
}

resource "google_bigquery_dataset" "analytics" {
  dataset_id  = local.analytics_dataset_id
  description = "Analytics models for consolidated warehouse dims"
  location    = var.region
}

resource "google_bigquery_connection" "biglake" {
  connection_id = var.connection_id
  location      = var.region

  cloud_resource {}
}

resource "google_storage_bucket_iam_member" "conn_dev_viewer" {
  bucket = var.dev_bucket
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_bigquery_connection.biglake.cloud_resource[0].service_account_id}"
}

resource "google_storage_bucket_iam_member" "conn_prod_viewer" {
  bucket = var.prod_bucket
  role   = "roles/storage.objectViewer"
  member = "serviceAccount:${google_bigquery_connection.biglake.cloud_resource[0].service_account_id}"
}

resource "google_project_iam_member" "runner_bq_job_user" {
  project = var.project_id
  role    = "roles/bigquery.jobUser"
  member  = "serviceAccount:${google_service_account.dim_case_runner.email}"
}

resource "google_project_iam_member" "runner_conn_user" {
  project = var.project_id
  role    = "roles/bigquery.connectionUser"
  member  = "serviceAccount:${google_service_account.dim_case_runner.email}"
}

resource "google_bigquery_dataset_iam_member" "runner_analytics_editor" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dim_case_runner.email}"
}

resource "google_bigquery_dataset_iam_member" "runner_ops_editor" {
  dataset_id = google_bigquery_dataset.ops.dataset_id
  role       = "roles/bigquery.dataEditor"
  member     = "serviceAccount:${google_service_account.dim_case_runner.email}"
}

resource "google_bigquery_table" "stream_config" {
  dataset_id = google_bigquery_dataset.ops.dataset_id
  table_id   = "stream_config"

  schema = jsonencode([
    { name = "env", type = "STRING", mode = "REQUIRED" },
    { name = "tenant_id", type = "STRING", mode = "REQUIRED" },
    { name = "is_active", type = "BOOL", mode = "REQUIRED" },
    { name = "gcs_bucket", type = "STRING", mode = "REQUIRED" },
    { name = "cases_prefix", type = "STRING", mode = "REQUIRED" },
    { name = "notes", type = "STRING", mode = "NULLABLE" }
  ])
}

resource "google_bigquery_table" "pipeline_state" {
  dataset_id = google_bigquery_dataset.ops.dataset_id
  table_id   = "pipeline_state"

  schema = jsonencode([
    { name = "pipeline_name", type = "STRING", mode = "REQUIRED" },
    { name = "env", type = "STRING", mode = "REQUIRED" },
    { name = "tenant_id", type = "STRING", mode = "REQUIRED" },
    { name = "last_success_dt", type = "DATE", mode = "NULLABLE" },
    { name = "last_success_ts", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "updated_at", type = "TIMESTAMP", mode = "REQUIRED" }
  ])
}

resource "google_bigquery_table" "dim_case" {
  dataset_id          = google_bigquery_dataset.analytics.dataset_id
  table_id            = "dim_case"
  deletion_protection = false

  schema = jsonencode([
    { name = "case_key", type = "INT64", mode = "REQUIRED" },
    { name = "tenant_id", type = "STRING", mode = "REQUIRED" },
    { name = "case_id", type = "STRING", mode = "REQUIRED" },
    { name = "case_name", type = "STRING", mode = "NULLABLE" },
    { name = "org_name", type = "STRING", mode = "NULLABLE" },
    { name = "clockify_case_name", type = "STRING", mode = "NULLABLE" },
    { name = "invoice_memo", type = "STRING", mode = "NULLABLE" },
    { name = "created_at", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "updated_at", type = "TIMESTAMP", mode = "REQUIRED" },
    { name = "case_created_at", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "case_retired_at", type = "TIMESTAMP", mode = "NULLABLE" },
    { name = "is_active", type = "BOOL", mode = "REQUIRED" },
    { name = "is_billable", type = "BOOL", mode = "NULLABLE" }
  ])
}

# BigLake external table for dev CDC Avro stream.
resource "google_bigquery_table" "ext_cases_avro_dev" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "ext_cases_avro_dev"

  external_data_configuration {
    autodetect    = true
    source_format = "AVRO"
    source_uris   = ["gs://${var.dev_bucket}/cases/*"]

    # TODO: Confirm provider field support for Hive partitioning options in your exact provider version.
    # If unavailable in Terraform, create this table with SQL from sql/external_tables/ext_cases_avro_dev.sql.
    connection_id = google_bigquery_connection.biglake.name
  }
}

resource "google_bigquery_table" "ext_cases_avro_prod" {
  dataset_id = google_bigquery_dataset.analytics.dataset_id
  table_id   = "ext_cases_avro_prod"

  external_data_configuration {
    autodetect    = true
    source_format = "AVRO"
    source_uris   = ["gs://${var.prod_bucket}/cases/*"]
    connection_id = google_bigquery_connection.biglake.name
  }
}

resource "google_cloud_run_v2_job" "dim_case_updater" {
  name     = local.job_name
  location = var.region

  template {
    template {
      service_account = google_service_account.dim_case_runner.email
      timeout         = "3600s"

      containers {
        image = var.pipeline_image
        env {
          name  = "PROJECT_ID"
          value = var.project_id
        }
        env {
          name  = "DATASET_OPS"
          value = var.dataset_ops
        }
        env {
          name  = "DATASET_ANALYTICS"
          value = var.dataset_analytics
        }
        env {
          name  = "BQ_REGION"
          value = var.region
        }
      }
    }
  }
}

resource "google_cloud_scheduler_job" "dim_case_daily_dev" {
  name      = "dim-case-daily-dev"
  region    = var.region
  schedule  = "0 2 * * *"
  time_zone = var.scheduler_timezone

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.dim_case_updater.name}:run"

    oauth_token {
      service_account_email = google_service_account.dim_case_runner.email
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }

    body = base64encode(jsonencode({
      overrides = {
        containerOverrides = [{
          env = [{ name = "PIPELINE_ENV", value = "dev" }]
        }]
      }
    }))
  }
}

resource "google_cloud_scheduler_job" "dim_case_daily_prod" {
  name      = "dim-case-daily-prod"
  region    = var.region
  schedule  = "0 3 * * *"
  time_zone = var.scheduler_timezone

  http_target {
    http_method = "POST"
    uri         = "https://${var.region}-run.googleapis.com/apis/run.googleapis.com/v1/namespaces/${var.project_id}/jobs/${google_cloud_run_v2_job.dim_case_updater.name}:run"

    oauth_token {
      service_account_email = google_service_account.dim_case_runner.email
      scope                 = "https://www.googleapis.com/auth/cloud-platform"
    }

    body = base64encode(jsonencode({
      overrides = {
        containerOverrides = [{
          env = [{ name = "PIPELINE_ENV", value = "prod" }]
        }]
      }
    }))
  }
}
