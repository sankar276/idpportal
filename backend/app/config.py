from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_env: str = "development"
    app_name: str = "IDP Portal AI Backend"
    debug: bool = True

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/idpportal"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # Keycloak Auth
    keycloak_url: str = "http://localhost:8080"
    keycloak_realm: str = "idpportal"
    keycloak_client_id: str = "idpportal"
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

    # Flux CD
    flux_github_token: str = ""

    # Vault
    vault_addr: str = "http://localhost:8200"
    vault_token: str = ""

    # Kafka
    kafka_bootstrap_servers: str = "localhost:9092"
    kafka_sasl_username: str = ""
    kafka_sasl_password: str = ""
    schema_registry_url: str = ""

    # Rancher
    rancher_server_url: str = ""
    rancher_api_token: str = ""

    # Policy Agent
    policy_agent_url: str = "http://localhost:8443"

    # Backstage
    backstage_url: str = "http://localhost:7007"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
