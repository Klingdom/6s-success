# Prompt 15 — Reusable Content Audit Super Prompt

## OBJECTIVE

Continuously reduce duplicated content.

Inspect:

- ActivityTemplates
- InstructionBlocks
- SupplyRequirements
- OrganizationPatterns
- SustainRoutines
- SafetyRules

Identify near duplicates.

Example duplication:

- Wipe entryway shelf
- Wipe pantry shelf
- Wipe bathroom shelf

These likely should become:

`clean_washable_shelf`

with parameters:

```ts
{
  surfaceType,
  soilType,
  roomContext,
  recommendedCleaner,
  dryingMethod
}
```

Create reusable abstraction where doing so improves clarity.

Do not over-generalize tasks that genuinely require distinct procedures.

## PRODUCE

For every candidate:

- duplicate candidate
- recommended canonical content
- required parameters
- affected records
- migration plan
- regression tests

## IMPLEMENTATION RULE

Do not delete referenced historical content. Migrate current references and deprecate obsolete records where appropriate.
