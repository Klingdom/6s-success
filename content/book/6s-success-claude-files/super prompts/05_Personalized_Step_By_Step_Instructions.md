# Prompt 05 — Build Personalized Step-by-Step Instructions

## OBJECTIVE

Turn selected ActivityTemplates into highly usable instructions.

## INSTRUCTION ARCHITECTURE

Each ActivityInstance should produce:

1. Why this matters
2. What success looks like
3. Supplies needed
4. Preparation
5. Step-by-step instructions
6. Decision points
7. Safety considerations
8. Completion check
9. Optional improvement
10. Sustain action

## SAMPLE OUTPUT STRUCTURE

```ts
interface ActivityInstruction {
  activityInstanceId: string

  title: string
  reason: string

  estimatedMinutes: number

  supplies: {
    required: SupplyReference[]
    recommended: SupplyReference[]
    optional: SupplyReference[]
  }

  preparationSteps: Step[]
  actionSteps: Step[]
  decisionPoints: DecisionPoint[]

  verificationSteps: Step[]

  completionCriteria: string[]

  optionalUpgrades: Upgrade[]

  sustainSuggestion?: SustainSuggestion
}
```

## PERSONALIZATION PARAMETERS

Use:

- detected surface material
- storage type
- item category
- estimated volume
- available supplies
- available containers
- user time
- number of players
- accessibility preferences
- children or pets only when explicitly provided
- user skill level
- prior activities
- existing standard

Never unnecessarily regenerate generic instructions.

Example:

A microfiber wiping procedure should be a reusable content block.

The final user instruction may inject:

- entry console
- painted wood
- light dust
- microfiber cloth

## DELIVERABLES

Build:

- InstructionBlock model
- parameter substitution
- content selection rules
- personalization service
- fallback behavior when AI is unavailable
- tests ensuring reused instructions remain consistent
