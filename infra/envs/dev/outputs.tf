output "ecr_repository_url" {
  value = module.ecr.repository_url
}

output "ecr_repository_name" {
  value = module.ecr.repository_name
}

output "ecs_cluster_name" {
  value = module.ecs.cluster_name
}

output "ecs_service_name" {
  value = module.ecs.service_name
}

output "ecs_task_definition_family" {
  value = module.ecs.task_definition_family
}

output "alb_dns_name" {
  value = module.ecs.alb_dns_name
}

output "alb_url" {
  value = "http://${module.ecs.alb_dns_name}"
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
