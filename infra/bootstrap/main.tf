data "aws_caller_identity" "current" {}

locals {
  state_bucket_name = var.state_bucket_suffix != "" ? "matchmaking-tfstate-${var.state_bucket_suffix}" : "matchmaking-tfstate-${data.aws_caller_identity.current.account_id}"
  lock_table_name   = "matchmaking-tflock"
  trusted_subs = compact(concat(
    ["repo:${var.github_org}/${var.github_repo}:ref:refs/heads/main"],
    var.github_environment != "" ? ["repo:${var.github_org}/${var.github_repo}:environment:${var.github_environment}"] : []
  ))
}

# Reuse the account-wide GitHub Actions OIDC provider (create it once manually or via another stack if missing).
data "aws_iam_openid_connect_provider" "github_actions" {
  url = var.github_oidc_provider_url
}

resource "aws_s3_bucket" "tfstate" {
  bucket = local.state_bucket_name

  tags = {
    Name        = local.state_bucket_name
    Purpose     = "terraform-state"
    ManagedBy   = "terraform-bootstrap"
    Environment = "shared"
  }
}

resource "aws_s3_bucket_versioning" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  versioning_configuration {
    status = "Enabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "tfstate" {
  bucket = aws_s3_bucket.tfstate.id
  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

resource "aws_s3_bucket_public_access_block" "tfstate" {
  bucket                  = aws_s3_bucket.tfstate.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_dynamodb_table" "tflock" {
  name         = local.lock_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "LockID"

  attribute {
    name = "LockID"
    type = "S"
  }

  tags = {
    Name        = local.lock_table_name
    Purpose     = "terraform-locks"
    ManagedBy   = "terraform-bootstrap"
    Environment = "shared"
  }
}

data "aws_iam_policy_document" "gha_assume" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRoleWithWebIdentity"]

    principals {
      type        = "Federated"
      identifiers = [data.aws_iam_openid_connect_provider.github_actions.arn]
    }

    condition {
      test     = "StringEquals"
      variable = "token.actions.githubusercontent.com:aud"
      values   = ["sts.amazonaws.com"]
    }

    condition {
      test     = "StringLike"
      variable = "token.actions.githubusercontent.com:sub"
      values   = local.trusted_subs
    }
  }
}

resource "aws_iam_role" "gha_deploy" {
  name                 = "gha-matchmaking-deployer"
  assume_role_policy   = data.aws_iam_policy_document.gha_assume.json
  max_session_duration = 3600

  tags = {
    Name = "gha-matchmaking-deployer"
  }
}

resource "aws_iam_role_policy_attachment" "gha_power_user" {
  role       = aws_iam_role.gha_deploy.name
  policy_arn = "arn:aws:iam::aws:policy/PowerUserAccess"
}

resource "aws_iam_role_policy_attachment" "gha_iam_full" {
  role       = aws_iam_role.gha_deploy.name
  policy_arn = "arn:aws:iam::aws:policy/IAMFullAccess"
}

data "aws_iam_policy_document" "gha_state" {
  statement {
    sid    = "TerraformStateBucket"
    effect = "Allow"
    actions = [
      "s3:ListBucket",
      "s3:GetBucketVersioning",
      "s3:GetBucketEncryption",
      "s3:GetBucketPublicAccessBlock",
      "s3:GetBucketLocation",
    ]
    resources = [aws_s3_bucket.tfstate.arn]
  }

  statement {
    sid    = "TerraformStateObjects"
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:DeleteObject",
    ]
    resources = ["${aws_s3_bucket.tfstate.arn}/*"]
  }

  statement {
    sid       = "TerraformLocks"
    effect    = "Allow"
    actions   = ["dynamodb:GetItem", "dynamodb:PutItem", "dynamodb:DeleteItem"]
    resources = [aws_dynamodb_table.tflock.arn]
  }
}

resource "aws_iam_role_policy" "gha_state" {
  name   = "terraform-remote-state"
  role   = aws_iam_role.gha_deploy.id
  policy = data.aws_iam_policy_document.gha_state.json
}
