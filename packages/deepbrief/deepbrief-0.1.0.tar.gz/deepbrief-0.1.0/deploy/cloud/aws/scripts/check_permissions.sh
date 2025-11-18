#!/usr/bin/env bash
set -euo pipefail

# Verifies the current principal has the typical permissions needed for eksctl cluster creation.
# Requires: aws CLI, jq, and iam:SimulatePrincipalPolicy permission.

need() { command -v "$1" >/dev/null 2>&1 || { echo "Missing required CLI: $1" >&2; exit 1; }; }
need aws
need jq

echo ">>> Getting AWS caller identity"
IDENTITY_JSON=$(aws sts get-caller-identity)
ACCOUNT_ID=$(jq -r '.Account' <<<"$IDENTITY_JSON")
RAW_ARN=$(jq -r '.Arn' <<<"$IDENTITY_JSON")
echo "    Account: $ACCOUNT_ID"
echo "    ARN:     $RAW_ARN"

# Convert STS assumed-role ARN to IAM role ARN for simulation
if [[ "$RAW_ARN" == arn:aws:sts::*:assumed-role/*/* ]]; then
  ROLE_NAME=$(awk -F'/' '{print $2}' <<<"$RAW_ARN")
  PRINCIPAL_ARN="arn:aws:iam::${ACCOUNT_ID}:role/${ROLE_NAME}"
else
  PRINCIPAL_ARN="$RAW_ARN"
fi
echo ">>> Using principal for simulation: $PRINCIPAL_ARN"

# Actions eksctl typically needs (control plane + nodegroup + OIDC + CFN + EC2 + Addons + service-linked role)
ACTIONS=(
  # --- EKS control plane + nodegroups ---
  "eks:CreateCluster"
  "eks:DescribeCluster"
  "eks:DescribeClusterVersions"
  "eks:DeleteCluster"
  "eks:TagResource"
  "eks:CreateNodegroup"
  "eks:DescribeNodegroup"
  "eks:DeleteNodegroup"

  # --- EKS managed add-ons (since EKS 1.28+) ---
  "eks:ListAddons"
  "eks:DescribeAddon"
  "eks:CreateAddon"
  "eks:UpdateAddon"
  "eks:DeleteAddon"
  "eks:DescribeAddonVersions"
  "eks:DescribeAddonConfiguration"

  # --- IAM for roles + IRSA (OIDC) ---
  "iam:CreateRole"
  "iam:GetRole"
  "iam:AttachRolePolicy"
  "iam:PassRole"
  "iam:CreateOpenIDConnectProvider"
  "iam:GetOpenIDConnectProvider"
  "iam:TagOpenIDConnectProvider"
  "iam:ListAttachedRolePolicies"

  # --- Service-linked role for EKS (if not present yet) ---
  "iam:CreateServiceLinkedRole"

  # --- CloudFormation (eksctl uses CFN stacks) ---
  "cloudformation:CreateStack"
  "cloudformation:UpdateStack"
  "cloudformation:DescribeStacks"
  "cloudformation:DeleteStack"

  # --- EC2 networking (describes + minimal create + tags) ---
  "ec2:DescribeVpcs"
  "ec2:DescribeSubnets"
  "ec2:DescribeRouteTables"
  "ec2:DescribeSecurityGroups"
  "ec2:DescribeAvailabilityZones"
  "ec2:CreateSecurityGroup"
  "ec2:CreateTags"

  # --- S3 (bucket for workflow artifacts) ---
  "s3:CreateBucket"
  "s3:HeadBucket"
  "s3:PutBucketTagging"
)

echo ">>> Simulating permissions with IAM policy simulator"
SIM_JSON=$(aws iam simulate-principal-policy \
  --policy-source-arn "$PRINCIPAL_ARN" \
  --action-names "${ACTIONS[@]}" \
  --output json)

DENIED=$(jq -r '.EvaluationResults[] | select(.EvalDecision!="allowed") | .EvalActionName' <<<"$SIM_JSON" | sort -u)

if [[ -z "$DENIED" ]]; then
  echo "✅ All simulated actions are ALLOWED for $PRINCIPAL_ARN"
  exit 0
else
  echo "❌ Some actions are NOT allowed for $PRINCIPAL_ARN:"
  echo "$DENIED" | sed 's/^/   - /'
  cat <<'EOF'

Remediation tips (pick one path):
  • Quickest (dev/testing): attach AdministratorAccess to your user.

  • Granular (recommended for production):
    Add EKS, CloudFormation, IAM, and EC2 permissions.
    A minimal custom inline policy for the EKS portion can be one of the following:

    --- Simple (grant all EKS actions) ---
    {
      "Version": "2012-10-17",
      "Statement": [
        { "Effect": "Allow", "Action": "eks:*", "Resource": "*" }
      ]
    }

    --- Minimal (just what eksctl typically needs, including Add-ons) ---
    {
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Action": [
            "eks:CreateCluster",
            "eks:DescribeCluster",
            "eks:DescribeClusterVersions",
            "eks:DeleteCluster",
            "eks:TagResource",
            "eks:CreateNodegroup",
            "eks:DescribeNodegroup",
            "eks:DeleteNodegroup",
            "eks:ListAddons",
            "eks:DescribeAddon",
            "eks:CreateAddon",
            "eks:UpdateAddon",
            "eks:DeleteAddon",
            "eks:DescribeAddonVersions",
            "eks:DescribeAddonConfiguration"
          ],
          "Resource": "*"
        }
      ]
    }

    You also need these AWS-managed policies attached:
      - CloudFormationFullAccess
      - IAMFullAccess (or equivalent IAM actions including iam:CreateServiceLinkedRole)
      - AmazonEC2FullAccess

    Optional but recommended for simplicity:
      - AmazonEKSFullAccess

After adding permissions, re-run this script and then run create_cluster.sh.
EOF
  exit 2
fi
