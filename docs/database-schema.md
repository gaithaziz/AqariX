# Database Schema

Approved MVP database: PostgreSQL with PostGIS. Use PostgreSQL/pgvector for initial vector matching unless scale or latency proves a separate vector database is needed.

This is an initial logical schema for MVP planning. Field names and types should be finalized during implementation.

## Entity Relationship Summary

- `users` have one or more `user_roles`.
- `organizations` represent dealer offices, developer accounts, and agency teams.
- `properties` describe real-world real estate assets.
- `listings` are marketplace offerings attached to properties.
- `offering_analyses` store AI valuation, forecast, and recommendation outputs for listings.
- `buyer_investor_profiles` store intake data and matching preferences.
- `user_behavior_events` store in-app behavior used to improve recommendations.
- `listing_feedback` stores user feedback captured after listing review.
- `listing_feedback_summaries` store aggregated ad-improvement and investor-facing notes.
- `recommendation_snapshots` store personalized recommendation results and explanations.
- `saved_offerings` and `saved_searches` support discovery workflows.
- `lead_rooms` connect buyer/investor users with seller/dealer users around a listing.
- `lead_room_events`, `messages`, `tasks`, `appointments`, and `offers` track the managed workflow.
- `dealer_crm_entries` support pipeline management.
- `agency_orders` and `agency_assets` support AqariX Agency.
- `admin_flags` support trust and safety review.

## Core Tables

### users

- `id` UUID primary key
- `email` text unique
- `phone` text nullable
- `full_name` text
- `preferred_language` text default `ar`
- `created_at` timestamp
- `updated_at` timestamp
- `last_login_at` timestamp nullable
- `status` text

### user_roles

- `id` UUID primary key
- `user_id` UUID references `users.id`
- `role` text
- `organization_id` UUID nullable references `organizations.id`
- `created_at` timestamp

Allowed roles:

- `buyer`
- `investor`
- `seller`
- `dealer`
- `admin`
- `agency_operator`

### organizations

- `id` UUID primary key
- `name` text
- `type` text
- `city` text nullable
- `phone` text nullable
- `verification_status` text
- `created_at` timestamp
- `updated_at` timestamp

Organization types:

- `dealer_office`
- `developer`
- `agency_team`
- `internal`

### buyer_investor_profiles

- `id` UUID primary key
- `user_id` UUID references `users.id`
- `budget_min_jod` numeric nullable
- `budget_max_jod` numeric nullable
- `preferred_cities` text array
- `preferred_neighborhoods` text array
- `property_types` text array
- `purpose` text
- `risk_tolerance` text
- `investment_horizon_years` integer nullable
- `cash_or_financing` text nullable
- `expected_rental_use` boolean
- `family_lifestyle_needs` jsonb
- `created_at` timestamp
- `updated_at` timestamp

### properties

- `id` UUID primary key
- `city` text
- `neighborhood` text
- `address_text` text nullable
- `location` geography(Point, 4326)
- `property_type` text
- `area_sqm` numeric
- `bedrooms` integer nullable
- `bathrooms` integer nullable
- `floor` integer nullable
- `building_age_years` integer nullable
- `condition` text nullable
- `view_quality` text nullable
- `amenities` text array
- `verification_status` text
- `created_at` timestamp
- `updated_at` timestamp

Recommended indexes:

- GiST index on `location`
- B-tree indexes on `city`, `neighborhood`, `property_type`
- Composite index on `city`, `property_type`, `area_sqm`

### listings

- `id` UUID primary key
- `property_id` UUID references `properties.id`
- `seller_user_id` UUID nullable references `users.id`
- `dealer_org_id` UUID nullable references `organizations.id`
- `title` text
- `description` text
- `asking_price_jod` numeric
- `currency` text default `JOD`
- `status` text
- `listing_quality_score` numeric nullable
- `is_verified` boolean default false
- `is_sponsored` boolean default false
- `published_at` timestamp nullable
- `created_at` timestamp
- `updated_at` timestamp

Allowed listing statuses:

- `draft`
- `pending_review`
- `active`
- `paused`
- `under_offer`
- `closed`
- `rejected`
- `archived`

### listing_media

- `id` UUID primary key
- `listing_id` UUID references `listings.id`
- `media_type` text
- `url` text
- `sort_order` integer
- `quality_flags` jsonb
- `created_at` timestamp

### offering_analyses

- `id` UUID primary key
- `listing_id` UUID references `listings.id`
- `requested_by_user_id` UUID nullable references `users.id`
- `fair_value_jod` numeric
- `fair_value_confidence` text
- `listed_price_gap_pct` numeric
- `bargain_min_jod` numeric nullable
- `bargain_max_jod` numeric nullable
- `forecast_horizon_years` integer
- `forecast_conservative_jod` numeric nullable
- `forecast_base_jod` numeric nullable
- `forecast_optimistic_jod` numeric nullable
- `location_momentum_score` numeric nullable
- `liquidity_score` numeric nullable
- `recommendation_label` text
- `explanation` jsonb
- `model_version` text
- `evidence_sources` jsonb
- `created_at` timestamp

### comparable_properties

- `id` UUID primary key
- `analysis_id` UUID references `offering_analyses.id`
- `property_id` UUID nullable references `properties.id`
- `listing_id` UUID nullable references `listings.id`
- `similarity_score` numeric
- `price_jod` numeric nullable
- `price_per_sqm_jod` numeric nullable
- `distance_meters` numeric nullable
- `source_type` text
- `created_at` timestamp

### saved_offerings

- `id` UUID primary key
- `user_id` UUID references `users.id`
- `listing_id` UUID references `listings.id`
- `notes` text nullable
- `created_at` timestamp

### saved_searches

- `id` UUID primary key
- `user_id` UUID references `users.id`
- `name` text
- `filters` jsonb
- `alert_enabled` boolean default false
- `created_at` timestamp
- `updated_at` timestamp

### user_behavior_events

- `id` UUID primary key
- `user_id` UUID nullable references `users.id`
- `session_id` text nullable
- `event_type` text
- `listing_id` UUID nullable references `listings.id`
- `property_id` UUID nullable references `properties.id`
- `lead_room_id` UUID nullable references `lead_rooms.id`
- `search_filters` jsonb nullable
- `map_bounds` jsonb nullable
- `event_weight` numeric nullable
- `metadata` jsonb
- `created_at` timestamp

Tracked event types:

- `search_performed`
- `filter_applied`
- `map_area_viewed`
- `listing_viewed`
- `listing_saved`
- `listing_unsaved`
- `listing_compared`
- `analysis_opened`
- `nearby_opportunity_clicked`
- `lead_room_started`
- `listing_dismissed`
- `recommendation_clicked`
- `listing_feedback_prompt_shown`
- `listing_feedback_submitted`

Recommended indexes:

- B-tree index on `user_id`, `created_at`
- B-tree index on `event_type`, `created_at`
- B-tree index on `listing_id`, `created_at`

### recommendation_snapshots

- `id` UUID primary key
- `user_id` UUID references `users.id`
- `listing_id` UUID references `listings.id`
- `rank_position` integer
- `recommendation_score` numeric
- `source` text
- `reason_codes` text array
- `explanation` text nullable
- `model_version` text nullable
- `created_at` timestamp

Allowed sources:

- `intake_match`
- `behavior_match`
- `nearby_opportunity`
- `saved_search_alert`
- `sponsored_compatible`

### listing_feedback

- `id` UUID primary key
- `listing_id` UUID references `listings.id`
- `user_id` UUID nullable references `users.id`
- `session_id` text nullable
- `clarity_rating` integer nullable
- `photo_quality_rating` integer nullable
- `price_trust_rating` integer nullable
- `location_confidence_rating` integer nullable
- `interest_level` text nullable
- `missing_information` text array
- `free_text` text nullable
- `created_at` timestamp

Allowed interest levels:

- `not_interested`
- `watching`
- `interested`
- `high_intent`

Common missing information tags:

- `exact_location`
- `better_photos`
- `floor_plan`
- `building_age`
- `ownership_verification`
- `nearby_services`
- `fees_or_taxes`
- `rental_yield`
- `negotiability`

### listing_feedback_summaries

- `id` UUID primary key
- `listing_id` UUID references `listings.id`
- `feedback_count` integer
- `average_clarity_rating` numeric nullable
- `average_photo_quality_rating` numeric nullable
- `average_price_trust_rating` numeric nullable
- `average_location_confidence_rating` numeric nullable
- `top_missing_information` text array
- `seller_improvement_notes` text array
- `investor_note` text nullable
- `generated_at` timestamp
- `model_version` text nullable

Rules:

- Create investor-facing notes only after a minimum feedback threshold.
- Keep raw feedback private to AqariX operations unless policy explicitly allows otherwise.
- Seller/dealer notes should focus on improving the ad, not identifying users.

## Managed Lead Room Tables

### lead_rooms

- `id` UUID primary key
- `listing_id` UUID references `listings.id`
- `buyer_user_id` UUID references `users.id`
- `seller_user_id` UUID nullable references `users.id`
- `dealer_org_id` UUID nullable references `organizations.id`
- `stage` text
- `qualification_status` text
- `contact_reveal_status` text
- `admin_owner_id` UUID nullable references `users.id`
- `created_at` timestamp
- `updated_at` timestamp
- `closed_at` timestamp nullable
- `outcome` text nullable

Lead room stages:

- `new_inquiry`
- `qualified`
- `viewing_scheduled`
- `offer_made`
- `negotiation`
- `closing_support`
- `closed`
- `archived`

### lead_room_messages

- `id` UUID primary key
- `lead_room_id` UUID references `lead_rooms.id`
- `sender_user_id` UUID references `users.id`
- `message_type` text
- `body` text
- `metadata` jsonb
- `created_at` timestamp

### lead_room_tasks

- `id` UUID primary key
- `lead_room_id` UUID references `lead_rooms.id`
- `assigned_to_user_id` UUID nullable references `users.id`
- `task_type` text
- `title` text
- `due_at` timestamp nullable
- `status` text
- `created_at` timestamp
- `updated_at` timestamp

### appointments

- `id` UUID primary key
- `lead_room_id` UUID references `lead_rooms.id`
- `scheduled_at` timestamp
- `location_note` text nullable
- `status` text
- `attendance_confirmed` boolean nullable
- `created_at` timestamp
- `updated_at` timestamp

### offers

- `id` UUID primary key
- `lead_room_id` UUID references `lead_rooms.id`
- `offered_by_user_id` UUID references `users.id`
- `amount_jod` numeric
- `reasoning` text nullable
- `status` text
- `created_at` timestamp

## CRM Tables

### dealer_crm_entries

- `id` UUID primary key
- `dealer_org_id` UUID references `organizations.id`
- `lead_room_id` UUID references `lead_rooms.id`
- `pipeline_stage` text
- `next_action` text nullable
- `next_action_at` timestamp nullable
- `notes` text nullable
- `pipeline_value_jod` numeric nullable
- `created_at` timestamp
- `updated_at` timestamp

### seller_trials

- `id` UUID primary key
- `user_id` UUID references `users.id`
- `organization_id` UUID nullable references `organizations.id`
- `trial_started_at` timestamp
- `trial_ends_at` timestamp
- `listing_limit` integer
- `assistant_usage_limit` integer
- `assistant_usage_count` integer default 0
- `upgrade_status` text
- `created_at` timestamp

## Agency Tables

### agency_packages

- `id` UUID primary key
- `name` text
- `target_role` text
- `description` text
- `base_price_jod` numeric nullable
- `is_active` boolean

### agency_orders

- `id` UUID primary key
- `package_id` UUID references `agency_packages.id`
- `listing_id` UUID nullable references `listings.id`
- `dealer_org_id` UUID nullable references `organizations.id`
- `ordered_by_user_id` UUID references `users.id`
- `assigned_operator_id` UUID nullable references `users.id`
- `status` text
- `desired_audience` text nullable
- `media_requirements` jsonb
- `delivery_due_at` timestamp nullable
- `created_at` timestamp
- `updated_at` timestamp

### agency_assets

- `id` UUID primary key
- `agency_order_id` UUID references `agency_orders.id`
- `asset_type` text
- `url` text nullable
- `copy_text` text nullable
- `approval_status` text
- `created_at` timestamp
- `updated_at` timestamp

## Trust, Analytics, and Audit

### admin_flags

- `id` UUID primary key
- `entity_type` text
- `entity_id` UUID
- `flag_type` text
- `severity` text
- `status` text
- `notes` text nullable
- `created_by_user_id` UUID nullable references `users.id`
- `created_at` timestamp
- `resolved_at` timestamp nullable

### audit_events

- `id` UUID primary key
- `actor_user_id` UUID nullable references `users.id`
- `event_type` text
- `entity_type` text
- `entity_id` UUID nullable
- `metadata` jsonb
- `created_at` timestamp

### analytics_events

- `id` UUID primary key
- `user_id` UUID nullable references `users.id`
- `event_name` text
- `properties` jsonb
- `created_at` timestamp

## Schema Guardrails

- Every user-owned record must have an ownership path.
- Every lead-room object must be scoped to room participants and authorized admins.
- Behavior events must be scoped to the owning user and must not expose one user's behavior to another user.
- Recommendation snapshots must store enough reason codes to support "why recommended" explanations.
- Listing feedback must be aggregated before seller/dealer or investor display.
- Store AI output snapshots; do not recompute history silently.
- Use `jsonb` for flexible evidence/explanation data, but avoid hiding core query fields inside JSON.
- Add indexes before public launch for common search, map, CRM, and lead-room queries.
