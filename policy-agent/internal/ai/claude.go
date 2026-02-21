package ai

import (
	"bytes"
	"context"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/sankar276/policy-agent/internal/policy"
)

const anthropicAPIURL = "https://api.anthropic.com/v1/messages"

type ClaudeClient struct {
	apiKey     string
	httpClient *http.Client
	model      string
}

type message struct {
	Role    string `json:"role"`
	Content string `json:"content"`
}

type request struct {
	Model     string    `json:"model"`
	MaxTokens int       `json:"max_tokens"`
	Messages  []message `json:"messages"`
	System    string    `json:"system,omitempty"`
}

type contentBlock struct {
	Type string `json:"type"`
	Text string `json:"text"`
}

type response struct {
	Content []contentBlock `json:"content"`
}

func NewClaudeClient(apiKey string) *ClaudeClient {
	return &ClaudeClient{
		apiKey:     apiKey,
		httpClient: &http.Client{},
		model:      "claude-sonnet-4-20250514",
	}
}

func (c *ClaudeClient) GenerateConfig(ctx context.Context, domain string, requirements string, policies []policy.PolicyInfo) (string, error) {
	var policyRules []string
	for _, p := range policies {
		policyRules = append(policyRules, fmt.Sprintf("Policy: %s\nDomain: %s\nDescription: %s\nContent:\n%s", p.Name, p.Domain, p.Description, p.Content))
	}

	systemPrompt := fmt.Sprintf(`You are an infrastructure configuration generator. Generate valid, policy-compliant %s configurations.
You must ensure all generated configs comply with these OPA/Rego policies:

%s

Output ONLY the YAML configuration, no explanations.`, domain, strings.Join(policyRules, "\n---\n"))

	return c.chat(ctx, systemPrompt, fmt.Sprintf("Generate a %s configuration for: %s", domain, requirements))
}

func (c *ClaudeClient) FixViolations(ctx context.Context, domain string, configYAML string, violations []string) (string, error) {
	systemPrompt := fmt.Sprintf(`You are an infrastructure configuration remediation expert for %s.
Fix policy violations while preserving the original intent. Output ONLY the corrected YAML.`, domain)

	userMsg := fmt.Sprintf("Fix the following violations in this configuration:\n\nViolations:\n%s\n\nConfiguration:\n%s",
		strings.Join(violations, "\n"), configYAML)

	return c.chat(ctx, systemPrompt, userMsg)
}

func (c *ClaudeClient) chat(ctx context.Context, systemPrompt, userMessage string) (string, error) {
	reqBody := request{
		Model:     c.model,
		MaxTokens: 4096,
		System:    systemPrompt,
		Messages: []message{
			{Role: "user", Content: userMessage},
		},
	}

	body, err := json.Marshal(reqBody)
	if err != nil {
		return "", fmt.Errorf("failed to marshal request: %w", err)
	}

	req, err := http.NewRequestWithContext(ctx, http.MethodPost, anthropicAPIURL, bytes.NewReader(body))
	if err != nil {
		return "", fmt.Errorf("failed to create request: %w", err)
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("x-api-key", c.apiKey)
	req.Header.Set("anthropic-version", "2023-06-01")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return "", fmt.Errorf("API request failed: %w", err)
	}
	defer resp.Body.Close()

	respBody, err := io.ReadAll(resp.Body)
	if err != nil {
		return "", fmt.Errorf("failed to read response: %w", err)
	}

	if resp.StatusCode != http.StatusOK {
		return "", fmt.Errorf("API error (status %d): %s", resp.StatusCode, string(respBody))
	}

	var apiResp response
	if err := json.Unmarshal(respBody, &apiResp); err != nil {
		return "", fmt.Errorf("failed to parse response: %w", err)
	}

	if len(apiResp.Content) == 0 {
		return "", fmt.Errorf("empty response from API")
	}

	return apiResp.Content[0].Text, nil
}
