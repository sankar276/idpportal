export interface Agent {
  name: string;
  description: string;
  capabilities: AgentCapability[];
  version: string;
  protocol: string;
}

export interface AgentCapability {
  name: string;
  description: string;
  tools: string[];
}

export interface Template {
  name: string;
  description: string;
  category: string;
  parameters: TemplateParameter[];
}

export interface TemplateParameter {
  name: string;
  type: string;
  required?: boolean;
  default?: unknown;
  options?: string[];
}

export interface ProvisioningStatus {
  request_id: string;
  status: "pending" | "running" | "completed" | "failed";
  steps: ProvisioningStep[];
}

export interface ProvisioningStep {
  name: string;
  status: string;
  message?: string;
}
