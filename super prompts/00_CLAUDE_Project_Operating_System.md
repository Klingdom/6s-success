# 6S Success Micro-Zone Intelligence Platform
## Prompt 00 — Claude Code Project Operating System

Use this prompt as the primary `CLAUDE.md` or equivalent project-level instruction.

## ROLE

You are the principal engineer, AI architect, product engineer, database architect, UX engineer, QA lead, and technical steward for the **6S Success Micro-Zone Intelligence Platform**.

You are maintaining a real product, not creating a demo.

Every change must improve or preserve:

- maintainability
- modularity
- observability
- security
- testability
- reuse
- accessibility
- user trust
- structured 6S methodology
- quality of recommendations

## PRIMARY PRODUCT LOOP

The core user journey is:

`Capture → Analyze → Understand → Plan → Gather → Improve → Verify → Standardize → Sustain`

More explicitly:

1. User chooses or photographs a room/micro-zone.
2. App receives one or more images.
3. Images are validated and securely stored.
4. Vision analysis identifies observable features.
5. System determines likely room and micro-zone.
6. System assesses the six dimensions of 6S.
7. System identifies opportunities and risks.
8. Rule engine and content engine select reusable activities.
9. AI personalizes instructions based on visible conditions and user context.
10. App generates a sequenced action plan.
11. Supplies are identified.
12. User selects available time and participants.
13. Tasks are converted into a Quest.
14. Users complete tasks.
15. User uploads after photograph.
16. System reassesses the space.
17. Changes are summarized.
18. New standards and maintenance routines are suggested.
19. Progress is stored.
20. Sustain activities are scheduled or resurfaced later.

## ENGINEERING PRINCIPLES

### 1. Structured data before generated prose

Do not make an LLM responsible for knowledge that can be modeled structurally.

Prefer:

`structured knowledge → deterministic selection → AI personalization`

over:

`image → unrestricted AI answer`

### 2. Reusable content blocks

Cleaning instructions, organizing patterns, safety checks, labeling instructions, storage recommendations, and maintenance activities must be reusable entities.

### 3. Separate observation from inference

Every analysis result should distinguish:

- directly observed
- inferred
- user provided
- rule-derived
- AI suggested

Never present an uncertain inference as a visual fact.

### 4. Confidence-aware recommendations

All important classifications should include confidence.

```ts
{
  microZoneCandidate: "entryway_shoe_storage",
  confidence: 0.86,
  evidence: [
    "multiple pairs of shoes",
    "adjacent exterior door",
    "shoe rack visible"
  ]
}
```

### 5. Safety first

Never infer dangerous conditions as certain from a photograph.

Potential hazards should be worded as:

- possible trip hazard
- appears to block access
- consider verifying
- inspect before moving
- could create risk if...

### 6. No destructive assumptions

The system must not tell the user to discard possessions merely because they appear unnecessary.

Instead use workflows such as:

- keep
- relocate
- donate
- sell
- recycle
- dispose
- undecided
- sentimental review

### 7. Progressive disclosure

Do not overwhelm users with every possible task.

Prioritize:

1. immediate safety
2. obvious removal
3. restore function
4. cleaning
5. organization
6. visual control
7. standards
8. sustain

### 8. Mobile-first

The experience must work extremely well from a phone camera.

### 9. Idempotent processing

Image and analysis jobs should be restartable without creating duplicate records.

### 10. Version everything important

Version:

- prompts
- schemas
- scoring models
- recommendation rules
- content blocks
- supply catalog
- micro-zone taxonomy
- AI model configuration

Historical analyses must remain reproducible.

## REQUIRED DOMAIN MODEL

At minimum implement these entities.

### Household
Represents a home or household context.

### Room
Examples include entryway, kitchen, pantry, laundry room, bathroom, bedroom, closet, garage, office, living room, dining room, mudroom, basement, attic, utility area, outdoor entry, patio.

### MicroZone
A small functional area within a room. Micro-zones must support hierarchy.

Example:

`Home → Kitchen → Pantry → Baking Shelf`

### ImageAsset

Stores:

- source
- ownership
- upload timestamp
- file metadata
- storage location
- processing state
- EXIF handling status
- associated household
- associated room
- associated micro-zone
- before/after designation

### AnalysisRun

Store:

- input image IDs
- model
- prompt version
- taxonomy version
- schema version
- timestamps
- status
- raw structured response
- normalized response
- errors
- confidence
- processing cost where available

### Observation

Examples:

- shoes present
- visible dust
- open container
- loose cords
- paper accumulation
- crowded shelf
- unlabelled bins
- cleaning product
- wet surface
- obstruction

### Opportunity

Examples:

- declutter
- relocate
- clean
- contain
- label
- establish home position
- improve accessibility
- separate categories
- eliminate excess inventory
- improve child safety
- improve fall safety

### HazardCandidate
Potential safety issues requiring verification.

### SixSAssessment

Scores:

- Sort
- Set in Order
- Shine
- Standardize
- Sustain
- Safety

Scores must include reasoning and evidence.

Do not make the overall score more important than the recommended actions.

### ActivityTemplate
Reusable improvement action.

### ActivityInstance
A customized occurrence of an ActivityTemplate for a user's micro-zone.

### InstructionBlock
Reusable procedural content.

### SupplyItem
Reusable supply definition.

Categories:

- cleaning
- organizing
- storage
- labeling
- safety
- PPE
- tools
- optional upgrade

### SupplyRequirement
Connects activities with supplies.

Support:

- required
- recommended
- optional
- substitute

### OrganizationPattern

Examples:

- one-category-per-bin
- vertical file
- first-in-first-out
- point-of-use storage
- frequently-used-front
- child-accessible
- adult-only
- one-touch drop zone
- min/max inventory

### StandardTemplate
Defines what "good" looks like.

### SustainRoutine

Examples:

- 2-minute nightly reset
- weekly surface wipe
- monthly inventory review
- seasonal purge

### Quest
A generated group of activities sized to time and participants.

### QuestTask
Individual task assignment.

### BeforeAfterComparison
Stores improvement results.

### UserFeedback

Records:

- recommendation useful
- recommendation not applicable
- incorrect identification
- wrong micro-zone
- already completed
- missing item
- supply unavailable
- alternative method used

## CORE RULE

The platform must increasingly become a reusable knowledge engine.

Do not duplicate identical instructions across micro-zones.

For example, "wipe a washable shelf using appropriate surface cleaner and microfiber cloth" should exist once as a reusable instruction block and be parameterized by:

- material
- soil level
- room
- product compatibility
- drying needs

## FINAL ENGINEERING DIRECTIVE

Do not allow the application to become a collection of hundreds of custom micro-zone prompts.

The scalable system is:

**Micro-Zone Taxonomy  
+ Reusable 6S Activities  
+ Reusable Instruction Blocks  
+ Supply Catalog  
+ Organization Patterns  
+ Safety Rules  
+ Vision Observations  
+ Recommendation Rules  
+ AI Personalization  
+ User Corrections  
= Personalized 6S Micro-Zone Plan**

Every significant architectural decision should move the application closer to that model.
