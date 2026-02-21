package policy

import (
	"context"
	"fmt"
	"os"
	"path/filepath"
	"strings"

	"github.com/open-policy-agent/opa/v1/ast"
	"github.com/open-policy-agent/opa/v1/rego"
	"gopkg.in/yaml.v3"
)

type PolicyInfo struct {
	Name        string `json:"name"`
	Domain      string `json:"domain"`
	Description string `json:"description"`
	Path        string `json:"path"`
	Content     string `json:"content,omitempty"`
}

type Violation struct {
	Rule     string `json:"rule"`
	Message  string `json:"message"`
	Severity string `json:"severity"`
	Domain   string `json:"domain"`
}

type ValidationResult struct {
	Valid      bool        `json:"valid"`
	Violations []Violation `json:"violations"`
}

type Engine struct {
	policiesDir string
	modules     map[string]*ast.Module
}

func NewEngine(policiesDir string) (*Engine, error) {
	e := &Engine{
		policiesDir: policiesDir,
		modules:     make(map[string]*ast.Module),
	}

	if err := e.loadPolicies(); err != nil {
		return nil, fmt.Errorf("failed to load policies: %w", err)
	}

	return e, nil
}

func (e *Engine) loadPolicies() error {
	return filepath.Walk(e.policiesDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() || !strings.HasSuffix(path, ".rego") {
			return nil
		}

		data, err := os.ReadFile(path)
		if err != nil {
			return fmt.Errorf("failed to read %s: %w", path, err)
		}

		module, err := ast.ParseModule(path, string(data))
		if err != nil {
			return fmt.Errorf("failed to parse %s: %w", path, err)
		}

		e.modules[path] = module
		return nil
	})
}

func (e *Engine) Evaluate(ctx context.Context, domain string, configYAML string) (*ValidationResult, error) {
	var input interface{}
	if err := yaml.Unmarshal([]byte(configYAML), &input); err != nil {
		return nil, fmt.Errorf("invalid YAML: %w", err)
	}

	input = convertMapKeys(input)

	domainDir := filepath.Join(e.policiesDir, domain)
	if _, err := os.Stat(domainDir); os.IsNotExist(err) {
		return &ValidationResult{Valid: true}, nil
	}

	var violations []Violation

	err := filepath.Walk(domainDir, func(path string, info os.FileInfo, err error) error {
		if err != nil || info.IsDir() || !strings.HasSuffix(path, ".rego") {
			return err
		}

		data, readErr := os.ReadFile(path)
		if readErr != nil {
			return readErr
		}

		r := rego.New(
			rego.Query("data.policy.violations"),
			rego.Module(path, string(data)),
			rego.Input(input),
		)

		rs, evalErr := r.Eval(ctx)
		if evalErr != nil {
			return nil // skip policies that fail to evaluate
		}

		for _, result := range rs {
			for _, expr := range result.Expressions {
				if arr, ok := expr.Value.([]interface{}); ok {
					for _, v := range arr {
						if m, ok := v.(map[string]interface{}); ok {
							violations = append(violations, Violation{
								Rule:     getString(m, "rule"),
								Message:  getString(m, "message"),
								Severity: getString(m, "severity"),
								Domain:   domain,
							})
						}
					}
				}
			}
		}
		return nil
	})

	if err != nil {
		return nil, err
	}

	return &ValidationResult{
		Valid:      len(violations) == 0,
		Violations: violations,
	}, nil
}

func (e *Engine) ListPolicies(domain string) ([]PolicyInfo, error) {
	var policies []PolicyInfo
	searchDir := e.policiesDir
	if domain != "" {
		searchDir = filepath.Join(e.policiesDir, domain)
	}

	filepath.Walk(searchDir, func(path string, info os.FileInfo, err error) error {
		if err != nil || info.IsDir() || !strings.HasSuffix(path, ".rego") {
			return err
		}

		data, _ := os.ReadFile(path)
		relPath, _ := filepath.Rel(e.policiesDir, path)
		parts := strings.SplitN(relPath, string(os.PathSeparator), 2)
		d := ""
		if len(parts) > 1 {
			d = parts[0]
		}

		desc := extractDescription(string(data))
		name := strings.TrimSuffix(filepath.Base(path), ".rego")

		policies = append(policies, PolicyInfo{
			Name:        name,
			Domain:      d,
			Description: desc,
			Path:        relPath,
			Content:     string(data),
		})
		return nil
	})

	return policies, nil
}

func extractDescription(content string) string {
	for _, line := range strings.Split(content, "\n") {
		trimmed := strings.TrimSpace(line)
		if strings.HasPrefix(trimmed, "# ") {
			return strings.TrimPrefix(trimmed, "# ")
		}
	}
	return ""
}

func getString(m map[string]interface{}, key string) string {
	if v, ok := m[key]; ok {
		return fmt.Sprintf("%v", v)
	}
	return ""
}

func convertMapKeys(v interface{}) interface{} {
	switch val := v.(type) {
	case map[interface{}]interface{}:
		m := make(map[string]interface{})
		for k, v2 := range val {
			m[fmt.Sprintf("%v", k)] = convertMapKeys(v2)
		}
		return m
	case []interface{}:
		for i, v2 := range val {
			val[i] = convertMapKeys(v2)
		}
	}
	return v
}
