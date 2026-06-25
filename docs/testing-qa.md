# Testing and QA

## Testing Philosophy

Testing AqariX means testing the product, not only the code. The platform must be tested for user clarity, role permissions, data integrity, AI safety, lead-room operations, deployment readiness, and recovery.

## Test Layers

### Product Validation

- Confirm the target user has the problem.
- Test whether buyer/investor analysis changes decisions.
- Test whether sellers understand pricing guidance.
- Test whether dealers see CRM value.
- Test whether agency packages feel worth paying for.

### Usability Testing

Test with real or representative users:

- Buyer searches and starts a lead room.
- Investor compares opportunities.
- Seller creates listing and uses pricing assistant.
- Dealer manages CRM follow-up.
- Admin reviews a flagged lead room.
- Agency operator completes an order.

Observe:

- Confusing labels.
- Missed CTAs.
- Trust concerns.
- Mobile layout issues.
- Overload in AI explanation.

### Functional Testing

Critical flows:

- Signup/login and role selection.
- Buyer/investor intake.
- Listing search and filtering.
- Personalized recommendations.
- Listing feedback prompt and submission.
- Offering detail and analysis.
- Save and compare.
- Seller listing creation.
- Pricing assistant.
- Marketing assistant.
- Lead-room creation.
- Lead-room stage transitions.
- Appointment scheduling.
- Offer creation.
- Dealer CRM updates.
- Agency order lifecycle.
- Admin flag review.

For each flow, test:

- Success.
- Empty state.
- Bad input.
- Slow network.
- Duplicate clicks.
- Permission denial.
- Error recovery.

### API and Authorization Testing

- Call endpoints directly without the UI.
- Confirm users cannot access other users' saved offerings.
- Confirm users cannot access other users' behavior events or recommendation snapshots.
- Confirm sellers/dealers cannot access raw individual listing feedback.
- Confirm investors see only aggregated listing feedback notes when thresholds are met.
- Confirm dealers cannot access other dealers' leads.
- Confirm lead-room participants cannot access unrelated rooms.
- Confirm sellers cannot edit listings they do not own.
- Confirm admin-only endpoints reject non-admins.
- Confirm contact reveal follows business rules.

### Database Testing

- Test migrations on staging data.
- Test geospatial queries.
- Test large listing lists.
- Test duplicate properties.
- Test missing optional fields.
- Test long Arabic text and RTL data.
- Test old archived records.
- Test concurrent lead-room and offer updates.
- Test behavior event volume and retention.
- Test listing feedback aggregation thresholds.
- Test listing feedback with missing, abusive, low-quality, and conflicting input.
- Test recommendation snapshots with missing, stale, and conflicting behavior data.

### AI Testing

- Compare AVM output against known comparable examples.
- Track MAPE by zone and property type.
- Verify confidence drops for weak data.
- Verify forecasts include caveats.
- Verify no output guarantees appreciation.
- Verify behavior-aware recommendations obey hard constraints.
- Verify "why recommended" explanations are present.
- Verify dismissals and negative signals reduce similar recommendations.
- Verify seller/dealer ad-improvement notes are generated from aggregated feedback.
- Verify investor-facing notes do not expose private user identity or raw feedback.
- Test prompt injection in user-generated listing text.
- Test assistant outputs for sensitive data leakage.
- Test model version tracking.

### Security Testing

- Secret scan.
- Dependency scan.
- Auth/session checks.
- Object-level authorization checks.
- CORS checks.
- Rate-limit checks.
- Quota and duplicate-action/idempotency checks.
- Upload validation.
- Log hygiene.
- Admin audit log checks.

### Performance Testing

- Search response time.
- Map query response time.
- Offering analysis latency.
- Lead-room message latency.
- Dealer CRM dashboard latency.
- Listing image loading.
- Mobile performance.
- Database index coverage.
- AI and vector-search cost.
- Debounce/throttle behavior for search, autocomplete, map movement, autosave, behavior events, and assistant draft generation.
- Redis cache hit behavior for expensive AI, recommendation, comparable, geospatial, aggregation, and report endpoints.

### Deployment Testing

Before production:

- Deploy to staging.
- Run smoke tests.
- Test migrations.
- Confirm environment variables.
- Confirm backups.
- Confirm monitoring.

After production:

- Run production smoke tests.
- Watch error rate and latency.
- Confirm analytics events.
- Confirm lead-room creation.
- Confirm AI analysis works.

### Recovery Testing

- Restore database backup into separate environment.
- Verify app can run from restored data.
- Verify media links and agency assets.
- Verify lead-room history.
- Verify rollback process.

## Minimum Pre-Launch Test Matrix

| Area | Required Test |
| --- | --- |
| Auth | Role selection and protected route checks |
| Marketplace | Search, filters, map, listing detail, listing feedback |
| AI | Valuation, confidence, caveats, comparable evidence, behavior-aware recommendations |
| Seller | Listing setup, pricing assistant, marketing assistant |
| Dealer | CRM pipeline, tasks, appointments |
| Lead room | Create, message, qualify, schedule, offer, close |
| Admin | Flags, review, supervision |
| Agency | Order, asset, approval, reporting |
| Security | Ownership, secrets, dependencies, uploads |
| Cost/abuse | Rate limits, quotas, debounce, idempotency, Redis cache behavior |
| Deployment | Staging smoke, production smoke, backup restore |

## QA Guardrail

Do not accept "I clicked it once and it worked" as testing. Every critical flow must be tested across success, failure, permissions, data, mobile, and deployment states.
