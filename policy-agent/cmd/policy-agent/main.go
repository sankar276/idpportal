package main

import (
	"fmt"
	"os"

	"github.com/sankar276/policy-agent/internal/ai"
	"github.com/sankar276/policy-agent/internal/policy"
	"github.com/sankar276/policy-agent/internal/validator"
	"github.com/spf13/cobra"
	"go.uber.org/zap"
)

var (
	policiesDir string
	domain      string
	filePath    string
	logger      *zap.Logger
)

func main() {
	logger, _ = zap.NewProduction()
	defer logger.Sync()

	rootCmd := &cobra.Command{
		Use:   "policy-agent",
		Short: "OPA/Rego policy validation agent for infrastructure and application configs",
	}

	rootCmd.PersistentFlags().StringVar(&policiesDir, "policies-dir", "./policies", "Directory containing Rego policies")

	rootCmd.AddCommand(validateCmd(), generateCmd(), fixCmd(), listCmd())

	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}

func validateCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "validate",
		Short: "Validate a configuration file against policies",
		RunE: func(cmd *cobra.Command, args []string) error {
			engine, err := policy.NewEngine(policiesDir)
			if err != nil {
				return fmt.Errorf("failed to create policy engine: %w", err)
			}

			v := validator.New(engine, logger)
			data, err := os.ReadFile(filePath)
			if err != nil {
				return fmt.Errorf("failed to read file: %w", err)
			}

			result, err := v.Validate(cmd.Context(), domain, string(data))
			if err != nil {
				return fmt.Errorf("validation failed: %w", err)
			}

			if result.Valid {
				fmt.Println("✓ Configuration is valid - no policy violations found")
			} else {
				fmt.Printf("✗ Found %d policy violation(s):\n", len(result.Violations))
				for i, v := range result.Violations {
					fmt.Printf("  %d. [%s] %s\n", i+1, v.Severity, v.Message)
				}
				os.Exit(1)
			}
			return nil
		},
	}
	cmd.Flags().StringVar(&domain, "domain", "", "Policy domain (kafka, kubernetes, terraform, cicd, gitops)")
	cmd.Flags().StringVar(&filePath, "file", "", "Configuration file to validate")
	cmd.MarkFlagRequired("domain")
	cmd.MarkFlagRequired("file")
	return cmd
}

func generateCmd() *cobra.Command {
	var requirements string
	cmd := &cobra.Command{
		Use:   "generate",
		Short: "Generate a policy-compliant configuration using AI",
		RunE: func(cmd *cobra.Command, args []string) error {
			engine, err := policy.NewEngine(policiesDir)
			if err != nil {
				return fmt.Errorf("failed to create policy engine: %w", err)
			}

			apiKey := os.Getenv("ANTHROPIC_API_KEY")
			if apiKey == "" {
				return fmt.Errorf("ANTHROPIC_API_KEY environment variable required for generation")
			}

			claude := ai.NewClaudeClient(apiKey)
			policies, err := engine.ListPolicies(domain)
			if err != nil {
				return fmt.Errorf("failed to list policies: %w", err)
			}

			config, err := claude.GenerateConfig(cmd.Context(), domain, requirements, policies)
			if err != nil {
				return fmt.Errorf("generation failed: %w", err)
			}

			fmt.Println(config)
			return nil
		},
	}
	cmd.Flags().StringVar(&domain, "domain", "", "Policy domain")
	cmd.Flags().StringVar(&requirements, "requirements", "", "Natural language requirements")
	cmd.MarkFlagRequired("domain")
	cmd.MarkFlagRequired("requirements")
	return cmd
}

func fixCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "fix",
		Short: "Auto-fix policy violations in a configuration",
		RunE: func(cmd *cobra.Command, args []string) error {
			engine, err := policy.NewEngine(policiesDir)
			if err != nil {
				return fmt.Errorf("failed to create policy engine: %w", err)
			}

			v := validator.New(engine, logger)
			data, err := os.ReadFile(filePath)
			if err != nil {
				return fmt.Errorf("failed to read file: %w", err)
			}

			result, err := v.Validate(cmd.Context(), domain, string(data))
			if err != nil {
				return err
			}

			if result.Valid {
				fmt.Println("✓ No violations to fix")
				return nil
			}

			apiKey := os.Getenv("ANTHROPIC_API_KEY")
			if apiKey == "" {
				return fmt.Errorf("ANTHROPIC_API_KEY required for auto-fix")
			}

			claude := ai.NewClaudeClient(apiKey)
			var violationMsgs []string
			for _, v := range result.Violations {
				violationMsgs = append(violationMsgs, v.Message)
			}

			fixed, err := claude.FixViolations(cmd.Context(), domain, string(data), violationMsgs)
			if err != nil {
				return fmt.Errorf("auto-fix failed: %w", err)
			}

			fmt.Println(fixed)
			return nil
		},
	}
	cmd.Flags().StringVar(&domain, "domain", "", "Policy domain")
	cmd.Flags().StringVar(&filePath, "file", "", "Configuration file to fix")
	cmd.MarkFlagRequired("domain")
	cmd.MarkFlagRequired("file")
	return cmd
}

func listCmd() *cobra.Command {
	cmd := &cobra.Command{
		Use:   "list",
		Short: "List available policies",
		RunE: func(cmd *cobra.Command, args []string) error {
			engine, err := policy.NewEngine(policiesDir)
			if err != nil {
				return fmt.Errorf("failed to create policy engine: %w", err)
			}

			policies, err := engine.ListPolicies(domain)
			if err != nil {
				return err
			}

			if len(policies) == 0 {
				fmt.Println("No policies found")
				return nil
			}

			for _, p := range policies {
				fmt.Printf("  • %s (%s) - %s\n", p.Name, p.Domain, p.Description)
			}
			return nil
		},
	}
	cmd.Flags().StringVar(&domain, "domain", "", "Filter by domain (optional)")
	return cmd
}
