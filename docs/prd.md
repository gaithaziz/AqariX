# Product Requirements Document

## Product Name

AqariX

## Product Summary

AqariX is a supervised AI real estate marketplace and CRM for Jordan. It combines property discovery, valuation, forecasting, behavior-aware buyer/investor matching, seller/dealer CRM, managed lead rooms, and AqariX Agency content services.

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
- Personalized recommendations
- Offering analysis
- Lead room
- Buyer dashboard

### Investor

Goal: identify undervalued assets, future locations, and nearby opportunities.

Primary surfaces:

- Investment intake
- Ranked offerings
- Behavior-aware recommendations
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
- Inside the app: behavior analysis that learns from searches, filters, views, saves, comparisons, map interactions, analysis opens, and lead-room starts to improve listing recommendations.
- After listing review: lightweight user feedback that improves the ad/listing itself and creates anonymized investor-facing notes about listing quality, missing information, and buyer concerns.
- During contact: managed lead rooms, qualification, communication records, viewing coordination, and negotiation support.
- After contact: CRM follow-up, final price capture, conversion analytics, model calibration, and reactivation.

## MVP Scope

### Must Have

- Role-aware authentication and onboarding.
- Buyer/investor intake.
- Search, filters, map, saved offerings, personalized recommendations, and listing detail.
- User behavior tracking for recommendation quality, including listing views, search filters, saves, comparisons, analysis opens, map interactions, lead-room starts, and explicit dismissals.
- End-of-listing feedback prompt to collect user impressions about listing clarity, price trust, photos, missing details, location confidence, and interest level.
- Listing improvement notes generated from aggregated feedback for sellers/dealers and AqariX admins.
- Investor-facing listing notes based on aggregated feedback, such as "users often ask for clearer location details" or "photo quality may limit confidence."
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
- Privacy controls and clear consent language for using in-app behavior to personalize recommendations.

### Should Have

- Comparison view for up to four offerings.
- Price-drop and opportunity alerts.
- "Why recommended" explanations on personalized listing cards.
- Feedback summary on offering detail when enough signals exist.
- User controls to reset, tune, or reduce personalization.
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
- Personalized recommendation click-through and save rate tracked by segment
- Listing feedback submission rate
- Listing improvement note completion rate
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
- Behavioral data misuse or over-personalization.
- Low-quality or biased listing feedback.
- Forecasting liability.

## Product Guardrail

Every user-facing AI output must be presented as decision support, not certainty. Show confidence, evidence, comparable context, and caveats.

Behavior-based recommendations must be transparent, consent-aware, and user-benefiting. Do not use hidden behavioral profiling in ways that reduce trust, unfairly manipulate users, or push incompatible sponsored listings.

Listing feedback must be aggregated before it becomes seller/dealer guidance or investor-facing notes. Do not expose an individual user's feedback identity to sellers, dealers, or other users.
