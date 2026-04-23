# Bootstrap: remote state + GitHub OIDC

Run **once per AWS account** (from your laptop) before `infra/envs/dev` or CI.

## Prerequisites

- AWS CLI configured (`aws sts get-caller-identity`)
- Terraform >= 1.5
- An **existing** IAM OIDC identity provider for GitHub Actions at `https://token.actions.githubusercontent.com` in this account (this bootstrap **does not** create it). If it is missing, add it once (for example with the [AWS CLI `aws iam create-open-id-connect-provider`](https://docs.aws.amazon.com/cli/latest/reference/iam/create-open-id-connect-provider.html) flow using GitHub’s thumbprints), then run bootstrap.

### Migrating from an older bootstrap that created the OIDC provider

If state still tracks `aws_iam_openid_connect_provider` or `data.tls_certificate`, remove them from state so Terraform does not try to delete the live provider or pull the unused `tls` provider:

```bash
terraform state rm 'aws_iam_openid_connect_provider.github_actions' 2>/dev/null || true
terraform state rm 'data.tls_certificate.github_actions' 2>/dev/null || true
```

Then `terraform apply` again. If your deploy role’s trust policy was saved with a wrong principal string, `terraform apply` will refresh it from the data source.

## Configure

Copy the example and set your GitHub org/repo:

```bash
cp terraform.tfvars.example terraform.tfvars
```

Optional: set `github_environment = "dev"` to also allow `repo:ORG/REPO:environment:dev` in the trust policy (in addition to pushes to `main`).

## Apply

```bash
cd infra/bootstrap
terraform init
terraform apply
```

## Wire GitHub

1. Copy output `github_actions_deploy_role_arn` into a repository **variable** named `AWS_DEPLOY_ROLE_ARN`.
2. Add repository **variable** `AWS_REGION` (same region you used here, e.g. `us-east-1`).
3. Configure `infra/envs/dev/backend.hcl` (see `backend.hcl.example`) with `bucket` and `dynamodb_table` from outputs, then:

   ```bash
   cd ../envs/dev
   terraform init -backend-config=backend.hcl
   ```

## Security note

The deploy role attaches `PowerUserAccess` and `IAMFullAccess` so Terraform and ECS task IAM can be managed without hand-maintaining hundreds of ARNs. Tighten the inline/custom policies before production multi-tenant use.
