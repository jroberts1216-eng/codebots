variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "Region for BigQuery connection and Cloud Run"
  type        = string
  default     = "us-east4"
}

variable "dataset_ops" {
  description = "BigQuery ops dataset (config/state tables)"
  type        = string
  default     = "ops"
}

variable "dataset_analytics" {
  description = "BigQuery analytics dataset (external tables/views/dim tables)"
  type        = string
  default     = "analytics"
}

variable "connection_id" {
  description = "BigLake connection ID"
  type        = string
  default     = "biglake_conn"
}

variable "dev_bucket" {
  description = "Dev CDC bucket"
  type        = string
  default     = "bkt-tla-operations-billing-svc-dev-use4"
}

variable "prod_bucket" {
  description = "Prod CDC bucket"
  type        = string
  default     = "bkt-tla-operations-billing-svc-prod-use4"
}

variable "pipeline_image" {
  description = "Container image for dim_case_updater Cloud Run Job"
  type        = string
  default     = "us-docker.pkg.dev/PROJECT/REPO/dim-case-updater:latest"
}

variable "scheduler_timezone" {
  description = "Timezone for scheduler jobs"
  type        = string
  default     = "Etc/UTC"
}
