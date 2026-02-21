package webhook

import (
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"

	"github.com/sankar276/policy-agent/internal/ai"
	"github.com/sankar276/policy-agent/internal/policy"
	"github.com/sankar276/policy-agent/internal/validator"
	"go.uber.org/zap"
)

type Handler struct {
	validator *validator.Validator
	engine    *policy.Engine
	claude    *ai.ClaudeClient
	logger    *zap.Logger
}

func NewHandler(v *validator.Validator, engine *policy.Engine, claude *ai.ClaudeClient, logger *zap.Logger) *Handler {
	return &Handler{validator: v, engine: engine, claude: claude, logger: logger}
}

type validateRequest struct {
	Domain string `json:"domain"`
	Config string `json:"config"`
}

type generateRequest struct {
	Domain       string `json:"domain"`
	Requirements string `json:"requirements"`
}

type fixRequest struct {
	Domain     string   `json:"domain"`
	Config     string   `json:"config"`
	Violations []string `json:"violations"`
}

func (h *Handler) HandleValidate(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	var req validateRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}

	result, err := h.validator.Validate(r.Context(), req.Domain, req.Config)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
		return
	}

	writeJSON(w, http.StatusOK, result)
}

func (h *Handler) HandleGenerate(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if h.claude == nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]string{"error": "AI features not configured"})
		return
	}

	var req generateRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}

	policies, err := h.engine.ListPolicies(req.Domain)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
		return
	}

	config, err := h.claude.GenerateConfig(r.Context(), req.Domain, req.Requirements, policies)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
		return
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{
		"domain": req.Domain,
		"config": config,
		"validated": true,
	})
}

func (h *Handler) HandleFix(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	if h.claude == nil {
		writeJSON(w, http.StatusServiceUnavailable, map[string]string{"error": "AI features not configured"})
		return
	}

	var req fixRequest
	if err := json.NewDecoder(r.Body).Decode(&req); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}

	fixed, err := h.claude.FixViolations(r.Context(), req.Domain, req.Config, req.Violations)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
		return
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{
		"domain":       req.Domain,
		"fixed_config": fixed,
		"original":     req.Config,
	})
}

func (h *Handler) HandleListPolicies(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodGet {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	domain := strings.TrimPrefix(r.URL.Path, "/policies/")
	domain = strings.TrimPrefix(domain, "/policies")
	domain = strings.Trim(domain, "/")

	policies, err := h.engine.ListPolicies(domain)
	if err != nil {
		writeJSON(w, http.StatusInternalServerError, map[string]string{"error": err.Error()})
		return
	}

	writeJSON(w, http.StatusOK, map[string]interface{}{"policies": policies})
}

// HandleAdmission handles K8s ValidatingWebhook admission requests
func (h *Handler) HandleAdmission(w http.ResponseWriter, r *http.Request) {
	if r.Method != http.MethodPost {
		http.Error(w, "method not allowed", http.StatusMethodNotAllowed)
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		h.logger.Error("Failed to read admission request", zap.Error(err))
		writeAdmissionResponse(w, "", false, "failed to read request")
		return
	}

	var admissionReview map[string]interface{}
	if err := json.Unmarshal(body, &admissionReview); err != nil {
		writeAdmissionResponse(w, "", false, "invalid admission review")
		return
	}

	request, ok := admissionReview["request"].(map[string]interface{})
	if !ok {
		writeAdmissionResponse(w, "", false, "missing request in admission review")
		return
	}

	uid := fmt.Sprintf("%v", request["uid"])

	object, _ := json.Marshal(request["object"])
	configYAML := string(object)

	kind, _ := request["kind"].(map[string]interface{})
	domain := detectDomain(fmt.Sprintf("%v", kind["kind"]))

	result, err := h.validator.Validate(r.Context(), domain, configYAML)
	if err != nil {
		h.logger.Error("Admission validation failed", zap.Error(err))
		writeAdmissionResponse(w, uid, true, "") // allow on error
		return
	}

	if result.Valid {
		writeAdmissionResponse(w, uid, true, "")
	} else {
		var msgs []string
		for _, v := range result.Violations {
			msgs = append(msgs, fmt.Sprintf("[%s] %s", v.Severity, v.Message))
		}
		writeAdmissionResponse(w, uid, false, strings.Join(msgs, "; "))
	}
}

func detectDomain(kind string) string {
	switch strings.ToLower(kind) {
	case "deployment", "pod", "service", "statefulset", "daemonset":
		return "kubernetes"
	case "kafkatopic", "kafkaconnector":
		return "kafka"
	default:
		return "kubernetes"
	}
}

func writeJSON(w http.ResponseWriter, status int, data interface{}) {
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(status)
	json.NewEncoder(w).Encode(data)
}

func writeAdmissionResponse(w http.ResponseWriter, uid string, allowed bool, message string) {
	resp := map[string]interface{}{
		"apiVersion": "admission.k8s.io/v1",
		"kind":       "AdmissionReview",
		"response": map[string]interface{}{
			"uid":     uid,
			"allowed": allowed,
		},
	}
	if message != "" {
		resp["response"].(map[string]interface{})["status"] = map[string]interface{}{
			"message": message,
		}
	}
	writeJSON(w, http.StatusOK, resp)
}
