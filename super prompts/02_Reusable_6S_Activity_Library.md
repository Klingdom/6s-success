# Prompt 02 — Build the Reusable 6S Activity Library

## OBJECTIVE

Create the canonical library of 6S actions from which personalized plans are assembled.

Each ActivityTemplate must belong primarily to one of:

- SORT
- SET_IN_ORDER
- SHINE
- STANDARDIZE
- SUSTAIN
- SAFETY

Activities may have secondary categories.

## REQUIRED ACTIVITY STRUCTURE

```ts
interface ActivityTemplate {
  id: string
  name: string
  primaryS: SixSCategory
  secondaryS: SixSCategory[]

  description: string

  applicableArchetypes: string[]
  applicableRooms: string[]
  applicableMicroZones: string[]

  triggerConditions: RuleExpression[]

  estimatedMinutes: {
    min: number
    typical: number
    max: number
  }

  difficulty: "easy" | "moderate" | "advanced"

  physicalEffort: "low" | "medium" | "high"

  instructionBlockIds: string[]
  supplyRequirementIds: string[]

  prerequisiteActivityIds: string[]
  incompatibleActivityIds: string[]

  verificationCriteria: string[]

  safetyNotes: string[]

  reusableParameters: Record<string, unknown>

  version: number
}
```

## EXAMPLES

### Sort

- remove obvious trash
- remove expired products
- gather misplaced items
- group like items
- identify duplicates
- separate rarely used items
- identify donation candidates
- quarantine undecided items
- reduce excessive inventory
- remove items unrelated to zone function

### Set in Order

- assign home position
- create category container
- place high-use items at point of use
- move low-frequency items to secondary storage
- separate categories
- establish return location
- create drop zone
- use drawer divider
- use tray
- use bin
- use hooks
- use vertical storage
- define charging position

### Shine

- dry dust
- vacuum
- sweep
- wipe
- degrease
- disinfect when appropriate
- remove residue
- clean container
- clean drawer
- clean cabinet
- clean hardware
- wash textile
- clean glass
- clean mirror

### Standardize

- label home position
- label container
- create visual boundary
- create category standard
- define inventory limit
- define replenishment point
- photograph target condition
- define order of items
- create color or icon cue

### Sustain

- two-minute reset
- nightly reset
- weekly reset
- monthly purge
- quarterly review
- reorder review
- audit quantity limits
- inspect labels
- refresh standard image

### Safety

- clear walkway
- remove unstable stack
- separate incompatible chemicals
- relocate medication
- relocate sharp objects
- protect child-access areas
- reduce fall hazards
- address exposed cord
- improve visibility
- keep emergency access clear

Build these as reusable templates rather than prose-only entries.

## DELIVERABLES

Create:

- schema
- seed library
- rule-expression format
- dependency handling
- versioning
- validation
- import/export support
- unit tests
- duplication checks
