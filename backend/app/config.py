import logging
import sys

from pydantic import field_validator
from pydantic_settings import BaseSettings

logger = logging.getLogger(__name__)


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "IDP Portal AI Backend"
    debug: bool = False  # Must be explicitly set to True via env var

    # CORS - configurable origins for production
    cors_allowed_origins: str = "http://localhost:3000,http://localhost:3001"

    # Database (no default credentials - must be provided via env)
    database_url: str = ""

    # Redis
    redis_url: str = ""

    # Keycloak Auth
    keycloak_url: str = ""
    keycloak_realm: str = "idpportal"
    keycloak_client_id: str = ""
    keycloak_client_secret: str = ""

    # LLM
    llm_provider: str = "anthropic"  # anthropic | openai
    anthropic_api_key: str = ""
    openai_api_key: str = ""
    llm_model: str = "claude-sonnet-4-20250514"

    # GitHub
    github_app_id: str = ""
    github_app_private_key: str = ""
    github_token: str = ""

    # Jira
    jira_base_url: str = ""
    jira_api_token: str = ""
    jira_user_email: str = ""

    # PagerDuty
    pagerduty_api_key: str = ""
    pagerduty_service_id: str = ""

    # Slack
    slack_bot_token: str = ""
    slack_signing_secret: str = ""
    slack_default_channel: str = ""

    # Argo CD
    argocd_server_url: str = ""
    argocd_auth_token: str = ""
    argocd_verify_tls: bool = True  # Disable only for dev with self-signed certs

    # Flux CD
    flux_github_token: str = ""

    # Vault
    vault_addr: str = ""
    vault_token: str = ""

    # Kafka
    kafka_bootstrap_servers: str = ""
    kafka_sasl_username: str = ""
    kafka_sasl_password: str = ""
    schema_registry_url: str = ""

    # Rancher
    rancher_server_url: str = ""
    rancher_api_token: str = ""
    rancher_verify_tls: bool = True  # Disable only for dev with self-signed certs

    # Policy Agent
    policy_agent_url: str = "http://localhost:8443"

    # Backstage
    backstage_url: str = "http://localhost:7007"

    # HTTP client settings
    http_timeout: int = 30  # seconds

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        if not v:
            logger.warning("DATABASE_URL not set - database features will be unavailable")
        return v

    def validate_startup(self) -> list[str]:
        """Validate critical settings on startup. Returns list of warnings."""
        warnings = []
        if not self.database_url:
            warnings.append("DATABASE_URL is not configured")
        if not self.redis_url:
            warnings.append("REDIS_URL is not configured")
        if not self.keycloak_url:
            warnings.append("KEYCLOAK_URL is not configured - auth will be disabled")
        if not self.anthropic_api_key and not self.openai_api_key:
            warnings.append("No LLM API key configured - AI features will be unavailable")
        if self.app_env == "production" and self.debug:
            warnings.append("DEBUG=True in production environment - this is a security risk")
        return warnings


settings = Settings()

# Log startup warnings
_warnings = settings.validate_startup()
for w in _warnings:
    logger.warning(f"Config warning: {w}")
if settings.app_env == "production" and len(_warnings) > 0:
    logger.error("Production startup has configuration warnings - review before proceeding")

