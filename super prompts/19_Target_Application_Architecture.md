# Prompt 19 — Target Application Architecture

## OBJECTIVE

Keep the application architecture aligned with the intended 6S Success knowledge-engine model.

The architecture should conceptually separate:

```text
┌──────────────────────────────┐
│        User Experience       │
│ Camera • Upload • Quest UI   │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│       Application API        │
│ Auth • Upload • Workflow     │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│      Image Intelligence      │
│ Objects • Zone • Condition   │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│        6S Rule Engine        │
│ Sort • Set • Shine • etc.    │
└──────────────┬───────────────┘
               │
┌──────────────▼───────────────┐
│     Recommendation Engine    │
│ Activities • Priority • Time │
└──────────────┬───────────────┘
               │
       ┌───────┴────────┐
       │                │
┌──────▼───────┐ ┌──────▼────────┐
│ Knowledge    │ │ Personalization│
│ Library      │ │ AI             │
│ Activities   │ │ Contextual text│
│ Supplies     │ │ Decisions      │
│ Standards    │ │ Explanations   │
└──────────────┘ └───────────────┘
```

## KEY ARCHITECTURAL BOUNDARY

Separate:

**What 6S Success knows**

from:

**What the AI sees in this particular photograph.**

The knowledge base should remain stable and reusable.

The photograph provides situational context.

The recommendation engine joins those two worlds.

## DESIRED END STATE

A user should eventually be able to photograph almost any micro-zone in a home and receive a grounded, sequenced, time-boxed 6S plan with:

- likely room and micro-zone
- visible observations
- six-S assessment
- prioritized actions
- supplies to gather
- step-by-step instructions
- safety verification
- Quest options
- before/after verification
- standard-condition capture
- sustain routine

## FINAL ARCHITECTURAL TEST

Before accepting any major feature, ask:

1. Does this add reusable knowledge or duplicate it?
2. Is AI being used for perception/personalization rather than avoidable hard-coded knowledge?
3. Can this work across many rooms and micro-zones?
4. Can the output be tested?
5. Can administrators update the content without code deployment?
6. Can historical analyses remain reproducible?
