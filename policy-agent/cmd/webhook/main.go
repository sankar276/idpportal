package main

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"os"
	"os/signal"
	"syscall"
	"time"

	"github.com/sankar276/policy-agent/internal/ai"
	"github.com/sankar276/policy-agent/internal/policy"
	"github.com/sankar276/policy-agent/internal/validator"
	webhookpkg "github.com/sankar276/policy-agent/internal/webhook"
	"github.com/spf13/cobra"
	"go.uber.org/zap"
)

func main() {
	logger, _ := zap.NewProduction()
	defer logger.Sync()

	var port int
	var policiesDir string

	rootCmd := &cobra.Command{
		Use:   "webhook",
		Short: "Policy Agent webhook server and HTTP API",
		RunE: func(cmd *cobra.Command, args []string) error {
			engine, err := policy.NewEngine(policiesDir)
			if err != nil {
				return fmt.Errorf("failed to create policy engine: %w", err)
			}

			v := validator.New(engine, logger)

			var claude *ai.ClaudeClient
			if apiKey := os.Getenv("ANTHROPIC_API_KEY"); apiKey != "" {
				claude = ai.NewClaudeClient(apiKey)
				logger.Info("AI generation/remediation enabled")
			} else {
				logger.Warn("ANTHROPIC_API_KEY not set, AI features disabled")
			}

			handler := webhookpkg.NewHandler(v, engine, claude, logger)

			mux := http.NewServeMux()

			// K8s admission webhook
			mux.HandleFunc("/webhook/validate", handler.HandleAdmission)

			// HTTP API for Python backend
			mux.HandleFunc("/validate", handler.HandleValidate)
			mux.HandleFunc("/generate", handler.HandleGenerate)
			mux.HandleFunc("/fix", handler.HandleFix)
			mux.HandleFunc("/policies", handler.HandleListPolicies)
			mux.HandleFunc("/policies/", handler.HandleListPolicies)
			mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
				json.NewEncoder(w).Encode(map[string]string{"status": "healthy"})
			})

			srv := &http.Server{
				Addr:         fmt.Sprintf(":%d", port),
				Handler:      mux,
				ReadTimeout:  30 * time.Second,
				WriteTimeout: 60 * time.Second,
			}

			go func() {
				logger.Info("Starting policy agent server", zap.Int("port", port))
				if err := srv.ListenAndServe(); err != nil && err != http.ErrServerClosed {
					logger.Fatal("Server failed", zap.Error(err))
				}
			}()

			quit := make(chan os.Signal, 1)
			signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
			<-quit

			ctx, cancel := context.WithTimeout(context.Background(), 10*time.Second)
			defer cancel()
			return srv.Shutdown(ctx)
		},
	}

	rootCmd.Flags().IntVar(&port, "port", 8443, "Server port")
	rootCmd.Flags().StringVar(&policiesDir, "policies-dir", "/policies", "Policies directory")

	if err := rootCmd.Execute(); err != nil {
		os.Exit(1)
	}
}
