# Agent Preflight Checklist

Run this before starting a change.

## Product Context

- Which user role is affected?
- Which workflow is affected?
- Is this in MVP scope?
- Does this preserve the managed lead room model?
- Does this support AqariX as an intelligence/workflow layer rather than a generic listing board?

## Data Context

- Which entities are touched?
- Who owns each record?
- What permissions are required?
- Does the change affect AI output, lead-room history, CRM, or agency operations?

## UX Context

- What is the success state?
- What is the empty state?
- What is the loading state?
- What is the error state?
- What is the permission-denied state?
- Does it work in Arabic/RTL?
- Does it work on mobile?

## Technical Context

- Is there an existing pattern to follow?
- Are new dependencies truly needed?
- Are API changes documented?
- Are schema changes necessary?
- Is there a migration plan?

## Testing Plan

- What unit tests are needed?
- What API/authorization tests are needed?
- What end-to-end or smoke test is needed?
- What manual QA is needed?
- What regression area could break?

## Stop Conditions

Pause before implementation if:

- The role or workflow is unclear.
- The ownership model is unclear.
- The change exposes private contact or message data.
- The change makes AI claims without confidence/caveats.
- The change requires production deployment without rollback.
