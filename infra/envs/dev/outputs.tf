output "ecr_repository_url" {
  value = module.ecr.repository_url
}

output "ecr_repository_name" {
  value = module.ecr.repository_name
}

output "apprunner_service_id" {
  value = module.apprunner.service_id
}

output "apprunner_service_url" {
  value       = module.apprunner.service_url
  description = "HTTPS base URL for the API (set VITE_API_BASE_URL to this)."
}

output "cloudfront_domain_name" {
  value = module.frontend.cloudfront_domain_name
}

output "cloudfront_url" {
  value = "https://${module.frontend.cloudfront_domain_name}"
}

output "cloudfront_distribution_id" {
  value = module.frontend.cloudfront_distribution_id
}

output "spa_bucket_id" {
  value = module.frontend.bucket_id
}

output "rds_endpoint" {
  value = module.rds.endpoint
}

output "rds_master_password" {
  value     = module.rds.master_password
  sensitive = true
}

output "database_url" {
  value     = module.rds.database_url
  sensitive = true
}
