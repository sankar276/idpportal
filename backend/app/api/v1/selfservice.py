from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/self-service", tags=["self-service"])


class TemplateInfo(BaseModel):
    name: str
    description: str
    category: str
    parameters: list[dict]


class ProvisionRequest(BaseModel):
    template_name: str
    parameters: dict


class ProvisionStatus(BaseModel):
    request_id: str
    status: str  # pending | running | completed | failed
    steps: list[dict]


TEMPLATES = [
    TemplateInfo(
        name="microservice",
        description="Create a new microservice with GitHub repo, CI/CD, and ArgoCD deployment",
        category="application",
        parameters=[
            {"name": "service_name", "type": "string", "required": True},
            {"name": "language", "type": "string", "options": ["python", "go", "node"], "required": True},
            {"name": "gitops_engine", "type": "string", "options": ["argocd", "flux"], "default": "argocd"},
            {"name": "needs_kafka", "type": "boolean", "default": False},
            {"name": "needs_database", "type": "boolean", "default": False},
        ],
    ),
    TemplateInfo(
        name="kafka-topic",
        description="Create a Kafka topic with schema registry",
        category="infrastructure",
        parameters=[
            {"name": "topic_name", "type": "string", "required": True},
            {"name": "partitions", "type": "integer", "default": 3},
            {"name": "retention_ms", "type": "integer", "default": 604800000},
            {"name": "schema", "type": "string", "required": False},
        ],
    ),
    TemplateInfo(
        name="database",
        description="Provision a managed database (RDS Postgres/MySQL/Aurora)",
        category="infrastructure",
        parameters=[
            {"name": "db_name", "type": "string", "required": True},
            {"name": "engine", "type": "string", "options": ["postgres", "mysql", "aurora-postgres"], "required": True},
            {"name": "instance_class", "type": "string", "default": "db.t3.medium"},
            {"name": "storage_gb", "type": "integer", "default": 20},
        ],
    ),
    TemplateInfo(
        name="api-service",
        description="Create a REST API service with OpenAPI spec and golden path patterns",
        category="application",
        parameters=[
            {"name": "service_name", "type": "string", "required": True},
            {"name": "language", "type": "string", "options": ["python", "go", "node"], "required": True},
            {"name": "auth_required", "type": "boolean", "default": True},
        ],
    ),
    TemplateInfo(
        name="s3-bucket",
        description="Create an S3 bucket with encryption and lifecycle policies",
        category="infrastructure",
        parameters=[
            {"name": "bucket_name", "type": "string", "required": True},
            {"name": "versioning", "type": "boolean", "default": True},
            {"name": "lifecycle_days", "type": "integer", "default": 90},
        ],
    ),
    TemplateInfo(
        name="worker-service",
        description="Create a background worker service (Kafka consumer or SQS processor)",
        category="application",
        parameters=[
            {"name": "service_name", "type": "string", "required": True},
            {"name": "source", "type": "string", "options": ["kafka", "sqs"], "required": True},
            {"name": "topic_or_queue", "type": "string", "required": True},
        ],
    ),
]


@router.get("/templates")
async def list_templates():
    return {"templates": [t.model_dump() for t in TEMPLATES]}


@router.get("/templates/{template_name}")
async def get_template(template_name: str):
    for t in TEMPLATES:
        if t.name == template_name:
            return t.model_dump()
    return {"error": f"Template '{template_name}' not found"}


@router.post("/provision")
async def provision(request: ProvisionRequest):
    # TODO: Wire up self-service engine
    import uuid

    return ProvisionStatus(
        request_id=str(uuid.uuid4()),
        status="pending",
        steps=[
            {"name": "validate_policies", "status": "pending"},
            {"name": "create_repo", "status": "pending"},
            {"name": "generate_configs", "status": "pending"},
            {"name": "deploy_gitops", "status": "pending"},
            {"name": "register_catalog", "status": "pending"},
            {"name": "notify_team", "status": "pending"},
        ],
    ).model_dump()
