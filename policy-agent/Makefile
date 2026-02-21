.PHONY: build test lint clean run-cli run-webhook docker-build

BINARY_CLI=policy-agent
BINARY_WEBHOOK=webhook
BUILD_DIR=bin

build:
	go build -o $(BUILD_DIR)/$(BINARY_CLI) ./cmd/policy-agent
	go build -o $(BUILD_DIR)/$(BINARY_WEBHOOK) ./cmd/webhook

test:
	go test ./... -v -race -cover

lint:
	go vet ./...
	@command -v golangci-lint >/dev/null 2>&1 && golangci-lint run || echo "golangci-lint not installed, skipping"

clean:
	rm -rf $(BUILD_DIR)

run-cli:
	go run ./cmd/policy-agent $(ARGS)

run-webhook:
	go run ./cmd/webhook --port 8443 --policies-dir ../../policies

docker-build:
	docker build -t policy-agent:latest .

validate-example:
	go run ./cmd/policy-agent validate --domain kubernetes --file examples/deployment.yaml --policies-dir ../../policies
