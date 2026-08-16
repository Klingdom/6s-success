# Prompt 09 — Build the Admin Content Management System

## OBJECTIVE

Create an internal Content Studio so 6S Success can improve the platform without software deployments.

Administrators should be able to manage:

- rooms
- micro-zones
- archetypes
- object categories
- activity templates
- instruction blocks
- supplies
- organization patterns
- standards
- sustain routines
- safety rules
- scoring rules
- AI prompt versions

## CMS REQUIREMENTS

Support:

- draft
- review
- approved
- deprecated

Support:

- version history
- change notes
- author
- updated timestamp
- preview
- dependency view
- usage count

Prevent deletion of content referenced by historical analyses.

Use deprecation instead.

## CONTENT REUSE VIEW

Provide tools that show:

- This instruction block is used by 47 activity templates.
- This supply is referenced by 126 activities.

This is essential for long-term maintenance.

## DELIVERABLES

Implement:

- admin authorization
- CRUD with versioning
- approval states
- dependency graph
- content preview
- deprecation
- bulk import/export
- search/filter
- usage analysis
- audit trail
- tests
