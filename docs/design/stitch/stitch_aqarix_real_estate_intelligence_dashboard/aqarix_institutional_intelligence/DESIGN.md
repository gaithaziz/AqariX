---
name: AqariX Institutional Intelligence
colors:
  surface: '#fbf9f4'
  surface-dim: '#dbdad5'
  surface-bright: '#fbf9f4'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#f5f3ee'
  surface-container: '#f0eee9'
  surface-container-high: '#eae8e3'
  surface-container-highest: '#e4e2dd'
  on-surface: '#1b1c19'
  on-surface-variant: '#3f4945'
  inverse-surface: '#30312e'
  inverse-on-surface: '#f2f1ec'
  outline: '#707975'
  outline-variant: '#bfc9c4'
  surface-tint: '#29695b'
  primary: '#00342b'
  on-primary: '#ffffff'
  primary-container: '#004d40'
  on-primary-container: '#7ebdac'
  inverse-primary: '#94d3c1'
  secondary: '#795900'
  on-secondary: '#ffffff'
  secondary-container: '#ffbf00'
  on-secondary-container: '#6d5000'
  tertiary: '#202e40'
  on-tertiary: '#ffffff'
  tertiary-container: '#364457'
  on-tertiary-container: '#a3b1c8'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#afefdd'
  primary-fixed-dim: '#94d3c1'
  on-primary-fixed: '#00201a'
  on-primary-fixed-variant: '#065043'
  secondary-fixed: '#ffdfa0'
  secondary-fixed-dim: '#fbbc00'
  on-secondary-fixed: '#261a00'
  on-secondary-fixed-variant: '#5c4300'
  tertiary-fixed: '#d5e3fc'
  tertiary-fixed-dim: '#b9c7df'
  on-tertiary-fixed: '#0d1c2e'
  on-tertiary-fixed-variant: '#3a485b'
  background: '#fbf9f4'
  on-background: '#1b1c19'
  surface-variant: '#e4e2dd'
typography:
  display-lg:
    fontFamily: Noto Serif
    fontSize: 48px
    fontWeight: '700'
    lineHeight: '1.2'
    letterSpacing: -0.02em
  display-lg-mobile:
    fontFamily: Noto Serif
    fontSize: 32px
    fontWeight: '700'
    lineHeight: '1.2'
  headline-md:
    fontFamily: Noto Serif
    fontSize: 24px
    fontWeight: '600'
    lineHeight: '1.4'
  headline-sm:
    fontFamily: Noto Serif
    fontSize: 20px
    fontWeight: '600'
    lineHeight: '1.4'
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: '1.6'
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: '1.6'
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: '1.5'
  label-caps:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: '1'
    letterSpacing: 0.05em
  data-mono:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: '1'
rounded:
  sm: 0.125rem
  DEFAULT: 0.25rem
  md: 0.375rem
  lg: 0.5rem
  xl: 0.75rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 40px
  container-max: 1280px
  gutter: 20px
---

## Brand & Style
The design system is engineered for a sophisticated real estate marketplace where data integrity and institutional trust are paramount. It targets professional investors, developers, and high-net-worth individuals in the Jordanian market, balancing a scholarly heritage with high-velocity AI insights.

The aesthetic follows a **Modern Institutional** approach: a refined intersection of scholarly typography and high-density, functional UI. It avoids trend-driven effects like glassmorphism or vibrant gradients in favor of structural clarity, generous white space (within a dense data context), and a prestigious color palette. The emotional response should be one of "Informed Confidence"—moving away from the "salesy" nature of traditional real estate towards a research-backed, analytical environment.

## Colors
This design system utilizes a palette grounded in authority and value.
- **Deep Teal (#004D40):** Used for primary brand moments, main action buttons, and navigation headers. It conveys stability and institutional scale.
- **Amber (#FFBF00):** Reserved for "Value Highlighting"—price changes, investment yields, and the 'AqariX Score'. It represents opportunity.
- **Warm Neutral (#F9F7F2):** The canvas color. It reduces eye strain during long research sessions compared to pure white and adds a premium, "parchment" quality.
- **Slate Grays:** Used for secondary UI elements and data-dense text to ensure maximum legibility without the harshness of pure black.

## Typography
The typographic strategy uses a "Serif for Authority, Sans for Utility" model. 
- **Noto Serif** provides a scholarly, editorial feel for property titles, section headers, and market reports.
- **Inter** is utilized for all functional UI, inputs, and tabular data. 
- **Tabular Numerals:** For JOD currency and square footage data, always use tabular (monospaced) figures to ensure column alignment in financial tables.
- **RTL Considerations:** Noto Serif and Inter are both optimized for high legibility in Arabic and English, maintaining visual weight across bilingual interfaces.

## Layout & Spacing
This design system employs a **12-column fluid grid** for desktop and a **4-column grid** for mobile. 
- **RTL Logic:** Spacing is defined using logical properties (padding-inline, margin-inline) to automatically mirror for the Jordanian market.
- **Information Density:** The spacing rhythm is tight (8px/16px increments) to allow for the high-density display of financial data, maps, and property attributes without excessive scrolling.
- **Data Tables:** Horizontal padding in data rows is minimized (12px) to maximize the "at-a-glance" visibility of property comparisons.

## Elevation & Depth
Depth is signaled through **Tonal Layers** and **Low-Contrast Outlines** rather than heavy shadows.
- **Level 0 (Base):** Warm Neutral (#F9F7F2).
- **Level 1 (Cards/Surface):** White (#FFFFFF) with a 1px border in Slate-200. No shadow.
- **Level 2 (Interactive):** White (#FFFFFF) with a subtle 4px blur, 4% opacity black shadow to indicate hover states.
- **Separators:** Use 1px solid lines in #E2E8F0 for vertical and horizontal divisions in data-heavy views.

## Shapes
The shape language is conservative and professional. 
- **Primary Elements:** Buttons and Input fields use a 4px (Soft) radius to maintain a structural, architectural feel. 
- **Data Badges:** 'AqariX Score' badges use the same 4px radius but never a full pill-shape, preserving the serious, analytical tone.
- **Images:** Property thumbnails should have a subtle 4px radius to match UI components.

## Components
- **Primary Buttons:** Solid Deep Teal (#004D40) with White text. Sharp corners (4px).
- **AqariX Score Badge:** A distinctive component with a Deep Teal background and Amber (#FFBF00) text or accent bar. The score is displayed in `data-mono` typography.
- **Confidence Level Indicator:** A 3-step segmented bar (Low/Med/High) using Teal tints, avoiding the "stoplight" red/green pattern to maintain neutrality.
- **Currency Inputs:** Prefixed/Suffixed with "JOD" in `label-caps`. Numbers are right-aligned in tabular-nums.
- **Property Cards:** High-density layout. Title in Noto Serif, price in Amber, and key specs (sqm, beds) in Inter with small icons.
- **Data Tables:** Zebra-striping using a 2% tint of Deep Teal on alternate rows to assist horizontal eye-tracking.