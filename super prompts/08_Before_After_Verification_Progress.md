# Prompt 08 — Build Before/After Verification and Progress Tracking

## OBJECTIVE

Measure meaningful improvement without making unreliable computer-vision claims.

When the user uploads an after photograph:

1. perform a new independent analysis
2. compare normalized observations
3. compare 6S opportunities
4. identify likely improvements
5. identify unresolved opportunities
6. allow user correction

## COMPARISON OUTPUT

Include:

- likely completed activities
- visible improvements
- remaining tasks
- new opportunities
- changed safety candidates
- updated 6S scores
- confidence

## NEVER CLAIM

Do not say:

"Your space is 37% cleaner."

unless there is a defensible measurable metric.

Prefer:

- Visible floor obstructions decreased.
- Loose shoes previously visible near the doorway are no longer visible.
- The console surface appears clearer.

## STANDARD CONDITION FEATURE

Allow the user to choose an after image as:

**Make This My Standard**

Store the visual standard and compare future images against it.

## DELIVERABLES

Build:

- BeforeAfterComparison model
- normalized comparison engine
- standard-condition model
- progress history
- visual trend summaries
- user correction path
- tests
