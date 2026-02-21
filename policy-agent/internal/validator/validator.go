package validator

import (
	"context"

	"github.com/sankar276/policy-agent/internal/policy"
	"go.uber.org/zap"
)

type Validator struct {
	engine *policy.Engine
	logger *zap.Logger
}

func New(engine *policy.Engine, logger *zap.Logger) *Validator {
	return &Validator{engine: engine, logger: logger}
}

func (v *Validator) Validate(ctx context.Context, domain string, configYAML string) (*policy.ValidationResult, error) {
	v.logger.Info("Validating configuration", zap.String("domain", domain))

	result, err := v.engine.Evaluate(ctx, domain, configYAML)
	if err != nil {
		v.logger.Error("Validation failed", zap.Error(err))
		return nil, err
	}

	v.logger.Info("Validation complete",
		zap.Bool("valid", result.Valid),
		zap.Int("violations", len(result.Violations)),
	)

	return result, nil
}
