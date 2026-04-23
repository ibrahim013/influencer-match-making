output "terraform_state_bucket" {
  value       = aws_s3_bucket.tfstate.bucket
  description = "S3 bucket for infra/envs/dev remote backend."
}

output "terraform_lock_table" {
  value       = aws_dynamodb_table.tflock.name
  description = "DynamoDB table for Terraform state locking."
}

output "github_actions_deploy_role_arn" {
  value       = aws_iam_role.gha_deploy.arn
  description = "Set as GitHub repository variable AWS_DEPLOY_ROLE_ARN."
}

output "oidc_provider_arn" {
  value       = data.aws_iam_openid_connect_provider.github_actions.arn
  description = "GitHub Actions OIDC provider ARN."
}
