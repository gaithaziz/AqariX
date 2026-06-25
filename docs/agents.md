# AqariX Agent Instructions

Agents working in `docs/` or changing AqariX product behavior must read:

- [agent-guardrails/AGENTS.md](./agent-guardrails/AGENTS.md)
- [agent-guardrails/vibe-coding-mistakes-summary.md](./agent-guardrails/vibe-coding-mistakes-summary.md)
- [../vibe-coding-mistakes-research.md](../vibe-coding-mistakes-research.md)

## Documentation Rule

Document every meaningful change made to AqariX.

At minimum, update the relevant docs when a change affects:

- Product behavior, requirements, or scope.
- User roles, dashboards, or flows.
- API behavior or contracts.
- Database schema, ownership, or migrations.
- AI outputs, prompts, model behavior, confidence, or explainability.
- Security, permissions, privacy, or compliance.
- Deployment, environments, monitoring, backups, or release steps.
- Testing strategy, QA checklists, or acceptance criteria.

Keep the PRD, architecture, database schema, API spec, testing plan, and agent guardrails consistent with each other.

## Required Handoff Note

Every agent handoff should include:

```text
Changed:
Docs updated:
Tests run:
Risks / follow-up:
```
