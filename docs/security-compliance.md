# Security and Compliance

## Security Posture

AqariX handles user identity, property data, communications, offers, business leads, and AI-generated decision support. It must be designed as a trust platform from the beginning.

## Core Risks

- Broken access control.
- Lead-room privacy leaks.
- Seller/dealer contact exposure.
- Misuse of AI forecasts.
- Sensitive data in logs.
- Weak admin permissions.
- Off-platform leakage.
- Abuse, spam, scams, and suspicious listings.
- Unverified or misleading property claims.

## Authorization Rules

- Every API route must check authentication unless explicitly public.
- Every object access must check ownership, organization membership, room participation, or admin permission.
- Admin permissions should be scoped by role.
- Dealer users should only access leads/listings connected to their organization.
- Lead-room participants should only see room data they are allowed to see.
- Contact details must follow qualification and reveal rules.

## Data Privacy

- Collect only data needed for matching, valuation, CRM, and operations.
- Use explicit consent for sensitive uses of lead-room data.
- Keep message retention policy documented.
- Protect phone numbers, emails, offer amounts, and user notes.
- Do not log secrets, tokens, passwords, private messages, or sensitive user profile data.

## AI Compliance and Disclaimers

AI outputs must be framed as decision support.

Required disclaimers:

- Valuations are estimates, not guaranteed sale prices.
- Forecasts are scenarios, not guaranteed appreciation.
- Recommendations are not legal, financial, or investment advice.
- Users should consult qualified professionals for legal, financing, or transaction decisions.

## Trust and Safety Controls

- Listing verification status.
- Suspicious pricing flags.
- Spam and abuse reporting.
- Off-platform leakage detection.
- Dispute review process.
- Admin review for high-risk communications.
- Audit logs for admin actions.

## Technical Security Checklist

- Store secrets outside code.
- Use HTTPS everywhere.
- Use secure session settings.
- Validate input server-side.
- Use ORM-safe or parameterized queries.
- Rate-limit auth, search, uploads, AI analysis, and public endpoints.
- Scan dependencies.
- Scan commits for secrets.
- Use restrictive CORS.
- Add file upload validation.
- Add structured audit events.

## Compliance To Review Before Launch

- Jordanian data protection requirements.
- Real estate advertising requirements.
- Broker/dealer legal positioning.
- Consumer protection requirements.
- Terms for AI-generated valuations and forecasts.
- Consent and retention rules for lead-room communications.

## Security Guardrail

Never rely on frontend-only checks for business rules, role access, pricing, contact reveal, or lead-room permissions.
