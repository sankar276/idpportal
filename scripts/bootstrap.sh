#!/usr/bin/env bash
set -euo pipefail

# IDP Portal Bootstrap Script
# Two-stage bootstrap: install ArgoCD + ESO, then ArgoCD manages everything else

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$SCRIPT_DIR")"

CLUSTER_NAME="${CLUSTER_NAME:-idpportal-dev}"
REPO_URL="${REPO_URL:-https://github.com/your-org/idpportal.git}"
REPO_BRANCH="${REPO_BRANCH:-main}"

echo "=== IDP Portal Bootstrap ==="
echo "Cluster: $CLUSTER_NAME"
echo "Repo: $REPO_URL ($REPO_BRANCH)"
echo ""

# Step 1: Verify cluster access
echo "[1/5] Verifying cluster access..."
kubectl cluster-info > /dev/null 2>&1 || {
    echo "ERROR: Cannot connect to cluster. Ensure kubectl is configured."
    exit 1
}
echo "  Connected to cluster"

# Step 2: Install ArgoCD
echo "[2/5] Installing Argo CD..."
kubectl create namespace argocd --dry-run=client -o yaml | kubectl apply -f -
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update argo
helm upgrade --install argocd argo/argo-cd \
    --namespace argocd \
    --set server.extraArgs[0]="--insecure" \
    --set applicationSet.enabled=true \
    --wait --timeout 5m
echo "  Argo CD installed"

# Step 3: Install External Secrets Operator
echo "[3/5] Installing External Secrets Operator..."
kubectl create namespace external-secrets --dry-run=client -o yaml | kubectl apply -f -
helm repo add external-secrets https://charts.external-secrets.io
helm repo update external-secrets
helm upgrade --install external-secrets external-secrets/external-secrets \
    --namespace external-secrets \
    --set installCRDs=true \
    --wait --timeout 3m
echo "  External Secrets Operator installed"

# Step 4: Configure ArgoCD repo
echo "[4/5] Configuring ArgoCD repository..."
kubectl apply -f - <<EOF
apiVersion: v1
kind: Secret
metadata:
  name: idpportal-repo
  namespace: argocd
  labels:
    argocd.argoproj.io/secret-type: repository
type: Opaque
stringData:
  type: git
  url: ${REPO_URL}
EOF
echo "  Repository configured"

# Step 5: Apply root ApplicationSet
echo "[5/5] Applying root ApplicationSet (App of Apps)..."
helm upgrade --install addons "${ROOT_DIR}/packages/addons" \
    --namespace argocd \
    --set repoURL="${REPO_URL}" \
    --set targetRevision="${REPO_BRANCH}" \
    --wait --timeout 3m
echo "  Root ApplicationSet applied"

echo ""
echo "=== Bootstrap Complete ==="
echo ""
echo "ArgoCD will now manage all platform addons."
echo ""
echo "Access ArgoCD:"
echo "  kubectl port-forward svc/argocd-server -n argocd 8080:443"
echo "  Username: admin"
echo "  Password: kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 -d"
echo ""
