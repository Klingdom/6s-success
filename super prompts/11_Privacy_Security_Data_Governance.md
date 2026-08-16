# Prompt 11 — Build Privacy, Security, and Data Governance

## OBJECTIVE

Treat photographs of users' homes as highly sensitive private content.

Implement privacy by design.

## REQUIREMENTS

### Image access

Images are private by default.

Use controlled authenticated retrieval.

### Tenant isolation

Households and users must never access another household's assets.

### Authorization

Enforce authorization server-side.

Never rely solely on hidden UI.

### Metadata

Strip unnecessary EXIF metadata, especially geolocation metadata.

### Deletion

Allow:

- delete photo
- delete analysis
- delete micro-zone history
- delete household
- delete account

Define what happens to derived records.

### AI providers

Document:

- what content is transmitted
- which model
- what is stored
- retention configuration
- failure handling

### Logging

Never place image contents or sensitive household details into ordinary application logs.

### Analytics

Prefer event metadata such as:

`analysis_completed`

rather than storing generated household descriptions in analytics tools.

## DELIVERABLES

Implement and document:

- authentication
- authorization
- tenant isolation
- storage policies
- signed media access
- retention
- deletion
- EXIF stripping
- audit logging
- provider-data-flow documentation
- security tests
