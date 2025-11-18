#!/usr/bin/env bash
set -euo pipefail

# -------- Defaults (override via env) --------
CLUSTER_NAME="${CLUSTER_NAME:-aisv-dev}"
AWS_REGION="${AWS_REGION:-us-east-1}"
NODE_TYPE="${NODE_TYPE:-t3.xlarge}"
NODE_COUNT="${NODE_COUNT:-2}"
NODE_MIN="${NODE_MIN:-1}"
NODE_MAX="${NODE_MAX:-5}"
K8S_VERSION="${K8S_VERSION:-1.32}"

# SSH behavior
ENABLE_SSH="${ENABLE_SSH:-1}"
EC2_KEYPAIR_NAME="${EC2_KEYPAIR_NAME:-}"
SSH_PUBLIC_KEY="${SSH_PUBLIC_KEY:-$HOME/.ssh/id_rsa.pub}"

# Prevent AWS CLI paging
export AWS_PAGER=""

trap 'echo "❌ Failed. Check IAM permissions, EKS Add-on policies, and VPC settings. See logs above." >&2' ERR

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing required CLI: $1" >&2; exit 1; }; }
need aws
need kubectl
need eksctl

echo ">>> Using:
    CLUSTER_NAME     = ${CLUSTER_NAME}
    AWS_REGION       = ${AWS_REGION}
    NODE_TYPE        = ${NODE_TYPE}
    NODE_COUNT       = ${NODE_COUNT}
    NODE_MIN         = ${NODE_MIN}
    NODE_MAX         = ${NODE_MAX}
    K8S_VERSION      = ${K8S_VERSION}
    ENABLE_SSH       = ${ENABLE_SSH}
    EC2_KEYPAIR_NAME = ${EC2_KEYPAIR_NAME:-<unset>}
    SSH_PUBLIC_KEY   = ${SSH_PUBLIC_KEY:-<unset>}
"

aws sts get-caller-identity >/dev/null

# --- Run preflight if available ---
if [[ -x "$(dirname "$0")/check_permissions.sh" ]]; then
  echo ">>> Running permissions preflight"
  if ! "$(dirname "$0")/check_permissions.sh"; then
    echo ">>> Permissions preflight failed; fix IAM and re-run." >&2
    exit 1
  fi
fi

# --- Prefer YAML config if present ---
YAML_PATH="$(dirname "$0")/../cluster.yaml"
if [[ -f "$YAML_PATH" ]]; then
  echo ">>> Found cluster config: $YAML_PATH"
  echo ">>> Creating cluster from config"
  eksctl create cluster -f "$YAML_PATH"
else
  echo ">>> No cluster.yaml found; falling back to inline flags"

  SSH_ARGS=()
  if [[ "${ENABLE_SSH}" == "1" ]]; then
    if [[ -n "${EC2_KEYPAIR_NAME}" ]]; then
      echo ">>> Using existing EC2 key pair: ${EC2_KEYPAIR_NAME}"
      SSH_ARGS=(--ssh-access --ssh-public-key "${EC2_KEYPAIR_NAME}")
    else
      if [[ -f "${SSH_PUBLIC_KEY}" ]]; then
        echo ">>> Using local SSH public key: ${SSH_PUBLIC_KEY}"
        SSH_ARGS=(--ssh-access --ssh-public-key "${SSH_PUBLIC_KEY}")
      else
        echo ">>> No SSH key found at ${SSH_PUBLIC_KEY}; creating new key"
        need ssh-keygen
        key_base="${HOME}/.ssh/eks_${CLUSTER_NAME}"
        ssh-keygen -t ed25519 -N "" -C "${USER:-eks}@${HOSTNAME:-host}" -f "${key_base}" >/dev/null
        SSH_PUBLIC_KEY="${key_base}.pub"
        echo ">>> Created ${SSH_PUBLIC_KEY}"
        SSH_ARGS=(--ssh-access --ssh-public-key "${SSH_PUBLIC_KEY}")
      fi
    fi
  else
    echo ">>> SSH access disabled (ENABLE_SSH=0)"
  fi

  echo ">>> Creating EKS cluster '${CLUSTER_NAME}' in ${AWS_REGION}"
  cmd=(eksctl create cluster
    --name "${CLUSTER_NAME}"
    --region "${AWS_REGION}"
    --version "${K8S_VERSION}"
    --managed
    --node-type "${NODE_TYPE}"
    --nodes "${NODE_COUNT}"
    --nodes-min "${NODE_MIN}"
    --nodes-max "${NODE_MAX}"
    --with-oidc
    --node-ami-family AmazonLinux2023
    --node-private-networking
  )

  if (( ${#SSH_ARGS[@]} )); then
    cmd+=("${SSH_ARGS[@]}")
  fi

  "${cmd[@]}"
fi