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

Purpose: match users to compatible offerings.

Inputs:

- Buyer/investor intake
- Behavioral signals
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

Guardrail: sponsored listings should only appear when compatible enough to preserve trust.

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
3. Users interact with offerings.
4. Lead rooms capture inquiry quality, objections, offers, and outcomes.
5. Final prices and loss reasons calibrate models.
6. Admin review corrects disputed or suspicious outputs.

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
- Store model version and output snapshot for auditability.
