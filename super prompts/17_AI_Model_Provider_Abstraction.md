# Prompt 17 — Add or Improve an AI Model Super Prompt

## OBJECTIVE

Change AI providers or models without coupling product behavior to one vendor.

All AI access must use provider-independent interfaces.

Create abstractions such as:

```ts
interface VisionAnalyzer {
  analyze(input: VisionInput): Promise<VisionAnalysis>
}

interface InstructionPersonalizer {
  personalize(
    activity: ActivityInstance,
    context: PersonalizationContext
  ): Promise<ActivityInstruction>
}
```

Provider implementations may include:

- Anthropic
- OpenAI
- Google
- local models
- future providers

Business logic should never directly depend on provider-specific response structures.

## BEFORE SWITCHING MODELS

1. run existing evaluation suite
2. compare accuracy
3. compare hallucination rate
4. compare latency
5. compare cost
6. compare structured-output reliability
7. compare recommendation usefulness

Do not deploy purely because a model is newer.

## DELIVERABLES

Create:

- provider-independent interfaces
- provider adapters
- model configuration
- versioning
- fallback strategy
- retry strategy
- cost telemetry
- eval comparison report
- tests
