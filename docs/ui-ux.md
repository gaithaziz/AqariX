# UI/UX Requirements

## UX Principle

AqariX must feel role-specific. Each user type should see the work they came to do, not a generic listing dashboard.

## Language and Localization

- Arabic-first capability is required from day one.
- RTL layouts must be supported.
- English can be supported, but should not be the only design assumption.
- Currency defaults to JOD.
- Location vocabulary should match Jordanian user expectations.

## Role-Specific First Screens

### Buyer

First screen should prioritize:

- Search
- Map
- Filters
- Matched offerings
- Personalized recommendations with "why recommended"
- Saved listings
- Clear CTA to inspect analysis

### Investor

First screen should prioritize:

- Investment intake completion
- Ranked opportunities
- Behavior-aware recommendations
- Forecast watchlist
- Comparison
- Yield and risk indicators

### Seller

First screen should prioritize:

- Trial status
- Listing setup
- Pricing assistant
- Media checklist
- Lead status
- Upgrade prompts

### Dealer

First screen should prioritize:

- CRM pipeline
- Tasks
- Active leads
- Listing performance
- Boost and agency actions

### Admin

First screen should prioritize:

- Lead-room flags
- Listing quality review
- Marketplace KPIs
- Suspicious behavior
- Agency queue

### Agency Operator

First screen should prioritize:

- Assigned orders
- Due dates
- Asset checklist
- Approval status
- Campaign reporting

## Required UI States

Every major screen must include:

- Loading state
- Empty state
- Error state
- Permission-denied state
- Offline or retry state where relevant
- Success confirmation
- Validation errors

## Key UX Features

### Offering Detail

Must show:

- Listing media
- Price
- Location
- Property facts
- AqariX analysis
- Confidence and caveats
- Comparable evidence
- Nearby alternatives
- Why recommended
- Personalization confidence when relevant
- Aggregated feedback note when enough listing feedback exists
- CTA to save, compare, or start lead room
- End-of-listing feedback prompt

### Recommendation Surfaces

Must show:

- Recommended listing card
- Reason codes such as "matches your budget," "similar to saved listings," "near areas you viewed," or "better value than compared listings"
- Clear dismiss or "not interested" action
- Avoid showing recommendations that violate hard constraints unless clearly labeled as exploratory
- Privacy-friendly language explaining that in-app behavior improves recommendations

### Listing Feedback Prompt

At the end of listing review, ask for lightweight feedback:

- Was this listing clear?
- Were the photos useful?
- Does the price feel trustworthy?
- Is the location information enough?
- What is missing?
- Are you interested, watching, or not interested?

The prompt should be quick, optional, and never block saving, comparing, or starting a lead room.

Use collected feedback to:

- Improve the ad/listing for sellers and dealers.
- Create investor-facing notes when enough users report the same issue.
- Improve recommendation quality.

### Managed Lead Room

Must show:

- Current stage
- Participants
- Messages
- Tasks
- Appointment status
- Offer history
- Next action
- Admin or safety flags where relevant

### Seller Listing Setup

Must show:

- Structured form
- Media checklist
- Required vs optional fields
- AI pricing action
- Listing quality prompts
- User-feedback improvement notes
- Trial/upgrade limits

## Accessibility

- Use semantic components.
- Label all form inputs.
- Preserve visible focus states.
- Ensure sufficient color contrast.
- Do not rely on color alone.
- Ensure keyboard navigation for web portals.
- Avoid tiny touch targets in mobile UI.

## Design Guardrails

- Do not make AqariX look like a generic classified board.
- Do not hide primary actions below decorative content.
- Do not use vague AI labels without explanation.
- Do not present forecast labels without confidence.
- Do not overload listing cards with too many scores.
- Do not use internal jargon in user-facing labels.
- Make trust signals visible but not noisy.
