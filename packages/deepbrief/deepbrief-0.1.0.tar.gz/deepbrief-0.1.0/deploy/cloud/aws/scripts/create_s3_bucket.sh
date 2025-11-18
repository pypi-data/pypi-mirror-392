#!/usr/bin/env bash

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: create_s3_bucket.sh [bucket-name] [--prefix <prefix>]

Options:
  bucket-name         Optional explicit bucket name (must be globally unique).
  --prefix <prefix>   Generate a unique bucket name by appending a random suffix (6 chars) to <prefix>.

If neither bucket-name nor --prefix is provided, the script defaults to deepbrief-$USER-<timestamp>.
EOF
}

if ! command -v aws >/dev/null 2>&1; then
  echo "aws CLI not found. Install AWS CLI v2 before running this script." >&2
  exit 1
fi

PREFIX_MODE=false
PREFIX_VALUE=""
POSITIONAL_NAME=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --prefix)
      PREFIX_MODE=true
      PREFIX_VALUE="${2:-}"
      if [[ -z "$PREFIX_VALUE" ]]; then
        echo "--prefix requires a value" >&2
        usage
        exit 1
      fi
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    -*)
      echo "Unknown option: $1" >&2
      usage
      exit 1
      ;;
    *)
      POSITIONAL_NAME="$1"
      shift
      ;;
  esac
done

REGION="${AWS_REGION:-us-east-1}"
CREATE_ARGS=()
if [[ "$REGION" != "us-east-1" ]]; then
  CREATE_ARGS=(--region "$REGION" --create-bucket-configuration LocationConstraint="$REGION")
fi

if [[ "$PREFIX_MODE" == true ]]; then
  RAND_SUFFIX=""
  for _ in {1..6}; do
    RAND_SUFFIX+=$(printf "%x" $((RANDOM % 16)) | tr '[:upper:]' '[:lower:]')
  done
  BUCKET_NAME="${PREFIX_VALUE}-${RAND_SUFFIX}"
elif [[ -n "$POSITIONAL_NAME" ]]; then
  BUCKET_NAME="$POSITIONAL_NAME"
else
  BUCKET_NAME="deepbrief-$USER-$(date +%Y%m%d%H%M%S)"
fi

OWNED_BUCKETS=$(aws s3api list-buckets --query "Buckets[].Name" --output text | tr '\t' '\n' || true)
if grep -Fxq "$BUCKET_NAME" <<<"$OWNED_BUCKETS"; then
  echo "Bucket '$BUCKET_NAME' already exists in your account. Nothing to do."
  exit 0
fi

echo "Checking if bucket '$BUCKET_NAME' already exists..."
if aws s3api head-bucket --bucket "$BUCKET_NAME" >/dev/null 2>&1; then
  echo "Bucket name '$BUCKET_NAME' is already taken globally. Choose a different name." >&2
  exit 1
fi

echo "Creating bucket '$BUCKET_NAME' in region '$REGION'..."
if [[ ${#CREATE_ARGS[@]} -gt 0 ]]; then
  if ! aws s3api create-bucket --bucket "$BUCKET_NAME" "${CREATE_ARGS[@]}"; then
    echo "Failed to create bucket '$BUCKET_NAME'. Ensure the name is globally unique and you have s3:CreateBucket permission." >&2
    exit 1
  fi
else
  if ! aws s3api create-bucket --bucket "$BUCKET_NAME"; then
    echo "Failed to create bucket '$BUCKET_NAME'. Ensure the name is globally unique and you have s3:CreateBucket permission." >&2
    exit 1
  fi
fi

echo "Bucket '$BUCKET_NAME' created successfully."
echo "Remember to update 'deploy/cloud/aws/components/s3.yaml' with this bucket name."
