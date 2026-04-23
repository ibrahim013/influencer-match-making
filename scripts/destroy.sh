#!/usr/bin/env bash
# Local destroy mirror of .github/workflows/destroy.yml

set -euo pipefail

if [[ "${1:-}" != "DESTROY" ]]; then
  echo "Usage: $0 DESTROY"
  echo "You must pass the literal DESTROY to confirm teardown."
  exit 1
fi

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
  echo "Missing ${BACKEND_HCL}."
  exit 1
fi

terraform -chdir="${TF_DIR}" init -backend-config="${BACKEND_HCL}" -input=false

if BUCKET="$(terraform -chdir="${TF_DIR}" output -raw spa_bucket_id 2>/dev/null)"; then
  aws s3 rm "s3://${BUCKET}/" --recursive || true
fi

terraform -chdir="${TF_DIR}" destroy -input=false -auto-approve
