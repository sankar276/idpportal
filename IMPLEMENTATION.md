# IDP Portal - Getting Started & Execution Guide

Complete guide to run, deploy, and operate the IDP Portal. Whether you're setting up locally for development or deploying to production on AWS EKS, follow the relevant sections below.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [AWS Infrastructure](#aws-infrastructure)
- [EKS Cluster Bootstrap](#eks-cluster-bootstrap)
- [Platform Services Configuration](#platform-services-configuration)
- [Application Deployment](#application-deployment)
- [CI/CD Pipeline Setup](#cicd-pipeline-setup)
- [Self-Service & Backstage Templates](#self-service--backstage-templates)
- [Production Hardening](#production-hardening)
- [Verification Checklist](#verification-checklist)
- [Troubleshooting](#troubleshooting)
- [Current Status & Roadmap](#current-status--roadmap)

---

## Prerequisites

### Tools

| Tool | Version | Purpose | Install |
|------|---------|---------|---------|
| Docker | 24+ | Local containers | [docs.docker.com](https://docs.docker.com/get-docker/) |
| Docker Compose | v2+ | Multi-container dev | Included with Docker |
| Python | 3.12+ | AI backend | [python.org](https://www.python.org/downloads/) |
| uv | latest | Python package manager | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Node.js | 20+ | Portal UI | [nodejs.org](https://nodejs.org/) |
| Go | 1.22+ | Policy agent | [go.dev](https://go.dev/dl/) |
| Terraform | 1.7+ | Infrastructure | [terraform.io](https://developer.hashicorp.com/terraform/install) |
| AWS CLI | v2 | Cloud management | [aws.amazon.com/cli](https://aws.amazon.com/cli/) |
| kubectl | 1.28+ | K8s management | [kubernetes.io](https://kubernetes.io/docs/tasks/tools/) |
| Helm | 3.14+ | Package management | [helm.sh](https://helm.sh/docs/intro/install/) |
| gh | latest | GitHub CLI | [cli.github.com](https://cli.github.com/) |

### Accounts & Access

| Service | What You Need | Where to Get It |
|---------|--------------|-----------------|
| AWS Account | IAM role with EKS, VPC, IAM, KMS, SecretsManager | [aws.amazon.com](https://aws.amazon.com/) |
| Anthropic API | API key for Claude | [console.anthropic.com](https://console.anthropic.com/) |
| GitHub | Personal access token with `repo`, `workflow` scopes | GitHub Settings > Developer settings > PAT |
| Domain Name | Route53 hosted zone (optional, for TLS) | AWS Route53 |

---

## Local Development

### 1. Clone and Configure

```bash
git clone https://github.com/sankar276/idpportal.git
cd idpportal

cp .env.example .env
```

Edit `.env` with your values:

```bash
# Required for AI features
ANTHROPIC_API_KEY=sk-ant-xxxxx

# Database (local Docker defaults)
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/idpportal
REDIS_URL=redis://localhost:6379/0

# Keycloak (local Docker defaults)
KEYCLOAK_URL=http://localhost:8080
KEYCLOAK_REALM=idpportal
KEYCLOAK_CLIENT_ID=idpportal-ui
KEYCLOAK_CLIENT_SECRET=your-client-secret

# Optional: Enable additional agents
GITHUB_TOKEN=ghp_xxxxx
# JIRA_BASE_URL=https://your-org.atlassian.net
# SLACK_BOT_TOKEN=xoxb-xxxxx
# ARGOCD_SERVER_URL=https://argocd.example.com
```

### 2. Start All Services

```bash
# Start all 8 containers (Postgres, Redis, Keycloak, Vault, backend, UI, etc.)
docker compose up -d

# Verify everything is running
docker compose ps

# Watch backend logs for any startup errors
docker compose logs -f backend
```

### 3. Verify

| Service | URL | Credentials |
|---------|-----|-------------|
| Portal UI | http://localhost:3000 | via Keycloak |
| Backend API (Swagger) | http://localhost:8000/docs | - |
| Backend Health | http://localhost:8000/api/v1/health | - |
| Keycloak Admin | http://localhost:8080 | admin / admin |
| Vault | http://localhost:8200 | Token: `dev-root-token` |

### 4. Hot Reload Development

```bash
# Option A: Docker Compose with volume mounts
docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up

# Option B: Run backend natively
cd backend && uv sync && uv run uvicorn app.main:app --reload --port 8000

# Option C: Run UI natively
cd ui && npm install && npm run dev
```

### 5. Policy Agent (Local)

```bash
cd policy-agent

go mod tidy                 # Download dependencies
go test ./...               # Run tests

# Build and test CLI
go build -o bin/policy-agent ./cmd/policy-agent
./bin/policy-agent validate \
  --domain kubernetes \
  --file examples/deployment.yaml \
  --policies-dir ../policies

# Build webhook server
go build -o bin/webhook ./cmd/webhook
```

---

## AWS Infrastructure

### 1. Configure AWS Access

```bash
aws configure                    # or: aws sso login --profile your-profile
aws sts get-caller-identity      # verify access
```

### 2. Create Terraform State Backend (One-Time)

```bash
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# S3 bucket for state
aws s3api create-bucket \
  --bucket idpportal-terraform-state-${ACCOUNT_ID} \
  --region us-west-2 \
  --create-bucket-configuration LocationConstraint=us-west-2

aws s3api put-bucket-versioning \
  --bucket idpportal-terraform-state-${ACCOUNT_ID} \
  --versioning-configuration Status=Enabled

aws s3api put-bucket-encryption \
  --bucket idpportal-terraform-state-${ACCOUNT_ID} \
  --server-side-encryption-configuration \
  '{"Rules":[{"ApplyServerSideEncryptionByDefault":{"SSEAlgorithm":"aws:kms"}}]}'

# DynamoDB table for state locking
aws dynamodb create-table \
  --table-name idpportal-terraform-lock \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST \
  --region us-west-2
```

### 3. Update Backend Configuration

Edit `infrastructure/backend.tf`:

```hcl
terraform {
  backend "s3" {
    bucket         = "idpportal-terraform-state-<YOUR_ACCOUNT_ID>"
    key            = "idpportal/terraform.tfstate"
    region         = "us-west-2"
    dynamodb_table = "idpportal-terraform-lock"
    encrypt        = true
  }
}
```

### 4. Configure Your Environment

Edit `infrastructure/envs/dev.tfvars` (or `staging.tfvars` / `prod.tfvars`):

```hcl
cluster_name     = "idpportal-dev"
cluster_version  = "1.31"
environment      = "dev"
region           = "us-west-2"
vpc_cidr         = "10.0.0.0/16"
domain_name      = "dev.idp.yourdomain.com"
gitops_repo_url  = "https://github.com/sankar276/idpportal.git"

node_instance_types = ["m6i.xlarge"]
node_min_size       = 3
node_max_size       = 6
node_desired_size   = 3
```

### 5. Provision (~20-30 minutes)

```bash
cd infrastructure
terraform init
terraform plan -var-file=envs/dev.tfvars -out=plan.tfplan
terraform apply plan.tfplan
terraform output -json > ../terraform-outputs.json
```

### 6. Connect to the Cluster

```bash
aws eks update-kubeconfig --name idpportal-dev --region us-west-2
kubectl get nodes        # all nodes should be "Ready"
kubectl cluster-info
```

---

## EKS Cluster Bootstrap

The bootstrap script installs ArgoCD and External Secrets Operator, then applies the root ApplicationSet that automatically deploys all 14 platform addons.

### 1. Pre-Check

```bash
kubectl get nodes -o wide                                 # all nodes Ready
kubectl get secret cluster-metadata -n argocd -o yaml     # GitOps Bridge secret exists
```

### 2. Run Bootstrap

```bash
chmod +x scripts/bootstrap.sh
./scripts/bootstrap.sh
```

What this does:
1. Verifies EKS cluster connectivity
2. Installs ArgoCD via Helm
3. Installs External Secrets Operator via Helm
4. Configures the Git repository source
5. Applies the root ApplicationSet (`packages/addons/`)

### 3. Access ArgoCD

```bash
# Get admin password
kubectl get secret argocd-initial-admin-secret -n argocd \
  -o jsonpath="{.data.password}" | base64 -d && echo

# Port-forward
kubectl port-forward svc/argocd-server -n argocd 8443:443

# Open https://localhost:8443 → Login: admin / <password>
```

### 4. Verify All Addons

```bash
kubectl get applications -n argocd

# All 14 should show "Synced" + "Healthy":
# argo-cd, backstage, cert-manager, external-dns, external-secrets,
# flux-system, ingress-nginx, kafka, keycloak, opa-gatekeeper,
# policy-agent, rancher, vault, ai-platform
```

---

## Platform Services Configuration

### Keycloak

```bash
kubectl port-forward svc/keycloak -n keycloak 8080:80
# Open http://localhost:8080/admin
```

Configure in the admin console:
1. Verify realm `idpportal` exists (imported automatically)
2. Verify clients: `idpportal-ui`, `argocd`, `backstage`, `vault`
3. Verify roles: `platform-admin`, `developer`, `viewer`
4. Create an initial admin user and assign `platform-admin` role

**Enterprise IdP (optional):**
```bash
kubectl apply -f packages/keycloak/overlays/okta-broker.yaml       # Okta
kubectl apply -f packages/keycloak/overlays/forgerock-broker.yaml  # ForgeRock
```

### Vault

```bash
kubectl port-forward svc/vault -n vault 8200:8200

# Initialize (save unseal keys and root token securely!)
kubectl exec -it vault-0 -n vault -- vault operator init -key-shares=5 -key-threshold=3

# Unseal (repeat with 3 different keys)
kubectl exec -it vault-0 -n vault -- vault operator unseal <key-1>
kubectl exec -it vault-0 -n vault -- vault operator unseal <key-2>
kubectl exec -it vault-0 -n vault -- vault operator unseal <key-3>

# Enable secrets engine + OIDC auth
kubectl exec -it vault-0 -n vault -- vault secrets enable -path=secret kv-v2
kubectl exec -it vault-0 -n vault -- vault auth enable oidc
```

### AWS Secrets Manager

Store secrets that External Secrets Operator will sync into K8s:

```bash
aws secretsmanager create-secret --name idpportal/config --secret-string '{
  "ANTHROPIC_API_KEY": "sk-ant-xxxxx",
  "GITHUB_TOKEN": "ghp_xxxxx",
  "DATABASE_URL": "postgresql+asyncpg://user:pass@rds-endpoint:5432/idpportal"
}'

aws secretsmanager create-secret --name idpportal/keycloak --secret-string '{
  "KEYCLOAK_CLIENT_SECRET": "xxxxx"
}'
```

### Kafka

```bash
kubectl get kafkas -n kafka                        # verify brokers
kubectl get pods -n kafka -l strimzi.io/kind=Kafka  # check readiness

# Test with a topic
kubectl apply -f - <<EOF
apiVersion: kafka.strimzi.io/v1beta2
kind: KafkaTopic
metadata:
  name: test-topic
  namespace: kafka
  labels:
    strimzi.io/cluster: idpportal-kafka
spec:
  partitions: 3
  replicas: 3
  config:
    retention.ms: 604800000
EOF

kubectl get kafkatopics -n kafka
```

---

## Application Deployment

### Build & Push Docker Images

```bash
# Backend
cd backend
docker build -t idpportal-backend:latest .
docker tag idpportal-backend:latest <ECR_REGISTRY>/idpportal-backend:v0.1.0
aws ecr get-login-password --region us-west-2 | docker login --username AWS --password-stdin <ECR_REGISTRY>
docker push <ECR_REGISTRY>/idpportal-backend:v0.1.0

# UI
cd ../ui
docker build --build-arg NEXT_PUBLIC_API_URL=https://api.yourdomain.com -t idpportal-ui:latest .
docker tag idpportal-ui:latest <ECR_REGISTRY>/idpportal-ui:v0.1.0
docker push <ECR_REGISTRY>/idpportal-ui:v0.1.0

# Policy Agent
cd ../policy-agent
go test ./... -v
docker build -t policy-agent:latest .
docker tag policy-agent:latest <ECR_REGISTRY>/policy-agent:v0.1.0
docker push <ECR_REGISTRY>/policy-agent:v0.1.0
```

### Update Helm Values

Edit `packages/ai-platform/values.yaml`:

```yaml
backend:
  replicaCount: 2
  image:
    repository: <ECR_REGISTRY>/idpportal-backend
    tag: v0.1.0
  port: 8000
  env:
    APP_ENV: production
    DEBUG: "false"
    CORS_ALLOWED_ORIGINS: "https://portal.yourdomain.com"
    KEYCLOAK_URL: "https://keycloak.yourdomain.com"
    KEYCLOAK_REALM: "idpportal"
    VAULT_ADDR: "http://vault.vault.svc:8200"
    POLICY_AGENT_URL: "http://policy-agent.policy-agent.svc:8443"
    BACKSTAGE_URL: "http://backstage.backstage.svc:7007"
  resources:
    requests: { cpu: 250m, memory: 512Mi }
    limits: { cpu: "1", memory: 1Gi }

ui:
  replicaCount: 2
  image:
    repository: <ECR_REGISTRY>/idpportal-ui
    tag: v0.1.0
  port: 3000
  env:
    KEYCLOAK_URL: "https://keycloak.yourdomain.com"
    KEYCLOAK_REALM: "idpportal"
    KEYCLOAK_CLIENT_ID: "idpportal-ui"
    BACKEND_URL: "http://idpportal-backend.idpportal.svc:8000"
```

Edit `packages/policy-agent/values.yaml`:

```yaml
image:
  repository: <ECR_REGISTRY>/policy-agent
  tag: v0.1.0
```

### Create Secrets & Enable Webhook

```bash
# Policy Agent API key
kubectl create secret generic policy-agent-secrets \
  -n policy-agent --from-literal=anthropic-api-key=sk-ant-xxxxx

# Label namespaces for policy validation
kubectl label namespace default policy-agent/validate=true
kubectl label namespace idpportal policy-agent/validate=true
```

### Verify Deployment

```bash
# ArgoCD auto-syncs from git. Check status:
kubectl get pods -n idpportal
kubectl logs -n idpportal -l app=idpportal-backend -f

# Health check
kubectl port-forward svc/idpportal-backend -n idpportal 8000:8000
curl http://localhost:8000/api/v1/health

# UI
kubectl port-forward svc/idpportal-ui -n idpportal 3000:3000
open http://localhost:3000
```

### Test Policy Webhook

```bash
# This should be rejected (uses :latest tag + privileged mode)
kubectl apply -f - <<EOF
apiVersion: apps/v1
kind: Deployment
metadata:
  name: test-bad-deploy
spec:
  replicas: 1
  selector:
    matchLabels: { app: test }
  template:
    metadata:
      labels: { app: test }
    spec:
      containers:
        - name: test
          image: nginx:latest
          securityContext:
            privileged: true
EOF
# Expected: admission webhook denies with policy violations
```

---

## CI/CD Pipeline Setup

### GitHub Repository Configuration

**Secrets** (Settings > Secrets and Variables > Actions):

| Secret | Value | Used By |
|--------|-------|---------|
| `AWS_ROLE_ARN` | `arn:aws:iam::<ACCOUNT>:role/github-actions-role` | terraform-*, release |
| `ECR_REGISTRY` | `<ACCOUNT>.dkr.ecr.us-west-2.amazonaws.com` | release |

**Variables:**

| Variable | Value |
|----------|-------|
| `TF_ENVIRONMENT` | `dev` / `staging` / `prod` |

**Environments** (Settings > Environments):
- `staging` — no protection rules
- `production` — require manual approval

### OIDC for AWS (Recommended)

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com
# Then create IAM role with trust policy for your repo
# See: https://docs.github.com/en/actions/security-for-github-actions/security-hardening-your-deployments/configuring-openid-connect-in-amazon-web-services
```

### Test the Pipelines

```bash
# Feature branch + PR triggers CI + policy gate
git checkout -b feature/test-ci
git commit --allow-empty -m "test: verify CI pipelines"
git push -u origin feature/test-ci
gh pr create --title "test: verify CI" --body "Testing CI pipelines"

# Tag triggers release pipeline (Docker build + ECR push)
git tag v0.1.0
git push origin v0.1.0
gh run watch
```

### Pipelines Summary

| Workflow | Trigger | What It Does |
|----------|---------|--------------|
| `ci-backend` | Push/PR to `backend/**` | Ruff lint + pytest with Postgres/Redis |
| `ci-ui` | Push/PR to `ui/**` | ESLint + Next.js build |
| `ci-policy-agent` | Push/PR to `policy-agent/**` | go vet + go test + build |
| `policy-gate` | PR with `*.yaml`/`*.tf` | Validates configs against Rego policies |
| `terraform-plan` | PR to `infrastructure/**` | Terraform plan + PR comment |
| `terraform-apply` | Merge to main `infrastructure/**` | Terraform plan + apply (with state lock) |
| `release` | Git tag `v*` | Docker build matrix, ECR push, Helm update |

---

## Self-Service & Backstage Templates

### Register Templates in Backstage

```bash
kubectl port-forward svc/backstage -n backstage 7007:7007
open http://localhost:7007
```

Navigate to **Create** > **Register Existing Component** and add:
- `https://github.com/sankar276/idpportal/blob/main/templates/microservice/template.yaml`
- `https://github.com/sankar276/idpportal/blob/main/templates/kafka-topic/template.yaml`
- `https://github.com/sankar276/idpportal/blob/main/templates/database/template.yaml`

### Test via AI Chat

Open the portal at `https://portal.yourdomain.com/chat` and try:

```
"Create a new microservice called payments-api in Python"
"Create a Kafka topic called orders.events with 6 partitions"
"Validate my deployment.yaml against policies"
"List all ArgoCD applications"
"Show me pods in the kafka namespace"
"What incidents are open in PagerDuty?"
```

### Test via Self-Service UI

Navigate to **Self-Service** in the portal sidebar:
1. Pick a template (Microservice, Kafka Topic, Database, etc.)
2. Fill in the parameters
3. Click **Validate & Provision**
4. Watch real-time progress via SSE streaming

---

## Production Hardening

### Security

```bash
# Restrict EKS API endpoint in prod.tfvars
cluster_endpoint_public_access = false

# Enable network policies (default deny)
kubectl apply -f - <<EOF
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: default-deny-all
  namespace: idpportal
spec:
  podSelector: {}
  policyTypes: [Ingress, Egress]
EOF

# Switch policy webhook to Fail mode
# Edit packages/policy-agent/values.yaml → webhook.failurePolicy: Fail

# Rotate all secrets (Keycloak client secrets, Vault tokens, API keys)
```

### Observability

```bash
# Prometheus + Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install monitoring prometheus-community/kube-prometheus-stack \
  -n monitoring --create-namespace

# ServiceMonitor for backend metrics
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: idpportal-backend
  namespace: idpportal
spec:
  selector:
    matchLabels: { app: idpportal-backend }
  endpoints:
    - port: http
      path: /api/v1/metrics
EOF
```

### Backups

```bash
# Velero for K8s cluster backup
helm repo add vmware-tanzu https://vmware-tanzu.github.io/helm-charts
helm install velero vmware-tanzu/velero -n velero --create-namespace \
  --set configuration.backupStorageLocation[0].bucket=idpportal-backups \
  --set configuration.backupStorageLocation[0].provider=aws

velero schedule create daily-backup --schedule="0 2 * * *"
```

---

## Verification Checklist

### Infrastructure
- [ ] EKS cluster running with 3+ nodes
- [ ] VPC with public/private subnets across 3 AZs
- [ ] KMS key for Vault auto-unseal
- [ ] Secrets Manager has required secrets
- [ ] IAM roles for ESO, External DNS, cert-manager

### Platform Services
- [ ] ArgoCD: all 14 Applications synced + healthy
- [ ] Keycloak realm `idpportal` configured with 4 clients
- [ ] Vault initialized, unsealed, accessible
- [ ] Kafka cluster: 3 brokers running
- [ ] cert-manager issued TLS certificates
- [ ] External DNS created Route53 records
- [ ] Ingress-NGINX NLB provisioned

### Application
- [ ] `GET /api/v1/health` returns 200
- [ ] `GET /api/v1/ready` returns 200
- [ ] UI loads at portal URL
- [ ] Keycloak OIDC login works
- [ ] AI chat responds to prompts
- [ ] Agent list returns 13 agents

### Policy & Security
- [ ] Policy Agent webhook receiving requests
- [ ] Non-compliant deployments rejected
- [ ] Rego policies load for all 5 domains
- [ ] CI/CD policy gate blocks non-compliant PRs

### Self-Service
- [ ] Backstage templates registered
- [ ] Microservice template creates repo + ArgoCD app
- [ ] Kafka topic template creates KafkaTopic CR
- [ ] Chat-based provisioning triggers multi-agent workflow

---

## Troubleshooting

### ArgoCD Application Stuck in "Progressing"

```bash
kubectl describe application <app-name> -n argocd
kubectl patch application <app-name> -n argocd \
  --type merge -p '{"operation":{"sync":{"revision":"HEAD"}}}'
```

### External Secrets Not Syncing

```bash
kubectl get clustersecretstore -A
kubectl get externalsecret -A
kubectl describe externalsecret <name> -n <namespace>
```

### Policy Agent Webhook Rejecting Everything

```bash
kubectl logs -n policy-agent -l app=policy-agent -f

# Temporarily disable
kubectl delete validatingwebhookconfiguration policy-agent-webhook
# Re-enable after fix
kubectl apply -f packages/policy-agent/templates/webhook.yaml
```

### Keycloak OIDC Login Fails

```bash
kubectl port-forward svc/keycloak -n keycloak 8080:80
# Check: redirect URIs match portal URL, client protocol is openid-connect
```

### Backend Database Connection Issues

```bash
kubectl exec -it deployment/idpportal-backend -n idpportal -- env | grep DATABASE
# If empty, check ExternalSecret sync or set DATABASE_URL in env config
```

### Terraform State Lock Stuck

```bash
cd infrastructure && terraform force-unlock <LOCK_ID>
```

---

## Current Status & Roadmap

### What's Ready

| Component | Notes |
|-----------|-------|
| Terraform Infrastructure | VPC, EKS, IAM, KMS, GitOps Bridge — fully functional |
| Helm Charts (14 addons) | All charts with values, templates, dependencies |
| Policy Engine (OPA/Rego) | 5 domains, 33 rules, Go binary, 4 integration modes |
| CI/CD Workflows | 7 pipelines: build, test, policy gate, deploy |
| GitOps Bridge Pattern | Terraform -> K8s Secret -> ApplicationSet -> Helm |
| Bootstrap Script | 5-step automated cluster setup |
| 13 AI Agents | GitHub, ArgoCD, Flux, Jira, Slack, PagerDuty, Backstage, Kubernetes, Kafka, Vault, Rancher, Policy, Knowledge |
| Architecture Documentation | README + 6 SVG diagrams |

### Known Limitations

| Area | Status | Detail |
|------|--------|--------|
| Self-Service Engine | Stub | `POST /self-service/provision` returns mock data — needs workflow orchestration wiring |
| UI Data Pages | Partial | 6 of 12 pages use mock data instead of real API calls |
| Tests | Minimal | Health check tests only — need agent/tool/integration/E2E tests |
| Database Migrations | Not created | Alembic dependency exists but no migration files |
| Login Page | Not created | Auth middleware redirects to `/login` but page component doesn't exist yet |

### Roadmap

1. Wire up self-service provisioning engine with real multi-agent workflows
2. Connect all UI pages to backend APIs (replace mock data)
3. Add comprehensive test suites (pytest, Jest/Playwright, Go test)
4. Create `/login` page component
5. Add Alembic database migrations
6. Add HorizontalPodAutoscaler for backend, UI, policy-agent
7. Build Prometheus + Grafana dashboards
8. Add Velero backup schedules
