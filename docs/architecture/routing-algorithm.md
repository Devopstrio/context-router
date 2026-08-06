# Context Routing Algorithm Specification

## 1. Mathematical Formulation

The optimal model selection decision $m^*$ is determined by maximizing the Target Score $S_i$ over all eligible models $M_{filtered}$:

$$m^* = \arg\max_{m_i \in M_{filtered}} S_i$$

Where $S_i$ is calculated as:

$$S_i = \left( w_c \cdot \frac{C_{max} - C_i}{C_{max}} \right) + \left( w_l \cdot \frac{L_{max} - L_i}{L_{max}} \right) + \left( w_h \cdot H_i \right) + \left( w_a \cdot A_i \right)$$

### Parameter Definitions
* $C_i$: Cost per 1k input tokens for model $m_i$.
* $L_i$: P99 historical latency (ms) for model $m_i$.
* $H_i \in [0, 1]$: Real-time health score of model target $m_i$ provided by circuit breaker.
* $A_i \in \{0, 1\}$: Tenant regional affinity match boolean.
* $w_c, w_l, w_h, w_a$: Configurable weight coefficients ($w_c + w_l + w_h + w_a = 1.0$).

## 2. Pseudo-Logic Decision Path

```
FUNCTION ResolveOptimalRoute(Request R, Tenant T, Session S):
    // Step 1: Query Policy Constraints
    Policies = PolicyEngineClient.GetTenantPolicies(T.ID)
    
    // Step 2: Query Active Memory Pointer
    MemoryState = MemoryManagerClient.GetSessionState(S.ID)
    
    // Step 3: Compute Context Mass Estimate
    TotalTokens = TokenBudgetClient.EstimatePayloadTokens(R.Payload, MemoryState)
    
    // Step 4: Filter Model Registry
    EligibleModels = []
    FOR EACH model IN ModelRegistry.GetAll():
        IF model.ContextWindow >= TotalTokens AND
           model.Region IN Policies.AllowedRegions AND
           model.CostPerToken <= Policies.MaxCostPerToken AND
           CircuitBreakers[model.ID].State != OPEN:
            EligibleModels.Append(model)
            
    IF EligibleModels.IsEmpty():
        // Trigger Emergency Truncation Plan
        TruncatedPayload = TokenBudgetClient.TruncateToLimit(R.Payload, Policies.FallbackMaxTokens)
        RETURN ResolveOptimalRoute(TruncatedPayload, T, S)
        
    // Step 5: Score Eligible Models
    BestModel = NULL
    HighestScore = -1.0
    FOR EACH model IN EligibleModels:
        Score = ComputeModelScore(model, Policies.Weights)
        IF Score > HighestScore:
            HighestScore = Score
            BestModel = model
            
    // Step 6: Construct Fallback Chain
    FallbackChain = SelectTopNRunnersUp(EligibleModels, BestModel, Count=2)
    
    RETURN ConstructRouteSpec(BestModel, FallbackChain, TotalTokens)
```