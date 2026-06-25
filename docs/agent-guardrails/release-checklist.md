# Release Checklist

Run this before deploying or handing off production-ready work.

## Scope

- Change is small enough to review.
- Affected roles and workflows are documented.
- MVP scope or approved expansion is clear.
- Docs were updated if behavior changed.

## Security

- Server-side authorization is implemented.
- Object ownership is checked.
- Secrets are not in code or client bundles.
- Logs do not expose sensitive data.
- Rate limits exist for expensive or public endpoints.
- Duplicate-prone writes have idempotency or duplicate-click protection.
- Uploads, feedback, behavior events, AI calls, and public routes have abuse controls.
- Dependency and secret scans were run where applicable.

## Cost and Performance

- Search, autocomplete, map movement, autosave, and repeated UI events are debounced or throttled.
- Expensive AI, recommendation, comparable, aggregation, geospatial, and report results are cached in backend Redis where freshness allows.
- Large lists and reports are paginated and capped.
- Paid service usage is tracked by endpoint, feature, role, user, or organization where practical.
- Spend alerts and quota limits are configured for production paid services.

## Testing

- Critical happy path tested.
- Empty state tested.
- Error state tested.
- Permission-denied state tested.
- Bad input tested.
- Duplicate action tested.
- Rate-limit, quota, debounce, and idempotency behavior tested where relevant.
- Mobile behavior tested.
- API behavior tested directly where relevant.
- AI output reviewed for confidence and caveats.

## Deployment

- Staging deploy completed.
- Staging smoke tests passed.
- Migrations tested.
- Backups confirmed.
- Rollback path known.
- Monitoring and alerts active.
- Production smoke test plan ready.

## AqariX-Specific

- Managed lead room behavior still works.
- Dealer CRM behavior still works where affected.
- Admin supervision still works where affected.
- Agency workflow still works where affected.
- Arabic/RTL readiness not degraded.
- AI output remains decision support, not guarantee.
