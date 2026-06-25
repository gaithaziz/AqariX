# Vibe-Coding Mistakes Summary for AqariX Agents

Full research: [../../vibe-coding-mistakes-research.md](../../vibe-coding-mistakes-research.md)

## Core Mistakes to Avoid

### 1. Treating a Prototype as Production

Do not ship because the demo path works. AqariX needs auth, data ownership, backups, monitoring, support, and recovery.

### 2. Skipping User and Market Validation

Do not assume a generated feature is useful. Validate buyer, investor, seller, dealer, admin, and agency workflows with real or representative users.

### 3. Prompting Vaguely

Do not ask for broad changes without context. Include role, workflow, data, constraints, acceptance criteria, and non-goals.

### 4. Trusting the Frontend

Do not put business rules only in the UI. Permissions, pricing, contact reveal, quotas, and lead-room rules belong on the backend.

### 5. Ignoring Security

Do not delay security until launch. AqariX handles identity, property data, lead-room messages, offers, and business relationships.

### 6. Testing Only the Happy Path

Do not click the expected path once and call it done. Test empty, error, permission, mobile, slow network, bad input, duplicate action, and recovery states.

### 7. Adding Features Faster Than Understanding

Do not let AI create a feature pile. Keep scope tied to MVP loops: matched offerings, offering analysis, seller pricing, managed lead rooms, dealer CRM, and agency orders.

### 8. Over-Polishing Too Early

Do not polish screens before the workflow is clear. Validate structure, user language, and state behavior first.

### 9. Accepting AI Output as Authority

Do not trust confident claims. Verify facts, legal/compliance assumptions, API behavior, and model outputs.

### 10. Deploying Without Operational Readiness

Do not release without staging, backups, rollback, monitoring, smoke tests, and ownership of alerts.

## AqariX-Specific Agent Guardrails

- Keep Arabic/RTL readiness in every user-facing design.
- Keep AI output as decision support with confidence and caveats.
- Keep seller/dealer contact reveal behind qualification.
- Keep lead-room outcomes structured for model calibration.
- Keep dealer CRM useful enough to reduce off-platform leakage.
- Keep agency workflows simple enough to operate manually at MVP.
