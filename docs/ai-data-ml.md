# AI, Data, and ML

## AI Product Philosophy

AqariX should treat AI as an evidence layer, not a decorative chatbot. The AI must improve decision quality, trust, and workflow productivity.

Every important AI output should include:

- Confidence
- Comparable evidence
- Caveats
- Model version
- Data freshness
- Human-readable explanation

## Core AI Modules

### Automated Valuation Model

Purpose: estimate fair market value.

Inputs:

- Property attributes
- Geospatial features
- Comparable listings
- Historical transactions or verified outcomes where available
- Neighborhood and zone data
- Listing quality signals

Outputs:

- Fair value
- Confidence range
- Price per sqm estimate
- Comparable evidence
- Model version

### Forecasting Model

Purpose: estimate 3-to-5-year price direction.

Inputs:

- Regional time series
- Demand signals
- Infrastructure changes
- Nearby POIs
- Comparable area trends
- Rental interest
- Liquidity data

Outputs:

- Conservative scenario
- Base scenario
- Optimistic scenario
- Confidence level
- Explanation and caveats

### Recommendation Engine

Purpose: match users to compatible offerings using both declared preferences and observed in-app behavior.

Inputs:

- Buyer/investor intake
- Behavioral signals from in-app activity
- Budget
- Risk tolerance
- Location preferences
- Property type
- Listing compatibility
- Sponsorship eligibility

Outputs:

- Ranked offerings
- Match reason
- Compatibility score
- Sponsored listing eligibility
- "Why recommended" explanation
- Personalization confidence

Behavioral signals may include:

- Search filters used and changed
- Map areas viewed or revisited
- Listing views
- Dwell time on listing detail and analysis sections
- Saves and unsaves
- Comparisons
- Analysis opens
- Nearby opportunity clicks
- Lead-room starts
- Explicit dismissals or "not interested" actions

Guardrails:

- Sponsored listings should only appear when compatible enough to preserve trust.
- Recommendations must remain explainable enough for users to understand why a listing appeared.
- Do not treat behavior as more important than hard constraints such as budget, city, property type, or risk tolerance.
- Let users reset or tune personalization when practical.

### Offering Assistant

Purpose: explain listing quality and decision support.

Outputs:

- Underpriced/fair/overpriced interpretation
- Bargain range
- Forecast summary
- Location momentum explanation
- Liquidity estimate
- Comparable context
- Nearby alternatives
- Aggregated user feedback notes about listing clarity, missing information, photo quality, price trust, and investor concerns

### Seller Assistant

Purpose: help sellers price and market better.

Outputs:

- Suggested asking price
- Bargain range
- Comparable properties
- Days-on-market risk
- Listing copy
- Photo checklist
- Social captions
- Video script ideas
- Buyer persona recommendations
- Boost suggestions
- Ad/listing improvement notes derived from aggregated user feedback

### CRM Intelligence

Purpose: help dealers manage follow-up and conversion.

Outputs:

- Lead-room summaries
- Next-action recommendations
- Low-quality lead detection
- Conversion blockers
- Follow-up scripts
- Pipeline risk flags

## Data Collection Loop

1. Listings enter the marketplace.
2. AI generates valuation, forecast, and recommendation signals.
3. Users interact with search, maps, listings, analysis, saves, comparisons, and lead rooms.
4. Behavior events update recommendation features and user preference signals.
5. Users submit lightweight listing feedback at the end of listing review.
6. Aggregated feedback creates ad-improvement notes for sellers/dealers and investor-facing listing-quality notes.
7. Lead rooms capture inquiry quality, objections, offers, and outcomes.
8. Final prices and loss reasons calibrate models.
9. Admin review corrects disputed or suspicious outputs.

## Explainability Rules

- Do not show one exact value as the "truth."
- Show confidence bands where possible.
- Explain which factors pushed the score up or down.
- Use conservative language for forecasts.
- Label outputs as decision support, not legal, financial, or investment advice.

## Model Quality Metrics

- AVM MAPE by zone and property type.
- Forecast error by horizon and zone.
- Recommendation click-through and save rate.
- Recommendation-to-analysis-open rate.
- Recommendation-to-lead-room-start rate.
- Dismissal and "not interested" rate.
- Listing feedback submission rate.
- Listing feedback sentiment and completeness score.
- Seller/dealer completion rate for suggested ad improvements.
- Diversity of recommended neighborhoods and property types.
- Hard-constraint violation rate for recommended listings.
- Analysis-to-lead-room conversion.
- Lead quality by recommendation source.
- Dispute rate for valuations.
- Admin override rate.

## Cold-Start Strategy

- Launch in bounded zones.
- Use comparable evidence manually where needed.
- Label low-confidence outputs clearly.
- Collect seller/dealer outcomes from lead rooms.
- Use human review for high-risk or disputed outputs.

## AI Safety Guardrails

- Never guarantee appreciation.
- Never provide legal advice.
- Never expose private user data in generated summaries.
- Never use lead-room content for model training without consent and policy review.
- Do not use sensitive behavioral inferences for targeting without explicit policy review.
- Do not expose individual feedback authors or raw private feedback to sellers, dealers, or investors.
- Use aggregated listing feedback for ad improvement and investor notes only after privacy and quality thresholds are met.
- Do not recommend listings outside hard user constraints unless clearly labeled as exploratory.
- Store model version and output snapshot for auditability.
