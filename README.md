<div align="center">

<img src="https://raw.githubusercontent.com/Devopstrio/.github/main/assets/Browser_logo.png" height="90"/>

<h1>context-router</h1>

<p><strong>Enterprise Context Engineering Platform - High-Performance Context & Model Router</strong></p>

[![Build Status](https://img.shields.io/badge/Build-Passing-10B981?style=flat-square)](https://devopstrio.co.uk)
[![Python Version](https://img.shields.io/badge/Python-3.11%2B-3776AB.svg?style=flat-square)](https://python.org)
[![Context Router](https://img.shields.io/badge/Context-Router-8B5CF6?style=flat-square)](https://devopstrio.co.uk)
[![Terraform](https://img.shields.io/badge/IaC-OpenTofu_1.8.5-FF5733?style=flat-square)](https://opentofu.org)

</div>

---

`context-router` is the enterprise-grade context orchestration, model matching, and dispatch control plane for high-scale Enterprise AI platforms handling millions of daily inference requests. It acts as the intelligent routing traffic controller within the Enterprise Context Engineering ecosystem, ensuring low-latency, cost-optimized, and strictly isolated context delivery to Foundational Models (LLMs/SLMs).

---

## 🏛 Document Architecture Map

This repository serves as the authoritative, implementation-ready engineering blueprint and production codebase for `context-router`.

```
context-router/
├── README.md                           # Main Architecture Portal & Quick Start
├── pyproject.toml                      # Python Dependencies & Package Manifest
├── Dockerfile                          # Multi-Stage Production Container Specification
├── docker-compose.yml                  # Local Dev & Integration Environment
├── .github/workflows/ci.yaml           # GitHub Actions CI/CD Pipeline
├── src/context_router/                 # Core Python Application Source
│   ├── api/                            # REST Routes & Probes (/v1/context/route, /health)
│   ├── cache/                          # Dual-Tier Cache (L1 Memory TTL + L2 Redis Cluster)
│   ├── config/                         # Settings & Dynamic Model Capabilities Registry
│   ├── contracts/                      # Sibling Microservice Integration Clients
│   ├── observability/                  # Prometheus Metrics, OpenTelemetry Tracing & Logging
│   ├── resiliency/                     # Circuit Breaker & Fallback Controller
│   ├── routing/                        # Routing Decision Matrix, Rule Engine & State Machine
│   ├── security/                       # JWT Authentication & TenantIsolationGuard
│   └── validation/                     # OpenAPI 3.1 Pydantic Schemas & RFC 7807 Error Handlers
├── deployment/                         # IaC Infrastructure Declarations
│   ├── kubernetes/                     # Base Kustomize & Dev/Staging/Prod Overlays
│   └── terraform/                      # Multi-Cloud Terraform Blueprints
├── docs/                               # Architecture Specifications & Diagrams
├── schemas/                            # Strict Data Validation Schemas
└── tests/                              # Unit, Integration, & API Test Suite (>90% Coverage)
```

---

## 🔑 Core Architecture Principles

1. **Deterministic Sub-12ms Latency (P99.9):** High-efficiency execution path utilizing dual-tier caching (L1 In-Memory TTL + L2 Redis Cluster) and non-blocking asynchronous event emission.
2. **Zero-Trust Tenant Boundaries:** Strict cryptographic context tagging (`TenantID` + `SessionID`) verified at every module boundary to eliminate cross-tenant data leaks.
3. **Dynamic Provider Resiliency:** Real-time circuit breaker health tracking with automatic dynamic failover to secondary provider regions during rate limiting (HTTP 429) or endpoint degradation.
4. **Decoupled Architecture:** Strict separation of responsibilities. `context-router` executes decision logic and context dispatching; physical prompt assembly, token truncation, and vector fetches are delegated to specialized sibling repositories via gRPC/REST.

---

## 🛠 High-Level Repository Architecture Diagram

```mermaid
graph TD
    A[Client Gateway / Agent Engine] -->|POST /v1/context/route| B[context-router Core Engine]
    
    subgraph context-router Core
        B --> C[IngressValidator & TenantGuard]
        C --> D[Routing Decision Matrix]
        D --> E[Resiliency Controller]
    end

    subgraph Sibling Services Contract
        D -->|gRPC Check| F[policy-engine]
        D -->|gRPC Get History| G[memory-manager]
        D -->|HTTP Evaluate Budget| H[token-budget-optimizer]
        E -->|Submit Assembly Job| I[context-assembler]
        B -.->|Async Kafka Log| J[audit-service]
    end
```

---

## 🚀 Quick Start & Local Execution

### 1. Installation & Environment Setup

```bash
# Clone repository
git clone https://github.com/Devopstrio/context-router.git
cd context-router

# Create virtual environment & install dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -e ".[dev]"
```

### 2. Running Quality Checks & Test Suite

```bash
# Linting & Formatting
ruff check .

# Type Checking
mypy .

# Security Scan
bandit -r src/ -ll -ii

# Unit & Integration Tests with Coverage
pytest --cov=src/context_router --cov-report=term-missing
```

### 3. Launching Service Locally

```bash
# Start with Uvicorn dev server
uvicorn context_router.main:app --host 127.0.0.1 --port 8080 --reload
```

---

<div align="center">
© 2026 Devopstrio — Engineering the Autonomous Enterprise.
</div>