# OPA/Rego Policies

Policy-as-code for validating infrastructure and application configurations.

## Domains

| Domain | Description |
|--------|-------------|
| `kafka/` | Kafka topic and connector configuration policies |
| `kubernetes/` | Kubernetes deployment, pod, and service policies |
| `terraform/` | Infrastructure-as-code security policies |
| `cicd/` | CI/CD pipeline (GitHub Actions) security policies |
| `gitops/` | ArgoCD and Flux CD configuration policies |

## Policy Structure

Each `.rego` file exports a `violations` set. Each violation is an object with:

```json
{
  "rule": "rule-name",
  "message": "Human-readable description",
  "severity": "critical|high|medium|low"
}
```

## Usage

### CLI
```bash
policy-agent validate --domain kubernetes --file deployment.yaml
```

### HTTP API
```bash
curl -X POST http://localhost:8443/validate \
  -H "Content-Type: application/json" \
  -d '{"domain": "kubernetes", "config": "..."}'
```

### K8s Admission Webhook
Automatically validates resources on create/update via `ValidatingWebhookConfiguration`.
