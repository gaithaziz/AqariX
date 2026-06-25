# AqariX Agent Guardrails

These instructions apply to work inside this folder and should be treated as mandatory context for AqariX agents.

## Always Read

Before implementing or changing AqariX, read:

- [../prd.md](../prd.md)
- [../architecture.md](../architecture.md)
- [../tech-stack.md](../tech-stack.md)
- [../database-schema.md](../database-schema.md)
- [../testing-qa.md](../testing-qa.md)
- [vibe-coding-mistakes-summary.md](./vibe-coding-mistakes-summary.md)
- [preflight-checklist.md](./preflight-checklist.md)

For release or deployment work, also read:

- [../deployment.md](../deployment.md)
- [release-checklist.md](./release-checklist.md)

## Agent Behavior

- Work in small, reviewable changes.
- State the affected role and workflow before changing behavior.
- Keep AqariX role-aware.
- Keep managed lead rooms central.
- Keep AI outputs explainable and caveated.
- Keep authorization server-side.
- Test beyond the happy path.
- Document every meaningful change in the relevant Markdown docs.
- Keep docs consistent when product, API, schema, AI, security, deployment, or testing behavior changes.

## Do Not

- Do not build generic SaaS dashboards that ignore AqariX roles.
- Do not bypass lead-room supervision for serious inquiries.
- Do not expose contact details without qualification logic.
- Do not present valuation or forecast output as certainty.
- Do not rely on frontend-only permission checks.
- Do not add packages, services, or architecture without a reason.
- Do not change the approved tech stack without updating `docs/tech-stack.md` and related docs.
- Do not make broad changes without tests and a rollback path.

## Required Change Template

```text
Change:
Affected role:
Affected workflow:
Data touched:
Authorization impact:
AI impact:
UX states affected:
Testing completed:
Docs updated:
Risks / rollback:
```
