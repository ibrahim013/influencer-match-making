output "endpoint" {
  value = aws_db_instance.main.address
}

output "port" {
  value = aws_db_instance.main.port
}

output "db_username" {
  value = var.db_username
}

output "db_name" {
  value = var.db_name
}

output "database_url" {
  description = "Postgres URL for LangGraph checkpointer (sensitive)."
  value       = "postgresql://${var.db_username}:${random_password.master.result}@${aws_db_instance.main.address}:${aws_db_instance.main.port}/${var.db_name}"
  sensitive   = true
}

output "master_password" {
  value     = random_password.master.result
  sensitive = true
}
