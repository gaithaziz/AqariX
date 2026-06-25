# Product Requirements Document

## Product Name

AqariX

## Product Summary

AqariX is a supervised AI real estate marketplace and CRM for Jordan. It combines property discovery, valuation, forecasting, buyer/investor matching, seller/dealer CRM, managed lead rooms, and AqariX Agency content services.

## Target Market

Initial launch market:

- Jordan, focused first on Amman and Irbid.
- Bounded launch zones should be selected based on available property data, active listings, dealer density, and buyer/investor demand.

## User Roles

### Buyer

Goal: find fairly priced properties and negotiate with better information.

Primary surfaces:

- Home search
- Filters
- Map
- Saved offerings
- Offering analysis
- Lead room
- Buyer dashboard

### Investor

Goal: identify undervalued assets, future locations, and nearby opportunities.

Primary surfaces:

- Investment intake
- Ranked offerings
- Forecast watchlist
- Comparison view
- Portfolio-style dashboard
- Lead room

### Seller

Goal: price correctly, market better, and convert qualified demand.

Primary surfaces:

- Free trial onboarding
- Property setup
- AI pricing assistant
- Marketing assistant
- Basic lead tracking
- Upgrade prompts

### Dealer/Broker

Goal: manage AqariX-originated investor demand and keep investor relationships inside AqariX.

Primary surfaces:

- CRM pipeline
- Listings
- Leads
- Tasks
- Viewing appointments
- Boosts
- Agency orders
- Performance analytics

### AqariX Admin

Goal: protect trust, supervise lead rooms, monitor quality, and improve the marketplace data loop.

Primary surfaces:

- Lead-room supervision
- Quality flags
- User/listing review
- Marketplace KPIs
- Agency queue
- Dispute review

### Agency Operator

Goal: produce seller/dealer content and campaign assets tied to listing performance.

Primary surfaces:

- Agency order board
- Asset checklist
- Production status
- Approval workflow
- Campaign reporting

## Core Product Promise

AqariX should create value before, during, and after buyer/seller contact:

- Before contact: valuation, matching, forecasting, comparable evidence, and opportunity scouting.
- During contact: managed lead rooms, qualification, communication records, viewing coordination, and negotiation support.
- After contact: CRM follow-up, final price capture, conversion analytics, model calibration, and reactivation.

## MVP Scope

### Must Have

- Role-aware authentication and onboarding.
- Buyer/investor intake.
- Search, filters, map, saved offerings, and listing detail.
- AI offering analysis with fair value, listed-price gap, bargain range, confidence, forecast, location momentum, liquidity estimate, and recommendation label.
- Nearby opportunity scout for weak or overpriced offerings.
- Seller/dealer free trial.
- Structured listing creation.
- Seller AI pricing assistant.
- Seller marketing assistant.
- Dealer CRM pipeline for AqariX-originated leads.
- Managed lead room with stages, messages, tasks, appointments, offers, flags, and outcomes.
- Admin dashboard for supervision and quality control.
- Agency package ordering and operator workflow.
- Arabic-first RTL-capable UI.
- Basic analytics, logging, Sentry-style error monitoring, and event tracking.

### Should Have

- Comparison view for up to four offerings.
- Price-drop and opportunity alerts.
- Smart Boosts for compatible buyers/investors.
- Dealer profile.
- Agency performance data attached to listings.
- Model version and evidence trace on AI outputs.

### Post-MVP

- Verified Listing Badge.
- Mortgage and affordability calculator.
- Branded AqariX Score.
- Rental yield calculator.
- Off-plan project tracker.
- Diaspora mode.
- B2B analytics API.

## MVP Success Metrics

Target by Week 36:

- Registered users: 5,000+
- Monthly active users: 1,500+
- AI valuations per month: 2,000+
- Offering analysis views per month: 3,000+
- Lead-room conversion from analysis CTA: 8-12%
- Active seller/dealer accounts: 150+
- Paying dealer/CRM accounts: 25-50
- Agency package attach rate: 5-10% of active sellers/dealers
- AVM MAPE in supported zones: below 12-15%, with confidence shown

## Non-Goals for MVP

- Fully automated legal, financing, or closing workflow.
- Guaranteed investment advice.
- National coverage before zone-level data quality is proven.
- Replacing broker relationships entirely.
- Enterprise CRM parity.
- Fully automated agency content production.

## Product Risks

- Cold-start data quality.
- Overclaiming AI accuracy.
- Off-platform leakage after high-intent contact.
- Broker resistance.
- Agency operations complexity.
- Privacy and compliance risk.
- Forecasting liability.

## Product Guardrail

Every user-facing AI output must be presented as decision support, not certainty. Show confidence, evidence, comparable context, and caveats.
