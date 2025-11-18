#!/usr/bin/env bash
set -euo pipefail

missing=()

install_aws_cli() {
  if command -v aws >/dev/null 2>&1; then
    echo ">>> aws CLI already installed: $(aws --version)"
    return
  fi

  echo ">>> Installing AWS CLI v2 (official pkg, requires sudo)"
  pkg_path="$(mktemp /tmp/awscli-XXXX.pkg)"
  curl -fsSL "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "${pkg_path}"
  sudo installer -pkg "${pkg_path}" -target /
  rm -f "${pkg_path}"
  echo ">>> aws CLI installed: $(aws --version)"
}

install_kubectl() {
  if command -v kubectl >/dev/null 2>&1; then
    echo ">>> kubectl already installed: $(kubectl version --client || kubectl version --client | head -n1)"
    return
  fi

  if command -v brew >/dev/null 2>&1; then
    echo ">>> Installing kubectl with Homebrew"
    brew install kubectl
  else
    missing+=("kubectl")
  fi
}

install_eksctl() {
  if command -v eksctl >/dev/null 2>&1; then
    echo ">>> eksctl already installed: $(eksctl version)"
    return
  fi

  if command -v brew >/dev/null 2>&1; then
    echo ">>> Adding AWS Homebrew tap and installing eksctl"
    brew tap aws/tap
    brew install aws/tap/eksctl
  else
    missing+=("eksctl")
  fi
}

install_helm() {
  if command -v helm >/dev/null 2>&1; then
    echo ">>> helm already installed: $(helm version --short)"
    return
  fi

  if command -v brew >/dev/null 2>&1; then
    echo ">>> Installing helm with Homebrew"
    brew install helm
  else
    missing+=("helm")
  fi
}

install_aws_cli
install_kubectl
install_eksctl
install_helm

if ((${#missing[@]} > 0)); then
  cat <<EOF

The following tools still need to be installed manually (Homebrew not available):
${missing[*]}

Refer to:
- AWS CLI: https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html
- kubectl: https://docs.aws.amazon.com/eks/latest/userguide/install-kubectl.html
- eksctl: https://eksctl.io/introduction/#installation
- Helm: https://helm.sh/docs/intro/install/
EOF
fi
