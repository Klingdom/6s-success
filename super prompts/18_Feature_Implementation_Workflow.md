# Prompt 18 — Feature Implementation Workflow for Claude Code

Use this for every significant feature.

## STEP 1: Understand

Explain:

- user problem
- current system behavior
- desired behavior
- affected components

## STEP 2: Inspect

Read the relevant repository code before writing changes.

Never invent architecture that conflicts with the current codebase.

## STEP 3: Reuse

Identify existing:

- services
- components
- domain models
- schemas
- hooks
- utilities
- prompts
- content blocks
- tests

Reuse before adding.

## STEP 4: Design

Provide the smallest maintainable architecture that supports the feature.

## STEP 5: Implement

Make changes in logical increments.

## STEP 6: Validate

Run:

- formatting
- linting
- type checks
- unit tests
- integration tests
- relevant end-to-end tests

## STEP 7: Review

Check:

- security
- authorization
- mobile UX
- error handling
- accessibility
- duplicate code
- duplicate domain knowledge
- AI cost
- observability

## STEP 8: Document

Update relevant:

- README
- architectural decision records
- schemas
- domain documentation
- prompt documentation

## STEP 9: Report

Summarize:

- what changed
- files changed
- architectural decisions
- tests executed
- outstanding risks
- recommended next improvement
