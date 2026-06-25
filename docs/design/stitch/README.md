# Stitch Initial UI Import

Source zip: `source-stitch-aqarix-real-estate-intelligence-dashboard.zip`

Extracted folder:

- `stitch_aqarix_real_estate_intelligence_dashboard/`

## Included Screens

- Home search
- Listing card gallery
- Offering detail
- AI analysis panel
- Property comparison
- Managed lead room
- Seller listing setup
- Dealer CRM dashboard
- Onboarding intake

## Review Summary

What to preserve:

- Institutional real estate intelligence tone.
- Deep teal primary color and amber value highlights.
- Warm neutral canvas.
- Serif headings with utility sans-serif body text.
- Dense but scannable property cards.
- Dealer CRM pipeline layout.
- Listing feedback and investor-confidence direction.

What to adjust during implementation:

- Arabic-first UI and RTL support are mandatory.
- Dark mode is required.
- Icons should use implementation-native icons instead of Material Symbols CDN.
- AI screens should remain UI shells only until the AI teammate owns real services.
- Recommendations and analysis must show explanations/caveats when connected later.
- Raw user feedback must not be exposed to sellers, dealers, or investors.

## Implementation Status

The first React/Vite web shell has been implemented in `apps/web` using the Stitch visual direction. It includes:

- Arabic-first language default with English toggle.
- RTL/LTR direction switching.
- Dark/light mode toggle.
- Search/listing card UI.
- Behavior-aware recommendation context.
- Listing detail and feedback prompt.
- Static analysis shell with no AI integration.
- Managed lead room shell.
- Seller ad-improvement summary.
- Dealer CRM pipeline shell.
