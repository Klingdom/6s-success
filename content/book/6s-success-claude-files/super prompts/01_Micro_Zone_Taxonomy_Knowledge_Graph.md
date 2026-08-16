# Prompt 01 — Build the Micro-Zone Taxonomy and Knowledge Graph

## OBJECTIVE

Create the canonical taxonomy that allows the entire application to reason consistently about homes.

Build a hierarchical, extensible taxonomy for:

`Home → Room → Zone → MicroZone → Function → ObjectCategory`

Each micro-zone should include structured metadata.

## REQUIRED MICRO-ZONE FIELDS

```ts
interface MicroZoneDefinition {
  id: string
  slug: string
  name: string
  roomTypes: string[]
  parentId?: string

  primaryFunctions: string[]
  secondaryFunctions: string[]

  commonObjects: string[]
  commonObjectCategories: string[]

  commonSurfaces: string[]
  commonStorageTypes: string[]

  commonSortProblems: string[]
  commonSetInOrderProblems: string[]
  commonShineProblems: string[]
  commonStandardizeProblems: string[]
  commonSustainProblems: string[]
  commonSafetyProblems: string[]

  recommendedActivityTemplateIds: string[]
  applicableOrganizationPatternIds: string[]
  applicableSupplyIds: string[]

  typicalResetMinutes: {
    light: number
    moderate: number
    heavy: number
  }

  visualRecognitionHints: string[]

  version: number
}
```

## BUILD INITIAL COVERAGE

Create comprehensive taxonomy coverage for common residential micro-zones across:

- entryway
- mudroom
- living room
- family room
- kitchen
- pantry
- dining room
- primary bedroom
- children's bedroom
- guest bedroom
- nursery
- primary bathroom
- guest bathroom
- linen closet
- coat closet
- walk-in closet
- reach-in closet
- laundry room
- home office
- craft area
- playroom
- garage
- workshop
- utility room
- basement
- attic
- storage room
- stairs
- hallway
- patio
- porch
- exterior entry
- vehicle-related household storage

Aim for **at least 150 meaningful micro-zones**, but architect the system for thousands.

## IMPORTANT

Do not create 150 unrelated strings.

Use reusable archetypes such as:

- horizontal work surface
- open shelf
- closed cabinet
- shallow drawer
- deep drawer
- hanging storage
- floor storage
- vertical storage
- drop zone
- consumable storage
- cleaning station
- personal care station
- paper processing station
- electronics station
- children's access zone
- hazardous storage zone

A micro-zone can inherit behaviors from one or more archetypes.

## DELIVERABLES

Create:

1. taxonomy schema
2. seed data
3. validation rules
4. inheritance/archetype mechanism
5. canonical IDs and slugs
6. migrations or import scripts
7. tests
8. documentation describing how to add future rooms and micro-zones
