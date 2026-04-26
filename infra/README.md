# AWS infrastructure (Terraform)

- **`bootstrap/`** — S3 remote state bucket, DynamoDB lock table, GitHub OIDC deploy role (run once per account). See [bootstrap/README.md](bootstrap/README.md).
- **`modules/`** — Reusable VPC, ECR, RDS, App Runner, S3 + CloudFront.
- **`envs/dev/`** — Composed dev stack; uses S3 backend (configure `backend.hcl` from `backend.hcl.example`).

Deploy from CI: [.github/workflows/deploy.yml](../.github/workflows/deploy.yml).  
Local: [`scripts/deploy.sh`](../scripts/deploy.sh) from the repository root.
