# Prompt 10 — Build User Corrections and Human-in-the-Loop Learning

## OBJECTIVE

Make incorrect AI analysis easy to correct.

Users must be able to edit:

- room
- micro-zone
- object identification
- object category
- surface
- activity relevance
- safety condition
- supply recommendation

Useful correction buttons include:

- That's not this room
- Wrong micro-zone
- Wrong object
- I already fixed this
- Not applicable
- I don't own this
- I don't want to change this
- This is intentional
- Show me another solution

Store corrections separately from model outputs.

Never overwrite the original AI result.

Use corrections to improve:

- ranking rules
- taxonomies
- prompt tests
- evaluation datasets

Do not automatically retrain models from individual user data.

## DELIVERABLES

Build:

- UserFeedback model
- correction history
- corrected-state overlay
- feedback analytics
- recommendation rejection reason codes
- eval dataset export
- tests ensuring source AI output remains immutable
