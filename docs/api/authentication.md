# Authentication & Authorization Specification

## 1. Zero-Trust Security Strategy
`context-router` mandates two-way mutual TLS (mTLS) for all transport connections and OAuth 2.0 JWT validation for request level context identification.

```mermaid
sequenceDiagram
    participant Gateway as API Gateway
    participant Router as context-router
    participant KMS as KMS Key Vault

    Gateway->>Router: Handshake TLS 1.3 (Client Certificate)
    Router->>Gateway: Certificate Verified (mTLS ACK)
    Gateway->>Router: POST /v1/context/route (Bearer JWT)
    Router->>KMS: Get Public JWKS Keys
    KMS-->>Router: Public Key Set
    Router->>Router: Cryptographically Validate Signature, Expiry, & Tenant Claims
```

## 2. JWT Claims Schema
```json
{
  "iss": "https://auth.enterprise.internal",
  "sub": "service-agent-01",
  "aud": "context-router-api",
  "exp": 1785945600,
  "iat": 1785942000,
  "tenant_id": "tenant-corp-alpha",
  "roles": ["context:route", "session:read"],
  "data_residency": ["EU", "US"]
}
```