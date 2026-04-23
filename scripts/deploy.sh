#!/usr/bin/env bash
# Local deploy mirror of .github/workflows/deploy.yml
# Prerequisites: AWS credentials (env or profile), Docker, Terraform >= 1.5, Node 22+.
# Copy infra/envs/dev/backend.hcl.example -> backend.hcl and set bucket / dynamodb_table from bootstrap.
# Optional: create .env.deploy at repo root with TF_VAR_* exports (see README).

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

if [[ -f "${ROOT}/.env.deploy" ]]; then
  # shellcheck source=/dev/null
  set -a && source "${ROOT}/.env.deploy" && set +a
fi

: "${AWS_REGION:?Set AWS_REGION}"
export AWS_DEFAULT_REGION="${AWS_REGION}"

TF_DIR="${ROOT}/infra/envs/dev"
BACKEND_HCL="${TF_DIR}/backend.hcl"

if [[ ! -f "${BACKEND_HCL}" ]]; then
  echo "Missing ${BACKEND_HCL}. Copy backend.hcl.example and fill bucket + dynamodb_table from bootstrap outputs."
  exit 1
fi

terraform -chdir="${TF_DIR}" init -backend-config="${BACKEND_HCL}" -input=false

terraform -chdir="${TF_DIR}" apply -input=false -auto-approve \
  -target=module.network \
  -target=module.ecr \
  -target=module.rds \
  -target=module.frontend

ECR_URL="$(terraform -chdir="${TF_DIR}" output -raw ecr_repository_url)"
IMAGE_TAG="${IMAGE_TAG:-$(git rev-parse HEAD 2>/dev/null || echo latest)}"

aws ecr get-login-password --region "${AWS_REGION}" | docker login --username AWS --password-stdin "${ECR_URL%%/*}"
docker build -f backend/Dockerfile -t "${ECR_URL}:${IMAGE_TAG}" -t "${ECR_URL}:latest" .
docker push "${ECR_URL}:${IMAGE_TAG}"
docker push "${ECR_URL}:latest"

terraform -chdir="${TF_DIR}" apply -input=false -auto-approve \
  -var="image_tag=${IMAGE_TAG}"

ALB_DNS="$(terraform -chdir="${TF_DIR}" output -raw alb_dns_name)"
export VITE_API_BASE_URL="http://${ALB_DNS}"

pushd frontend >/dev/null
npm ci
npm run build
popd >/dev/null

BUCKET="$(terraform -chdir="${TF_DIR}" output -raw spa_bucket_id)"
aws s3 sync frontend/dist "s3://${BUCKET}/" --delete

DIST="$(terraform -chdir="${TF_DIR}" output -raw cloudfront_distribution_id)"
aws cloudfront create-invalidation --distribution-id "${DIST}" --paths "/*"

echo "SPA: $(terraform -chdir="${TF_DIR}" output -raw cloudfront_url)"
echo "API: $(terraform -chdir="${TF_DIR}" output -raw alb_url)"
