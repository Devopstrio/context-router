# OpenAPI 3.1 Specification: `context-router`

```yaml
openapi: 3.1.0
info:
  title: Context Router API
  version: 1.0.0
  description: Enterprise Context Orchestration, Routing, and Dispatch Service.
servers:
  - url: https://router.context.internal/v1
    description: Internal Production Cluster
paths:
  /context/route:
    post:
      summary: Evaluate and Route Context Payload
      operationId: evaluateAndRoute
      security:
        - BearerAuth: []
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/RouteRequest'
      responses:
        '200':
          description: Route evaluated successfully.
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/RouteResponse'
        '400':
          $ref: '#/components/responses/400BadRequest'
        '401':
          $ref: '#/components/responses/401Unauthorized'
        '403':
          $ref: '#/components/responses/403Forbidden'
        '503':
          $ref: '#/components/responses/503ServiceUnavailable'

components:
  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

  schemas:
    RouteRequest:
      type: object
      required:
        - tenant_id
        - session_id
        - request_context
      properties:
        tenant_id:
          type: string
          example: "tenant-corp-alpha"
        session_id:
          type: string
          example: "sess-9923-bf34-9981"
        agent_id:
          type: string
          example: "agent-customer-support"
        request_context:
          type: object
          required:
            - user_query
          properties:
            user_query:
              type: string
            latency_priority:
              type: string
              enum: [ultra-low, balanced, high-accuracy]
              default: balanced
        constraints:
          type: object
          properties:
            max_cost_per_1k_tokens:
              type: number
            allowed_providers:
              type: array
              items:
                type: string

    RouteResponse:
      type: object
      required:
        - route_id
        - target_model
        - execution_plan
        - telemetry
      properties:
        route_id:
          type: string
        target_model:
          type: object
          required:
            - provider
            - model_id
            - endpoint
          properties:
            provider:
              type: string
            model_id:
              type: string
            endpoint:
              type: string
        execution_plan:
          type: object
          properties:
            session_lookup_required:
              type: boolean
            max_token_budget:
              type: integer
            fallback_chain:
              type: array
              items:
                type: string
        telemetry:
          type: object
          properties:
            routing_time_ms:
              type: number
            estimated_cost_usd:
              type: number

  responses:
    400BadRequest:
      description: Invalid payload schema.
    401Unauthorized:
      description: Authentication failure.
    403Forbidden:
      description: Tenant validation or compliance error.
    503ServiceUnavailable:
      description: Routing targets unavailable.
```