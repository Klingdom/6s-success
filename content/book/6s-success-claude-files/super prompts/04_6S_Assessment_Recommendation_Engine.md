# Prompt 04 — Build the 6S Assessment and Recommendation Engine

## OBJECTIVE

Translate observations into structured 6S opportunities.

Implement this as a hybrid system:

`Vision observations + taxonomy + deterministic rules + activity templates + AI reasoning`

The LLM must not directly invent the entire plan.

## ASSESS EACH S

### Sort

Evaluate:

- unrelated items
- excess quantity
- duplicates
- apparent trash
- expired or obsolete candidates
- displaced objects
- overfilled containers
- unnecessary packaging

### Set in Order

Evaluate:

- assigned locations
- grouping
- accessibility
- point-of-use placement
- container fit
- retrieval effort
- return effort
- vertical versus horizontal utilization
- wasted space
- visibility

### Shine

Evaluate only visually supportable indicators:

- dust
- debris
- stains
- residue
- visible spills
- visibly soiled surfaces

Avoid asserting sanitation.

### Standardize

Evaluate:

- labels
- category consistency
- home positions
- container consistency
- visual boundaries
- quantity limits
- obvious standards

### Sustain

This is difficult to infer from one image.

Use current-state indicators plus user history.

Do not claim poor sustaining behavior from a photograph.

### Safety

Identify possible:

- trip risks
- falling object risks
- blocked access
- child access
- sharp-object access
- chemical-access concerns
- overloaded or unstable storage
- wet floor
- cord routing

Require verification where necessary.

## SCORING

Use a 0-5 scale per S.

Scores are advisory and subordinate to recommended actions.

Include:

- score
- confidence
- positive observations
- improvement opportunities

Do not punish the user for décor, aesthetic preferences, home size, income, or ownership status.

## DELIVERABLES

Create:

- SixSAssessment service
- reusable rule engine
- opportunity model
- activity-template selection logic
- confidence propagation
- rule traceability
- tests across representative micro-zones
