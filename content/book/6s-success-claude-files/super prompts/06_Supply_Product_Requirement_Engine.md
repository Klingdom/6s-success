# Prompt 06 — Build the Supply and Product Requirement Engine

## OBJECTIVE

Create a reusable supply catalog that supports every 6S activity.

## SUPPLY CLASSES

### Cleaning

- microfiber cloth
- vacuum
- broom
- dustpan
- mop
- bucket
- glass cleaner
- appropriate general surface cleaner
- degreaser
- scrub brush
- sponge
- disposable towel
- trash bag

### Organization

- tray
- basket
- open bin
- closed bin
- drawer divider
- hook
- shelf
- riser
- turntable
- file holder
- cable organizer
- shoe rack

### Visual Control

- labels
- QR labels
- category cards
- bin markers
- visual boundaries
- min/max markers

### Safety

- gloves
- step stool
- child-resistant storage
- cord management
- non-slip products
- appropriate protective equipment

## SUPPLY MODEL

```ts
interface SupplyItem {
  id: string
  name: string
  genericName: string
  category: string
  subcategory: string

  functions: string[]

  reusable: boolean
  consumable: boolean

  alternatives: string[]

  incompatibleSurfaces: string[]
  cautions: string[]

  typicalMicroZones: string[]

  inventoryTrackable: boolean

  version: number
}
```

## IMPORTANT PRODUCT PRINCIPLE

Start with **generic product types**.

Do not require a specific retailer or brand for the activity engine.

Retailer-specific recommendations should be a separate optional commerce layer.

## USER SUPPLY INVENTORY

Allow users to mark:

- I own this
- I need this
- substitute available
- not applicable

Quest creation should prefer activities that can be performed using supplies already available.

## DELIVERABLES

Create:

- SupplyItem model
- SupplyRequirement model
- substitutions
- compatibility rules
- user inventory
- quest supply aggregation
- "gather first" output
- tests
