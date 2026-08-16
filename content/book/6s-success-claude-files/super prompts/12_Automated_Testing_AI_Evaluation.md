# Prompt 12 — Build Automated Testing and AI Evaluation

## OBJECTIVE

Treat AI behavior like software behavior.

Create automated tests for both code and recommendation quality.

## STANDARD TESTS

Implement:

- unit tests
- integration tests
- API tests
- database tests
- authorization tests
- upload tests
- UI tests
- accessibility tests
- end-to-end tests

## AI EVALUATION DATASET

Create a versioned evaluation suite with representative scenarios.

Examples:

- clean entryway
- moderately cluttered entryway
- heavily cluttered entryway
- shoe overflow
- mail accumulation
- children's items
- small apartment entry
- luxury entry
- minimalist entry
- mobility-sensitive layout
- dark photograph
- blurry photograph
- partial micro-zone
- multiple micro-zones visible

Add representative scenarios from every major room.

## TEST QUESTIONS

### Classification

Did it identify the correct room?

Did it identify plausible micro-zones?

### Grounding

Were observations actually visible?

### Hallucination

Did it invent objects?

### 6S completeness

Did it consider all six categories?

### Safety

Did it express uncertainty appropriately?

### Reuse

Did it select existing activity templates before inventing a new activity?

### Supplies

Were supplies appropriate for the activity?

### Actionability

Could a normal household user complete the instructions?

### Overload

Did it produce too many tasks?

### Tone

Was the feedback constructive and practical?

## DELIVERABLES

Create:

- eval fixture format
- expected outcomes
- scoring harness
- regression thresholds
- CI integration
- provider/model comparison reports
- failure triage output
