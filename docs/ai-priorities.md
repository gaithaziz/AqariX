# AqariX AI: Development Prioritization Roadmap for Irbid Launch

This document defines the implementation roadmap, dependencies, and immediate start points for the AqariX AI engine, focused exclusively on the Irbid micro-market.

---

## 1. Prioritization Roadmap

The development process is structured into three consecutive tiers based on technical dependencies and direct business impact.

### Phase 1: Ingestion & Spatial Foundation (Highest Priority)
This phase is the foundational layer. Without a structured, spatial data repository, downstream models cannot be trained or optimized.
1. **Dialect Ingestion & NLP Normalization**:
   * *Why?* Public real estate listings in Irbid are unstructured and heavily dialect-dependent, containing specific terms from university students and summer expats (e.g., "قريبة من البوابة" - close to the gate, "بداعي السفر" - motivated seller due to travel, "سكن شباب" - student/single housing).
2. **PostGIS & Spatial Infrastructure**:
   * *Why?* Proximity to major landmarks (Yarmouk University, JUST gates, King Abdullah University Hospital, University Street) dictates the pricing gradient in Irbid. A spatial graph is critical to model these relationships.
3. **Classifieds Scraper Orchestrator**:
   * *Why?* Necessary to automatically extract public listings from Facebook groups and local classified sites to bootstrap our baseline listings database.

### Phase 2: Core UX (Medium Priority)
Once structured, location-indexed listings are available, we begin building the core analytics.
1. **Two-Stage Automated Valuation Model (AVM)**:
   * Combines structural parameters (bedrooms, finishes) via LightGBM with spatial residuals adjustment via Graph Convolutional Networks (GCN) to produce highly accurate property valuations.
2. **Multi-Task Computer Vision**:
   * Automatically assesses listing photo quality, flags duplicate fraud, and extracts spec details (e.g., detecting student-friendly studio setups).

### Phase 3: Advanced Intelligence (Long-Term Priority)
Advanced user-facing intelligence and investor-grade predictive planning.
1. **Buyer Intelligence Engine**:
   * Implements dual-encoder vector matching to recommend listings based on user search behavior (e.g., segregating student group rentals from family buyers).
2. **Investor & Developer Predictive Analytics**:
   * Forecasts Irbid's future growth axes (e.g., expansions along the JUST highway corridor or Southern Irbid residential zones) using hybrid time-series modeling.

---

## 2. Where Do We Start? (Immediate Action Plan)

To minimize deployment friction, the development team will follow this sequential path:

### Step 1: Local Dialect NLP Parser (First Coding Step)
* **Goal**: Write the regex and heuristic lookup dictionaries to standardize Arabic real estate text (e.g., mapping "البوابة الشمالية" to specific geographical coordinates and parsing "سكن طلاب").
* **Target File**: `services/api/app/nlp/dialect_parser.py`

### Step 2: Spatial Database Setup (PostGIS)
* **Goal**: Launch the Docker container containing PostgreSQL, PostGIS (geospatial), and pgvector (vector search) extensions.
* **Target Files**: `docker-compose.yml` and `infra/neon/setup.sql`

### Step 3: Classified Scraper Ingestion
* **Goal**: Deploy the public listing scraping jobs to collect real-world data across Irbid districts.
* **Target Folder**: `services/jobs/scraper/`
