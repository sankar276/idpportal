from app.agents.base import AgentCard, BaseAgent
from app.agents.kubernetes.tools import (
    get_events,
    get_logs,
    get_pod_status,
    list_namespaces,
    list_pods,
    list_services,
    scale_deployment,
)


class KubernetesAgent(BaseAgent):
    def get_card(self) -> AgentCard:
        return AgentCard(
            name="kubernetes",
            description="Manage Kubernetes clusters directly - list pods, services, namespaces, get logs, scale deployments, view events",
            icon="kubernetes",
            category="infrastructure",
        )

    def get_tools(self) -> list:
        return [list_pods, get_pod_status, list_services, list_namespaces, get_logs, scale_deployment, get_events]
