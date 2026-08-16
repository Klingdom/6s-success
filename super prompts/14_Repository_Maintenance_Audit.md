# Prompt 14 — Repository Maintenance Super Prompt

Run periodically during development.

## TASK

Perform a comprehensive architectural review of the 6S Success Micro-Zone Intelligence Platform.

Inspect:

- repository structure
- duplicated code
- duplicated content
- database schema
- migrations
- APIs
- AI prompts
- schemas
- activity library
- micro-zone taxonomy
- supply catalog
- recommendation rules
- authorization
- image handling
- tests
- logging
- observability
- technical debt

## IDENTIFY

1. duplicated business logic
2. duplicated 6S content
3. hard-coded taxonomy values
4. hard-coded supply recommendations
5. direct AI calls bypassing shared abstractions
6. inconsistent schemas
7. missing validation
8. poor error handling
9. authorization gaps
10. untested behavior
11. unused components
12. obsolete prompt versions
13. unnecessary model calls
14. excessive AI cost
15. opportunities for deterministic logic

## THEN

Prioritize issues using:

- severity
- user impact
- architectural impact
- security impact
- likelihood
- effort

Fix high-value issues in small, testable increments.

Do not perform a massive rewrite unless clearly necessary.

Run tests after each meaningful change.

Document architectural decisions.

## REPORT

Summarize:

- findings
- fixes made
- tests run
- risks remaining
- next recommended maintenance action
