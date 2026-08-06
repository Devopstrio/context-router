# API Architectural Overview

`context-router` exposes high-performance RESTful APIs operating over HTTP/2 with JSON payloads. Protocols are designed for ultra-low latency serialization and sub-millisecond network parsing.

## 1. Key API Guarantees
* **Strict Backward Compatibility:** Versioning via URI path (`/v1/...`). Breaking schema changes require bump to `/v2/...`.
* **Idempotency:** All non-mutating evaluations support strict request tracing via `X-Correlation-ID`.
* **Uniform Error Responses:** RFC 7807 Problem Details compliant error structures across all endpoints.

## 2. Communication Standards
* **Protocol:** HTTP/2 (mTLS enforced inter-service).
* **Payload Format:** `application/json; charset=utf-8`.
* **Compression:** `gzip` or `br` (Brotli) supported for large payloads.
* **Timeouts:** Global gateway hard timeout set to $2000\text{ms}$.