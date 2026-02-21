# IDP Portal

A custom Internal Developer Portal combining GitOps-managed AWS infrastructure with an AI-powered multi-agent system for full-stack developer self-service with policy guardrails.

## Acknowledgments and References

This project draws architectural inspiration from the following open-source projects by the [CNOE](https://cnoe.io/) (Cloud Native Operational Excellence) community:

- **[CNOE AWS Reference Implementation](https://github.com/cnoe-io/reference-implementation-aws)** ([docs](https://cnoe.io/docs/reference-implementation/aws)) - The GitOps Bridge pattern used in this project (Terraform outputs -> K8s Secret annotations -> ArgoCD ApplicationSet cluster generator -> Helm values) is adapted from the CNOE reference architecture. The two-stage bootstrap approach (ArgoCD + ESO first, then ArgoCD manages everything) and the App-of-Apps ApplicationSet pattern also follow CNOE's design. CNOE is licensed under [Apache License 2.0](https://github.com/cnoe-io/reference-implementation-aws/blob/main/LICENSE).

- **[CAIPE - AI Platform Engineering](https://github.com/cnoe-io/ai-platform-engineering)** - The multi-agent AI architecture in this project is inspired by CAIPE's approach to applying AI agents to platform engineering tasks. The concepts of an LLM-based supervisor agent orchestrating specialized sub-agents, the use of the Model Context Protocol (MCP) for tool registration, and the Agent-to-Agent (A2A) protocol for inter-agent communication are informed by CAIPE's design. CAIPE is licensed under [Apache License 2.0](https://github.com/cnoe-io/ai-platform-engineering/blob/main/LICENSE).

- **[Policy Agent](https://github.com/sankar276/Policy_agent)** - The Go-based OPA/Rego policy validation agent integrated into this project is based on prior work by the author.

**What is original to this project:**
- The complete FastAPI backend implementation with 12 specialized AI agents (GitHub, ArgoCD, Flux, Jira, Slack, PagerDuty, Backstage, Kafka, Vault, Rancher, Policy, Backstage)
- The Next.js 15 portal UI with 12 pages, chat interface, and self-service wizard
- The self-service provisioning engine with multi-step workflows and policy gates
- The Keycloak identity broker pattern with Okta/ForgeRock overlays
- The specific Terraform module compositions for VPC, EKS, IAM, Vault, Kafka, and GitOps Bridge
- All Helm chart configurations and values for the 14 platform addons
- The CI/CD pipeline designs including the policy-gate workflow
- The OPA/Rego policy rules across 5 domains (kubernetes, kafka, terraform, cicd, gitops)
- The integration of the Policy Agent in 4 modes (K8s webhook, AI chat, CI/CD gate, Backstage templates)

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [System Architecture](#system-architecture)
- [AI Multi-Agent Architecture](#ai-multi-agent-architecture)
- [GitOps Bridge Pattern](#gitops-bridge-pattern)
- [Policy-as-Code Architecture](#policy-as-code-architecture)
- [Identity and Auth Architecture](#identity-and-auth-architecture)
- [Self-Service Flow](#self-service-flow)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Development](#development)
- [Deployment](#deployment)
- [CI/CD Pipelines](#cicd-pipelines)

---

## Architecture Overview

```
 Developers                                    Platform Engineers
     |                                                |
     v                                                v
 +-----------+                                +--------------+
 | Portal UI |  Next.js 15 / React 19        | Terraform    |
 | (SPA)     |  Tailwind + shadcn/ui         | Infrastructure|
 +-----+-----+                                +------+-------+
       |                                              |
       | HTTPS + Keycloak OIDC JWT                    | HCL
       |                                              v
 +-----v-----------------------------------------+  +------------------+
 |              AI Backend (FastAPI)               |  | AWS              |
 |                                                 |  |  EKS Cluster     |
 |  +-------------------------------------------+ |  |  VPC / Subnets   |
 |  |        Supervisor Agent (LangGraph)        | |  |  IAM Pod Identity|
 |  |  Intent classification -> Agent routing    | |  |  KMS (Vault)     |
 |  +-----+-----+-----+-----+-----+-----+------+ |  |  Secrets Manager |
 |        |     |     |     |     |     |        | |  +--------+---------+
 |  +-----v-+ +-v---+ +-v--++ +--v--+ +v----+   | |           |
 |  |GitHub | |Argo | |Flux | |Kafka| |Vault|   | |           | GitOps Bridge
 |  |Agent  | |CD   | |CD  | |Agent| |Agent|   | |           | (K8s Secret
 |  +-------+ |Agent| |Agnt| +-----+ +-----+   | |           |  annotations)
 |  +-------+ +-----+ +----+ +-----+ +-----+   | |           |
 |  |Jira   | |Slack | |PgDy| |Back| |Ranch|   | |           v
 |  |Agent  | |Agent | |Agnt| |stge| |er   |   | |  +--------+---------+
 |  +-------+ +------+ +----+ +----+ +-----+   | |  | ArgoCD           |
 |                                               | |  | ApplicationSet   |
 |  +----------+ +---------+ +----------------+ | |  | (cluster generator|
 |  |Policy    | |MCP      | |Self-Service    | | |  |  reads annotations|
 |  |Agent(Go) | |Server   | |Engine          | | |  |  -> Helm values)  |
 |  +----------+ +---------+ +----------------+ | |  +------------------+
 |                                               | |
 |  SSE Streaming | A2A Protocol | RAG/pgvector  | |  Platform Addons (14):
 +-----------------------+------------------------+ |  ArgoCD, Flux, Backstage
                         |                          |  Keycloak, Vault, Kafka
                         | HTTP/gRPC                |  Rancher, Cert-Manager
                         v                          |  External-DNS, External-
              +----------+-----------+              |  Secrets, Ingress-NGINX
              | Platform Services    |              |  OPA Gatekeeper,
              |  PostgreSQL+pgvector |              |  Policy Agent, AI Platform
              |  Redis               |
              |  Keycloak            |
              |  Vault               |
              |  Kafka (Redpanda)    |
              +----------------------+
```

---

## System Architecture

```
 +----------------------------------------------------------------------+
 |                         EXTERNAL SERVICES                             |
 |  GitHub API   Jira API   Slack API   PagerDuty API   Anthropic API   |
 +-------+----------+----------+----------+----------------+-----------+
         |          |          |          |                |
 +-------v----------v----------v----------v----------------v-----------+
 |                                                                      |
 |                        AI BACKEND (FastAPI)                          |
 |                                                                      |
 |  +----------------------------------------------------------------+ |
 |  |                  API Layer (/api/v1)                            | |
 |  |  POST /chat/stream (SSE)  |  GET /agents  |  POST /self-service| |
 |  +--------------+--------------------------------------------+---+ |
 |                 |                                             |     |
 |  +--------------v--------------+   +--------------------------v--+ |
 |  |   Supervisor Orchestrator   |   |   Self-Service Engine       | |
 |  |   (LangGraph StateGraph)    |   |                             | |
 |  |                             |   |  Workflows:                 | |
 |  |  1. Classify intent         |   |   create_service            | |
 |  |  2. Select agent(s)         |   |   create_kafka_topic        | |
 |  |  3. Execute tools           |   |   provision_database        | |
 |  |  4. Synthesize response     |   |   create_repo               | |
 |  |  5. Stream via SSE          |   |                             | |
 |  +--------------+--------------+   |  Each workflow chains:      | |
 |                 |                   |   validate -> create ->     | |
 |  +--------------v--------------+   |   deploy -> register ->     | |
 |  |    11 AI Sub-Agents         |   |   notify                    | |
 |  |                             |   +-----------------------------+ |
 |  |  github   argocd   flux    |                                    |
 |  |  jira     slack    pager   |   +-----------------------------+  |
 |  |  kafka    vault    rancher |   |  Services                   |  |
 |  |  backstage                 |   |   LLM (Claude/OpenAI)       |  |
 |  |                            |   |   Auth (Keycloak JWT)       |  |
 |  |  Each agent:               |   |   Database (pg+pgvector)    |  |
 |  |   BaseAgent ABC            |   |   Redis (cache/sessions)    |  |
 |  |   get_card() -> AgentCard  |   +-----------------------------+  |
 |  |   get_tools() -> MCP tools |                                    |
 |  |   invoke(task) -> result   |   +-----------------------------+  |
 |  +-----------------------------+   |  Protocols                 |  |
 |                                    |   MCP (tool registry)      |  |
 |  +-----------------------------+   |   A2A (agent-to-agent)     |  |
 |  |  Policy Agent (bridge)      |   +-----------------------------+  |
 |  |   Calls Go binary via HTTP  |                                   |
 |  |   validate / generate / fix |                                   |
 |  +--------------+--------------+                                   |
 +-----------------|--------------------------------------------------+
                   |
 +-----------------v--------------------------------------------------+
 |                     POLICY AGENT (Go)                               |
 |                                                                     |
 |  +--------------+  +--------------+  +---------------------------+ |
 |  |  CLI         |  |  HTTP API    |  |  K8s Admission Webhook    | |
 |  |  validate    |  |  /validate   |  |  ValidatingWebhookConfig  | |
 |  |  generate    |  |  /generate   |  |  Intercepts create/update | |
 |  |  fix         |  |  /fix        |  |  on Deployments,          | |
 |  |  list        |  |  /policies   |  |  KafkaTopics, etc.        | |
 |  +------+-------+  +------+------+  +-------------+-------------+ |
 |         |                 |                        |               |
 |  +------v-----------------v------------------------v-------------+ |
 |  |                  OPA Engine (Rego)                             | |
 |  |  policies/kubernetes/deployment.rego                           | |
 |  |  policies/kafka/topic.rego                                     | |
 |  |  policies/terraform/security.rego                              | |
 |  |  policies/cicd/pipeline.rego                                   | |
 |  |  policies/gitops/argocd.rego                                   | |
 |  +---------------------------+-----------------------------------+ |
 |                              |                                     |
 |  +---------------------------v-----------------------------------+ |
 |  |              Claude AI Client                                  | |
 |  |  GenerateConfig() - produce compliant YAML from requirements   | |
 |  |  FixViolations()  - auto-remediate policy violations           | |
 |  +----------------------------------------------------------------+ |
 +---------------------------------------------------------------------+
```

---

## AI Multi-Agent Architecture

```
  User: "Create a new microservice called order-api with a Kafka topic"
                                    |
                                    v
                         +---------------------+
                         |  Supervisor Agent    |
                         |  (LangGraph)         |
                         |                      |
                         |  System prompt with   |
                         |  agent descriptions   |
                         |  -> LLM classifies    |
                         |     intent            |
                         +---------+-----------+
                                   |
                    +--------------+--------------+
                    |              |              |
              +-----v-----+ +----v-----+ +-----v-----+
              |  Policy    | |  GitHub   | |  Kafka     |
              |  Agent     | |  Agent    | |  Agent     |
              |            | |           | |            |
              | validate   | | create    | | create     |
              | generated  | | repository| | topic via  |
              | configs    | | from      | | Strimzi    |
              | against    | | golden    | | KafkaTopic |
              | Rego       | | path      | | CRD        |
              | policies   | | template  | |            |
              +-----+------+ +----+-----+ +-----+-----+
                    |              |              |
                    +--------------+--------------+
                                   |
                         +---------v-----------+
                         |  ArgoCD Agent        |
                         |  Create Application  |
                         |  for GitOps deploy   |
                         +---------+-----------+
                                   |
                         +---------v-----------+
                         |  Backstage Agent     |
                         |  Register in catalog |
                         +---------+-----------+
                                   |
                         +---------v-----------+
                         |  Slack Agent         |
                         |  Notify #platform    |
                         +---------+-----------+
                                   |
                         +---------v-----------+
                         |  Supervisor          |
                         |  Synthesize final    |
                         |  response + SSE      |
                         |  stream to UI        |
                         +---------------------+


  Agent Inventory:
  +-------------+--------------------------------------+--------------+
  | Agent       | Tools                                | Integrates   |
  |-------------+--------------------------------------+--------------|
  | github      | create_repo, create_pr, list_repos   | GitHub API   |
  |             | create_issue, search_code            |              |
  | argocd      | sync_app, get_status, list_apps      | ArgoCD API   |
  |             | rollback, get_history                |              |
  | flux        | reconcile, suspend, resume           | kubectl      |
  |             | list_kustomizations, get_source      |              |
  | jira        | create_issue, search, update         | Jira REST v3 |
  |             | get_sprint, add_comment              |              |
  | slack       | send_message, create_channel         | Slack API    |
  |             | post_incident_update                 |              |
  | pagerduty   | list_incidents, acknowledge          | PagerDuty v2 |
  |             | resolve, get_oncall, trigger          |              |
  | backstage   | list_entities, get_entity            | Backstage API|
  |             | trigger_template, search              |              |
  | kafka       | create_topic, list_topics            | Strimzi CRDs |
  |             | describe, update_config, delete       | via kubectl  |
  | vault       | read_secret, write_secret            | Vault HTTP   |
  |             | list, create_policy, enable_engine    |              |
  | rancher     | list_clusters, get_status            | Rancher v3   |
  |             | scale_nodepool, get_events            |              |
  | policy      | validate_config, generate_config     | Go Policy    |
  |             | fix_violations, list_policies         | Agent HTTP   |
  +-------------+--------------------------------------+--------------+
```

---

## GitOps Bridge Pattern

```
  PHASE 1: Terraform provisions infrastructure and passes metadata

  +------------------------------------------------------------------+
  |                    Terraform                                      |
  |                                                                   |
  |  modules/vpc ------> VPC ID, Subnet IDs                          |
  |  modules/eks ------> Cluster endpoint, OIDC provider             |
  |  modules/iam ------> IAM Role ARNs (ESO, DNS, Cert-Mgr, Vault)  |
  |  modules/vault ----> KMS key, DynamoDB table                     |
  |  modules/secrets --> SM secret ARNs                              |
  |                                                                   |
  |  All outputs assembled in locals.tf --> gitops_bridge_metadata   |
  |                                                                   |
  |  modules/gitops-bridge --> Creates K8s Secret in argocd namespace|
  +------------------------------+-----------------------------------+
                                 |
                                 v
  +------------------------------------------------------------------+
  |  K8s Secret: "cluster-metadata" (namespace: argocd)              |
  |                                                                   |
  |  labels:                                                          |
  |    argocd.argoproj.io/secret-type: cluster                       |
  |                                                                   |
  |  annotations:  (GitOps Bridge metadata)                          |
  |    cluster_name: idpportal-dev                                   |
  |    region: us-west-2                                              |
  |    environment: dev                                               |
  |    vpc_id: vpc-0abc123                                            |
  |    iam_role_arn_external_secrets: arn:aws:iam::...:role/...      |
  |    iam_role_arn_external_dns: arn:aws:iam::...:role/...          |
  |    iam_role_arn_cert_manager: arn:aws:iam::...:role/...          |
  |    vault_addr: http://vault.vault.svc:8200                       |
  |    kafka_bootstrap_servers: kafka:9092                            |
  |    gitops_repo_url: https://github.com/org/idpportal.git         |
  |    domain_name: dev.idp.example.com                              |
  +------------------------------+-----------------------------------+
                                 |
  PHASE 2: ArgoCD ApplicationSet reads annotations as Helm values
                                 |
                                 v
  +------------------------------------------------------------------+
  |  ApplicationSet (packages/addons/templates/applicationset.yaml)  |
  |                                                                   |
  |  generators:                                                      |
  |    - clusters:                                                    |
  |        selector:                                                  |
  |          matchLabels:                                             |
  |            argocd.argoproj.io/secret-type: cluster               |
  |                                                                   |
  |  For each addon (14 total):                                      |
  |    template:                                                      |
  |      source:                                                      |
  |        path: packages/<addon-name>                               |
  |        helm:                                                      |
  |          parameters:                                              |
  |            - cluster.name = {{ annotations.cluster_name }}       |
  |            - cluster.region = {{ annotations.region }}            |
  |            - serviceAccount.role = {{ annotations.iam_role }}    |
  |      destination:                                                 |
  |        namespace: <addon-namespace>                              |
  |      syncPolicy:                                                  |
  |        automated: { prune: true, selfHeal: true }                |
  +------------------------------+-----------------------------------+
                                 |
                                 v
  +------------------------------------------------------------------+
  |  ArgoCD generates an Application per addon:                      |
  |                                                                   |
  |  argo-cd          --> argocd namespace                            |
  |  flux-system      --> flux-system namespace                      |
  |  backstage        --> backstage namespace                        |
  |  keycloak         --> keycloak namespace                         |
  |  vault            --> vault namespace                             |
  |  kafka            --> kafka namespace                             |
  |  rancher          --> cattle-system namespace                    |
  |  cert-manager     --> cert-manager namespace                     |
  |  external-dns     --> external-dns namespace                     |
  |  external-secrets --> external-secrets namespace                 |
  |  ingress-nginx    --> ingress-nginx namespace                    |
  |  opa-gatekeeper   --> gatekeeper-system namespace                |
  |  policy-agent     --> policy-agent namespace                     |
  |  ai-platform      --> idpportal namespace                        |
  +------------------------------------------------------------------+
```

---

## Policy-as-Code Architecture

```
  Policy Agent integrates in 4 modes:

  +-------------------------------------------------------------------+
  |                                                                    |
  |  MODE 1: K8s Admission Webhook                                    |
  |  +----------+    +-----------------+    +------------------------+ |
  |  | kubectl   |    | K8s API Server  |    | Policy Agent Webhook   | |
  |  | apply     |--->| ValidatingWH    |--->| POST /webhook/validate | |
  |  | deploy.yml|    | Configuration   |    | OPA evaluates Rego     | |
  |  +----------+    +-----------------+    | Returns allow/deny     | |
  |                                          +------------------------+ |
  |                                                                    |
  |  MODE 2: AI Chat Agent                                            |
  |  +----------+    +-----------------+    +------------------------+ |
  |  | Developer |    | Supervisor      |    | Policy Sub-Agent       | |
  |  | "validate |--->| routes to       |--->| calls Go agent HTTP    | |
  |  |  my yaml" |    | policy agent    |    | returns violations     | |
  |  +----------+    +-----------------+    +------------------------+ |
  |                                                                    |
  |  MODE 3: CI/CD Gate                                               |
  |  +----------+    +-----------------+    +------------------------+ |
  |  | GitHub PR |    | policy-gate.yml |    | policy-agent CLI       | |
  |  | with K8s  |--->| GitHub Action   |--->| validate --domain k8s  | |
  |  | configs   |    | on PR trigger   |    | --file deploy.yaml     | |
  |  +----------+    +-----------------+    | exit 1 on violations   | |
  |                                          +------------------------+ |
  |                                                                    |
  |  MODE 4: Self-Service Templates                                   |
  |  +----------+    +-----------------+    +------------------------+ |
  |  | Backstage |    | Scaffolder      |    | Policy Agent HTTP      | |
  |  | Template  |--->| validates       |--->| POST /validate         | |
  |  | Wizard    |    | before commit   |    | blocks non-compliant   | |
  |  +----------+    +-----------------+    +------------------------+ |
  |                                                                    |
  +-------------------------------------------------------------------+

  Policy Domains:
  +-------------+----------------------------------------------------+
  | Domain      | Example Rules                                      |
  |-------------+----------------------------------------------------|
  | kubernetes  | require security context, resource limits,         |
  |             | no privileged, no root, no :latest tag, probes     |
  | kafka       | min 3 partitions, min 3 replicas, max retention,  |
  |             | naming convention, require retention with delete   |
  | terraform   | S3 encryption, no public S3/RDS, no open ingress, |
  |             | RDS encryption+backups, EKS secrets encryption     |
  | cicd        | no pipe-to-bash, pin action versions,             |
  |             | restrict PR triggers, no secret logging, timeouts  |
  | gitops      | require self-heal, no HEAD revision, pin chart    |
  |             | versions, require namespace, health checks         |
  +-------------+----------------------------------------------------+
```

---

## Identity and Auth Architecture

```
  +------------------------------------------------------------------+
  |                   Identity Flow                                   |
  |                                                                   |
  |  Developer                                                        |
  |     |                                                             |
  |     |  1. Login request                                          |
  |     v                                                             |
  |  +--------------------------+                                    |
  |  |  Portal UI (Next.js)     |                                    |
  |  |  next-auth v5            |                                    |
  |  |  Keycloak OIDC Provider  |                                    |
  |  +------------+-------------+                                    |
  |               |  2. Redirect to Keycloak                         |
  |               v                                                   |
  |  +----------------------------------------------------+         |
  |  |              Keycloak (Front Door)                   |         |
  |  |                                                      |         |
  |  |  Realm: idpportal                                    |         |
  |  |  Clients: idpportal-ui, backstage, argocd, vault    |         |
  |  |  Roles: platform-admin, developer, viewer            |         |
  |  |  Groups: platform-admins, developers, viewers        |         |
  |  |                                                      |         |
  |  |  +----------------------------------------------+   |         |
  |  |  |  Identity Broker (optional)                   |   |         |
  |  |  |                                               |   |         |
  |  |  |  +---------------+  +-----------------+      |   |         |
  |  |  |  | Okta Broker    |  | ForgeRock       |      |   |         |
  |  |  |  | OIDC           |  | Broker OIDC     |      |   |         |
  |  |  |  |                |  |                 |      |   |         |
  |  |  |  | Enterprise SSO |  | Enterprise SSO  |      |   |         |
  |  |  |  +---------------+  +-----------------+      |   |         |
  |  |  +----------------------------------------------+   |         |
  |  +------------+---------------------------------------+         |
  |               |  3. JWT (access_token + roles)                   |
  |               v                                                   |
  |  +--------------------------+                                    |
  |  |  FastAPI Backend          |                                    |
  |  |  JWT verification         |                                    |
  |  |  Keycloak public key      |                                    |
  |  |  Role -> Permission map   |                                    |
  |  |                            |                                    |
  |  |  platform-admin -> all     |                                    |
  |  |  developer -> read + exec  |                                    |
  |  |  viewer -> read only       |                                    |
  |  +--------------------------+                                    |
  |                                                                   |
  |  SSO across all platform services:                               |
  |  Portal UI, Backstage, ArgoCD, Vault, Rancher                    |
  |  (all share the same Keycloak realm)                             |
  +------------------------------------------------------------------+
```

---

## Self-Service Flow

```
  Developer: "I need a new microservice with a Kafka topic"
      |
      v
  +-------------------------------------------------------------+
  |  Self-Service Hub (/self-service)                           |
  |                                                              |
  |  +------------+ +------------+ +------------+ +----------+ |
  |  |Microservice| |Kafka Topic | | Database   | |S3 Bucket | |
  |  | Template   | | Template   | | Template   | | Template | |
  |  +------+-----+ +------------+ +------------+ +----------+ |
  +---------|---------------------------------------------------+
            |  Select template, fill parameters
            v
  +-------------------------------------------------------------+
  |  Step 1: VALIDATE                                           |
  |  Policy Agent validates generated configs against Rego      |
  |  -> kubernetes/deployment.rego                              |
  |  -> kafka/topic.rego                                        |
  |  Result: PASS / FAIL with violations                        |
  +-----------------------------+-------------------------------+
                                | PASS
                                v
  +-------------------------------------------------------------+
  |  Step 2: CREATE REPOSITORY                                  |
  |  GitHub Agent creates repo from golden path template        |
  |  -> Dockerfile, CI pipeline, Helm chart, catalog-info.yaml |
  +-----------------------------+-------------------------------+
                                v
  +-------------------------------------------------------------+
  |  Step 3: PROVISION RESOURCES                                |
  |  Kafka Agent creates KafkaTopic CR via Strimzi              |
  |  Vault Agent stores credentials                             |
  +-----------------------------+-------------------------------+
                                v
  +-------------------------------------------------------------+
  |  Step 4: DEPLOY via GitOps                                  |
  |  ArgoCD Agent creates Application (or Flux Kustomization)  |
  |  -> Automated sync + self-heal enabled                      |
  +-----------------------------+-------------------------------+
                                v
  +-------------------------------------------------------------+
  |  Step 5: REGISTER                                           |
  |  Backstage Agent registers service in catalog               |
  +-----------------------------+-------------------------------+
                                v
  +-------------------------------------------------------------+
  |  Step 6: NOTIFY                                             |
  |  Slack Agent posts to #platform-updates                     |
  |  Jira Agent creates tracking ticket                         |
  +-------------------------------------------------------------+
```

---

## Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Cloud** | AWS (EKS, VPC, IAM, KMS, SM, Route53) | Infrastructure platform |
| **IaC** | Terraform + terraform-aws-modules | Infrastructure provisioning |
| **Container Orchestration** | Kubernetes (EKS 1.31) | Workload runtime |
| **GitOps** | Argo CD + Flux CD | Continuous deployment (teams choose) |
| **Developer Portal** | Backstage | Service catalog + scaffolder templates |
| **Identity** | Keycloak 26 + Okta/ForgeRock brokers | SSO across all services |
| **Secrets** | HashiCorp Vault + AWS Secrets Manager | App secrets + bootstrap secrets |
| **Streaming** | Apache Kafka (Strimzi operator) | Event streaming + topic self-service |
| **Multi-cluster** | Rancher | Kubernetes fleet management |
| **Policy** | OPA/Rego + custom Go Policy Agent | Policy-as-code validation |
| **AI Backend** | Python 3.12, FastAPI, LangGraph | Multi-agent orchestration |
| **AI Models** | Claude (Anthropic) / GPT (OpenAI) | LLM for agent reasoning |
| **AI Protocols** | MCP + A2A | Tool registry + agent communication |
| **Portal UI** | Next.js 15, React 19, Tailwind, shadcn/ui | Developer-facing SPA |
| **State** | Zustand | Client-side state management |
| **Auth (UI)** | next-auth v5 | Keycloak OIDC integration |
| **Database** | PostgreSQL 16 + pgvector | Data + RAG embeddings |
| **Cache** | Redis 7 | Sessions + caching |
| **DNS** | External DNS | Automatic Route53 records |
| **TLS** | cert-manager + Let's Encrypt | Automated TLS certificates |
| **Ingress** | NGINX Ingress Controller | HTTP routing + NLB |
| **Admission** | OPA Gatekeeper + Policy Agent webhook | Runtime policy enforcement |
| **CI/CD** | GitHub Actions (7 workflows) | Build, test, deploy, policy gate |

---

## Project Structure

```
idpportal/
├── config.yaml                          # Central environment configuration
├── Makefile                             # Top-level build/dev commands
├── docker-compose.yaml                  # Local dev (8 services)
├── docker-compose.dev.yaml              # Hot-reload overrides
├── .env.example                         # All environment variables
│
├── infrastructure/                      # Terraform (AWS)
│   ├── main.tf                          # Module composition
│   ├── locals.tf                        # GitOps Bridge metadata assembly
│   ├── variables.tf / outputs.tf
│   ├── providers.tf / versions.tf / backend.tf
│   ├── modules/
│   │   ├── vpc/                         # VPC + subnets (3 AZ)
│   │   ├── eks/                         # EKS 1.31 + managed node groups
│   │   ├── iam/                         # Pod Identity roles (ESO, DNS, Cert)
│   │   ├── secrets/                     # AWS Secrets Manager (bootstrap)
│   │   ├── vault/                       # KMS auto-unseal + DynamoDB backend
│   │   ├── kafka/                       # Kafka namespace prep
│   │   └── gitops-bridge/               # K8s Secret with TF metadata
│   └── envs/
│       ├── dev.tfvars
│       ├── staging.tfvars
│       └── prod.tfvars
│
├── packages/                            # Helm charts (14 addons via ArgoCD)
│   ├── addons/                          # Root ApplicationSet (App of Apps)
│   ├── argo-cd/                         # ArgoCD + Keycloak OIDC SSO
│   ├── flux-system/                     # Flux controllers + GitRepository
│   ├── backstage/                       # Backstage + GitHub App + Keycloak
│   ├── keycloak/                        # Keycloak + IdP broker overlays
│   │   └── overlays/
│   │       ├── okta-broker.yaml
│   │       └── forgerock-broker.yaml
│   ├── vault/                           # Vault HA + Secrets Operator
│   ├── kafka/                           # Strimzi operator + Kafka cluster
│   ├── rancher/                         # Rancher server
│   ├── cert-manager/                    # TLS + ClusterIssuer
│   ├── external-dns/                    # Route53 DNS automation
│   ├── external-secrets/                # AWS SM -> K8s Secrets
│   ├── ingress-nginx/                   # NLB ingress
│   ├── opa-gatekeeper/                  # Policy enforcement + templates
│   ├── policy-agent/                    # Go webhook + ValidatingWH config
│   └── ai-platform/                     # Backend + UI deployment + Ingress
│
├── policies/                            # OPA/Rego policies (5 domains)
│   ├── kubernetes/deployment.rego
│   ├── kafka/topic.rego
│   ├── terraform/security.rego
│   ├── cicd/pipeline.rego
│   └── gitops/argocd.rego
│
├── backend/                             # Python FastAPI (AI backend)
│   ├── app/
│   │   ├── main.py                      # Entry point + lifespan
│   │   ├── config.py                    # Pydantic settings
│   │   ├── api/v1/                      # REST endpoints
│   │   │   ├── chat.py                  # Chat (sync + SSE streaming)
│   │   │   ├── agents.py               # Agent management
│   │   │   ├── selfservice.py          # Self-service provisioning
│   │   │   └── health.py               # Health/readiness
│   │   ├── agents/                      # 12 AI agents
│   │   │   ├── base.py                  # BaseAgent ABC + AgentCard
│   │   │   ├── registry.py             # Agent discovery
│   │   │   ├── supervisor.py           # LangGraph orchestrator
│   │   │   ├── github/                  # GitHub (repos, PRs, issues)
│   │   │   ├── argocd/                 # ArgoCD (sync, rollback)
│   │   │   ├── flux/                   # Flux (reconcile, suspend)
│   │   │   ├── jira/                   # Jira (issues, sprints)
│   │   │   ├── slack/                  # Slack (messages, channels)
│   │   │   ├── pagerduty/             # PagerDuty (incidents)
│   │   │   ├── backstage/             # Backstage (catalog)
│   │   │   ├── kafka/                  # Kafka (topics via Strimzi)
│   │   │   ├── vault/                  # Vault (secrets CRUD)
│   │   │   ├── rancher/               # Rancher (clusters)
│   │   │   └── policy/                # Policy (validate/generate/fix)
│   │   └── services/
│   │       ├── llm.py                   # Claude / OpenAI factory
│   │       ├── auth.py                  # Keycloak JWT verification
│   │       └── database.py             # Async PostgreSQL + pgvector
│   ├── pyproject.toml
│   └── Dockerfile
│
├── policy-agent/                        # Go Policy Agent
│   ├── cmd/
│   │   ├── policy-agent/main.go         # CLI (validate, generate, fix)
│   │   └── webhook/main.go              # HTTP server + K8s webhook
│   ├── internal/
│   │   ├── policy/engine.go             # OPA engine (load + eval Rego)
│   │   ├── validator/validator.go       # Domain validation
│   │   ├── ai/claude.go                 # Claude API (gen + remediate)
│   │   └── webhook/handler.go           # Admission + HTTP handlers
│   ├── go.mod
│   └── Dockerfile
│
├── ui/                                  # Next.js 15 Portal UI
│   ├── src/
│   │   ├── app/                         # 12 pages (App Router)
│   │   │   ├── page.tsx                 # Dashboard
│   │   │   ├── chat/                    # AI chat interface
│   │   │   ├── catalog/                 # Service catalog
│   │   │   ├── deployments/             # ArgoCD + Flux view
│   │   │   ├── incidents/               # PagerDuty incidents
│   │   │   ├── kafka/                   # Kafka topics
│   │   │   ├── policies/                # Compliance dashboard
│   │   │   ├── secrets/                 # Vault browser
│   │   │   ├── self-service/            # Template wizard
│   │   │   ├── clusters/                # Rancher clusters
│   │   │   ├── knowledge/               # RAG search
│   │   │   └── settings/                # User prefs
│   │   ├── components/
│   │   │   ├── chat/                    # ChatWindow, MessageBubble, etc.
│   │   │   └── layout/                  # Sidebar, Header
│   │   ├── stores/chat.ts               # Zustand (SSE streaming)
│   │   └── lib/                         # API client, auth, utils
│   ├── package.json
│   └── Dockerfile
│
├── templates/                           # Backstage scaffolder templates
│   ├── microservice/template.yaml       # Golden path microservice
│   ├── kafka-topic/template.yaml        # Self-service Kafka topic
│   └── database/template.yaml           # Provision managed database
│
├── scripts/
│   └── bootstrap.sh                     # 2-stage EKS bootstrap
│
└── .github/workflows/                   # CI/CD (7 pipelines)
    ├── ci-backend.yaml                  # Ruff lint + pytest
    ├── ci-ui.yaml                       # ESLint + Next.js build
    ├── ci-policy-agent.yaml             # Go vet + test + build
    ├── policy-gate.yaml                 # Validate configs on PR
    ├── terraform-plan.yaml              # Plan on PR + comment
    ├── terraform-apply.yaml             # Apply on merge to main
    └── release.yaml                     # Docker build + ECR push
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.12+ with [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- Go 1.22+
- Terraform 1.7+ (for infrastructure)
- kubectl + AWS CLI (for EKS deployment)

### Local Development

```bash
# 1. Clone and configure
cp .env.example .env
# Edit .env with your API keys (at minimum: ANTHROPIC_API_KEY)

# 2. Start all services (8 containers)
docker compose up -d

# 3. Access the portal
#   UI:        http://localhost:3000
#   Backend:   http://localhost:8000/docs  (Swagger)
#   Keycloak:  http://localhost:8080       (admin/admin)
#   Vault:     http://localhost:8200       (token: dev-root-token)
```

### Development with Hot Reload

```bash
# Start with hot-reload on backend + UI
docker compose -f docker-compose.yaml -f docker-compose.dev.yaml up

# Or run backend/UI natively:
cd backend && uv run uvicorn app.main:app --reload --port 8000
cd ui && npm run dev
```

### Policy Agent

```bash
# Validate a Kubernetes config
cd policy-agent
go run ./cmd/policy-agent validate \
  --domain kubernetes \
  --file examples/deployment.yaml \
  --policies-dir ../policies

# Start webhook server
go run ./cmd/webhook --port 8443 --policies-dir ../policies
```

---

## Deployment

### EKS Bootstrap (Production)

```bash
# 1. Provision infrastructure
cd infrastructure
terraform init -backend-config=envs/dev.tfvars
terraform plan -var-file=envs/dev.tfvars
terraform apply -var-file=envs/dev.tfvars

# 2. Configure kubectl
aws eks update-kubeconfig --name idpportal-dev --region us-west-2

# 3. Bootstrap platform
#    Installs ArgoCD + ESO, then ArgoCD manages all 14 addons
./scripts/bootstrap.sh

# 4. ArgoCD auto-syncs everything via ApplicationSet
```

### Environments

| Environment | Cluster | VPC CIDR | Nodes |
|------------|---------|----------|-------|
| dev | idpportal-dev | 10.0.0.0/16 | 3x m6i.xlarge |
| staging | idpportal-staging | 10.1.0.0/16 | 3x m6i.xlarge |
| prod | idpportal-prod | 10.2.0.0/16 | 5x m6i.2xlarge |

---

## CI/CD Pipelines

| Workflow | Trigger | What it does |
|----------|---------|-------------|
| `ci-backend` | Push/PR to `backend/**` | Ruff lint + pytest with Postgres/Redis |
| `ci-ui` | Push/PR to `ui/**` | ESLint + Next.js build |
| `ci-policy-agent` | Push/PR to `policy-agent/**` | go vet + go test + build |
| `policy-gate` | PR with `*.yaml`/`*.tf` | Validates configs against Rego policies |
| `terraform-plan` | PR to `infrastructure/**` | Terraform plan + PR comment |
| `terraform-apply` | Merge to main `infrastructure/**` | Terraform apply |
| `release` | Git tag `v*` | Docker build, ECR push, Helm values update |

---

## Self-Service Capabilities

Developers can self-serve through the portal UI or AI chat:

| Template | What it provisions |
|----------|--------------------|
| **Microservice** | GitHub repo + CI pipeline + ArgoCD/Flux deploy + catalog registration |
| **Kafka Topic** | Strimzi KafkaTopic CR with policy validation |
| **Database** | RDS instance + credentials in Vault |
| **API Service** | REST API with OpenAPI spec + API gateway config |
| **S3 Bucket** | Encrypted S3 bucket with IAM policy |
| **Worker Service** | Background job processor with SQS/Kafka consumer |

All provisioning is policy-gated: configs are validated against OPA/Rego policies before any resources are created.

---

## References

- [CNOE - Cloud Native Operational Excellence](https://cnoe.io/)
- [CNOE AWS Reference Implementation](https://github.com/cnoe-io/reference-implementation-aws) - GitOps Bridge pattern, App-of-Apps, bootstrap strategy
- [CAIPE - AI Platform Engineering](https://github.com/cnoe-io/ai-platform-engineering) - Multi-agent AI architecture concepts
- [GitOps Bridge](https://github.com/gitops-bridge-dev/gitops-bridge) - Terraform-to-ArgoCD metadata bridge
- [terraform-aws-modules](https://github.com/terraform-aws-modules) - VPC, EKS, IAM Terraform modules
- [Backstage](https://backstage.io/) - Developer portal and software catalog
- [Strimzi](https://strimzi.io/) - Kubernetes-native Kafka operator
- [OPA / Rego](https://www.openpolicyagent.org/) - Policy-as-code framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Multi-agent orchestration framework
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) - AI tool registry standard

---

## License

This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
