FROM golang:1.22-alpine AS builder

WORKDIR /build

COPY go.mod go.sum ./
RUN go mod download

COPY . .

RUN CGO_ENABLED=0 GOOS=linux go build -o /bin/policy-agent ./cmd/policy-agent
RUN CGO_ENABLED=0 GOOS=linux go build -o /bin/webhook ./cmd/webhook

FROM alpine:3.20

RUN apk add --no-cache ca-certificates

COPY --from=builder /bin/policy-agent /usr/local/bin/policy-agent
COPY --from=builder /bin/webhook /usr/local/bin/webhook

EXPOSE 8443

ENTRYPOINT ["webhook"]
CMD ["--port", "8443", "--policies-dir", "/policies"]
