variable "aws_region" {
  type        = string
  description = "Region for state bucket, DynamoDB lock, and OIDC role."
  default     = "us-east-1"
}

variable "github_org" {
  type        = string
  description = "GitHub organization or user that owns the repository."
}

variable "github_repo" {
  type        = string
  description = "Repository name (without org)."
}

variable "github_environment" {
  type        = string
  description = "Optional GitHub Environment name for additional trust restriction (e.g. dev). Leave empty to allow any ref matching main branch only."
  default     = ""
}

variable "state_bucket_suffix" {
  type        = string
  description = "Suffix after matchmaking-tfstate- (defaults to AWS account id)."
  default     = ""
}

variable "github_oidc_provider_url" {
  type        = string
  description = "URL of the existing IAM OIDC identity provider for GitHub Actions (must already exist in the account)."
  default     = "https://token.actions.githubusercontent.com"
}
