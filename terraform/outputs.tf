output "biglake_connection_name" {
  value = google_bigquery_connection.biglake.name
}

output "runner_service_account" {
  value = google_service_account.dim_case_runner.email
}

output "cloud_run_job_name" {
  value = google_cloud_run_v2_job.dim_case_updater.name
}
