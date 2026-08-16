# Prompt 03 — Build Image Intake, Vision Analysis, and Micro-Zone Recognition

## OBJECTIVE

Implement the complete image-analysis pipeline.

## INPUT MODES

Support:

- camera capture
- photo library upload
- drag and drop
- multiple photographs
- optional wide-angle overview
- optional close-up photographs

## IMAGE PIPELINE

Implement:

`Upload → Validate → Normalize → Store → Analyze → Normalize AI Output → Rules → Recommendations`

## IMAGE SECURITY

Implement:

- signed uploads where appropriate
- private object storage by default
- authenticated access
- file type validation
- file size limits
- malware-safe handling where applicable
- EXIF metadata stripping unless required
- orientation normalization
- thumbnail generation
- retention controls
- deletion workflow

Never expose public permanent storage URLs.

## VISION ANALYSIS

The vision model must produce **structured JSON**, not free-form advice.

Required response schema:

```ts
interface MicroZoneVisionResult {
  detectedRoomCandidates: Candidate[]
  detectedMicroZoneCandidates: Candidate[]

  detectedObjects: DetectedObject[]
  objectCategories: DetectedCategory[]
  detectedSurfaces: SurfaceObservation[]
  storageSystems: StorageObservation[]

  clutterIndicators: Indicator[]
  cleanlinessIndicators: Indicator[]
  organizationIndicators: Indicator[]
  standardizationIndicators: Indicator[]
  maintenanceIndicators: Indicator[]
  safetyIndicators: Indicator[]

  possibleConstraints: Indicator[]

  observations: Observation[]

  imageQuality: {
    sufficient: boolean
    problems: string[]
    additionalPhotoSuggestions: string[]
  }
}
```

## OBSERVATION CONTRACT

Every observation must include:

```ts
{
  description: string
  confidence: number
  evidence: string[]
  sourceImageIds: string[]
  observationType: string
}
```

## NEVER RELY ON VISION TO DETERMINE

Without user verification, avoid asserting:

- exact chemical identity when labels cannot be read
- structural integrity
- electrical safety
- mold
- hazardous materials
- contamination
- disease risk
- ownership
- item value
- whether an item should be discarded

Generate a verification question where necessary.

## DELIVERABLES

Implement:

- upload API
- image storage adapter
- normalization pipeline
- processing job model
- provider-independent vision interface
- structured output validation
- retry behavior
- idempotency
- error handling
- observability
- tests for malformed and low-quality images
