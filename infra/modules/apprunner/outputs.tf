output "service_id" {
  value = aws_apprunner_service.api.id
}

output "service_arn" {
  value = aws_apprunner_service.api.arn
}

# Provider returns the public URL; normalize to string starting with https://
output "service_url" {
  value = startswith(aws_apprunner_service.api.service_url, "https://") ? aws_apprunner_service.api.service_url : "https://${aws_apprunner_service.api.service_url}"
}

output "vpc_connector_arn" {
  value = aws_apprunner_vpc_connector.main.arn
}
