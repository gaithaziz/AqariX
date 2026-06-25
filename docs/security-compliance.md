# Security and Compliance

## Security Posture

AqariX handles user identity, property data, communications, offers, business leads, and AI-generated decision support. It must be designed as a trust platform from the beginning.

## Core Risks

- Broken access control.
- Lead-room privacy leaks.
- Seller/dealer contact exposure.
- Misuse of AI forecasts.
- Behavioral data misuse or hidden profiling.
- Misuse of listing feedback or exposing individual feedback to sellers/dealers.
- Sensitive data in logs.
- Weak admin permissions.
- Off-platform leakage.
- Abuse, spam, scams, and suspicious listings.
- Cost-amplification abuse through repeated search, upload, feedback, AI, behavior-event, or public API calls.
- Unverified or misleading property claims.

## Authorization Rules

- Every API route must check authentication unless explicitly public.
- Every object access must check ownership, organization membership, room participation, or admin permission.
- Admin permissions should be scoped by role.
- Dealer users should only access leads/listings connected to their organization.
- Lead-room participants should only see room data they are allowed to see.
- Contact details must follow qualification and reveal rules.
- Quotas, rate limits, and duplicate-action protections must be enforced server-side, not only in the UI.

## Data Privacy

- Collect only data needed for matching, valuation, CRM, and operations.
- Collect in-app behavior only for clear product purposes: recommendations, analytics, fraud/abuse prevention, and product improvement.
- Explain that behavior such as searches, filters, listing views, saves, comparisons, analysis opens, and lead-room starts may improve recommendations.
- Explain that optional listing feedback may be used to improve ads/listings and create aggregated investor-facing notes.
- Provide a practical path to reset or reduce personalization when feasible.
- Use explicit consent for sensitive uses of lead-room data.
- Keep message retention policy documented.
- Protect phone numbers, emails, offer amounts, and user notes.
- Treat behavioral data as private user data.
- Treat raw listing feedback as private user data.
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
- Rate limits and quotas for auth, search, uploads, feedback, behavior events, lead-room actions, AI analysis, assistants, webhooks, and public endpoints.
- Idempotency keys or duplicate-action guards for lead-room creation, offers, agency orders, uploads, and payment-like actions.
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
- Rate-limit behavior events, listing feedback, lead-room messages/actions, assistants, webhooks, and high-volume admin/reporting endpoints.
- Debounce or throttle client-triggered search, autocomplete, map queries, autosave, and behavior-event submission.
- Add idempotency keys for duplicate-prone writes.
- Cap request payload size, result size, upload size, and AI prompt/output size.
- Cache expensive reads and generated outputs in backend Redis where freshness allows.
- Track usage for paid services and alert on abnormal spikes.
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
- Consent, retention, deletion, and user controls for behavioral personalization data.
- Aggregation thresholds and moderation rules for listing feedback notes.

## Security Guardrail

Never rely on frontend-only checks for business rules, role access, pricing, contact reveal, or lead-room permissions.
