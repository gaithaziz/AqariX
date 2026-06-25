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

- Does this follow the approved stack in `docs/tech-stack.md`?
- Does this fit the first vertical slice in `docs/implementation-plan.md`, or is it explicitly deferred?
- Are local and external requirements from `docs/implementation-requirements.md` satisfied?
- Does local service work fit the Docker Compose setup instead of ad hoc per-machine setup?
- Is there an existing pattern to follow?
- Are new dependencies truly needed?
- Are API changes documented?
- Are schema changes necessary?
- Is there a migration plan?

## Security and Abuse Context

- Which endpoints, jobs, or actions need rate limits?
- Which writes need idempotency keys or duplicate-action protection?
- Which objects need ownership, organization, room, or admin authorization checks?
- Which inputs need server-side validation, upload checks, or moderation?
- Could this expose contact details, messages, offers, behavioral events, raw feedback, or private AI inputs?
- Could anonymous or low-trust users abuse this workflow?

## Performance and Cost Context

- Could this fire repeatedly from typing, scrolling, map movement, autosave, retries, duplicate clicks, or re-renders?
- Should the UI debounce or throttle the action?
- Should the backend use Redis cache, paginate, batch, queue, or cap the work?
- Does this call paid APIs, AI models, vector search, maps, email/SMS, storage, or background jobs?
- Are usage metrics, quotas, and spend alerts needed?
- What graceful fallback should users see if limits are reached?

## Testing Plan

- What unit tests are needed?
- What API/authorization tests are needed?
- What rate-limit, quota, idempotency, or duplicate-click tests are needed?
- What debounce/throttle behavior needs testing?
- What end-to-end or smoke test is needed?
- What manual QA is needed?
- What regression area could break?

## Stop Conditions

Pause before implementation if:

- The role or workflow is unclear.
- The ownership model is unclear.
- The change exposes private contact or message data.
- The change makes AI claims without confidence/caveats.
- The change adds an expensive/public action without rate limits, quotas, debounce, caching, pagination, or a deliberate reason.
- The change requires production deployment without rollback.
