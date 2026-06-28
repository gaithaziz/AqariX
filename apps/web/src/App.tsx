import {
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
  type Dispatch,
  type FormEvent,
  type ReactNode,
  type SetStateAction,
} from 'react'
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  CheckCircle2,
  ChevronRight,
  DoorOpen,
  Eye,
  FileText,
  Home,
  Loader2,
  MapPinned,
  MessageSquareQuote,
  RefreshCw,
  Save,
  Search,
  SlidersHorizontal,
  Sparkles,
  UserRound,
  Wand2,
  type LucideIcon,
} from 'lucide-react'
import './App.css'
import {
  type BaselineValuationResponse,
  type BuyerInvestorProfile,
  type BuyerInvestorProfileIn,
  type LeadRoom,
  type Listing,
  type ListingFeedbackSummary,
  type ParsedListingTextResponse,
  type PropertyType,
  type Recommendation,
  DEFAULT_DEMO_USER_ID,
  estimateBaselineValue,
  getApiBase,
  getStoredDemoUserId,
  loadFeedbackSummary,
  loadListings,
  loadProfile,
  loadRecommendations,
  parseListingText,
  recordBehaviorEvent,
  saveProfile,
  setStoredDemoUserId,
  startLeadRoom,
  submitFeedback,
} from './aqarixApi'

type ListingFilters = {
  city: string
  neighborhood: string
  propertyType: PropertyType | ''
}

type ProfileFormState = {
  budget_min_jod: string
  budget_max_jod: string
  preferred_cities: string
  preferred_neighborhoods: string
  property_types: PropertyType[]
  purpose: string
  risk_tolerance: string
  investment_horizon_years: string
}

type FeedbackFormState = {
  clarity_rating: string
  photo_quality_rating: string
  price_trust_rating: string
  location_confidence_rating: string
  interest_level: string
  missing_information: string
  free_text: string
}

type LeadFormState = {
  intent: string
  budget_fit: string
  preferred_contact_method: string
}

type ActivityItem = {
  id: number
  title: string
  detail: string
  time: string
  tone: 'neutral' | 'positive' | 'warning'
}

const PROPERTY_TYPE_OPTIONS: Array<{ value: PropertyType; label: string }> = [
  { value: 'apartment', label: 'Apartment' },
  { value: 'villa', label: 'Villa' },
  { value: 'land', label: 'Land' },
  { value: 'commercial', label: 'Commercial' },
]

const PURPOSE_OPTIONS = [
  { value: 'buy', label: 'Buy' },
  { value: 'investment', label: 'Investment' },
  { value: 'rent', label: 'Rent' },
]

const RISK_OPTIONS = [
  { value: 'low', label: 'Low' },
  { value: 'medium', label: 'Medium' },
  { value: 'high', label: 'High' },
]

const SEARCH_FIT_OPTIONS = [
  { value: '', label: 'Any type' },
  { value: 'apartment', label: 'Apartment' },
  { value: 'villa', label: 'Villa' },
  { value: 'land', label: 'Land' },
  { value: 'commercial', label: 'Commercial' },
]

const FEEDBACK_INTEREST_OPTIONS = [
  { value: 'interested', label: 'Interested' },
  { value: 'maybe_later', label: 'Maybe later' },
  { value: 'not_interested', label: 'Not interested' },
]

const LEAD_INTENT_OPTIONS = [
  { value: 'viewing', label: 'Viewing' },
  { value: 'investment_followup', label: 'Investment follow-up' },
  { value: 'pricing_review', label: 'Pricing review' },
]

const BUDGET_FIT_OPTIONS = [
  { value: 'inside_budget', label: 'Inside budget' },
  { value: 'stretching_budget', label: 'Stretching budget' },
  { value: 'outside_budget', label: 'Outside budget' },
]

const CONTACT_OPTIONS = [
  { value: 'lead_room', label: 'Lead room' },
  { value: 'whatsapp', label: 'WhatsApp' },
  { value: 'phone', label: 'Phone' },
]

const DEFAULT_SEARCH: ListingFilters = {
  city: '',
  neighborhood: '',
  propertyType: '',
}

const DEFAULT_PROFILE_FORM: ProfileFormState = {
  budget_min_jod: '',
  budget_max_jod: '',
  preferred_cities: '',
  preferred_neighborhoods: '',
  property_types: [],
  purpose: 'buy',
  risk_tolerance: 'medium',
  investment_horizon_years: '',
}

const DEFAULT_FEEDBACK_FORM: FeedbackFormState = {
  clarity_rating: '',
  photo_quality_rating: '',
  price_trust_rating: '',
  location_confidence_rating: '',
  interest_level: '',
  missing_information: '',
  free_text: '',
}

const DEFAULT_LEAD_FORM: LeadFormState = {
  intent: 'viewing',
  budget_fit: 'inside_budget',
  preferred_contact_method: 'lead_room',
}

const DEFAULT_PARSE_SAMPLE =
  'شقة مفروشة للايجار في اربد قريبة من البوابة الشمالية، سكن طلاب، غرفتين و حمام 1، المساحة 90 متر، السعر 250 دينار'

const DEFAULT_VALUATION_SAMPLE =
  'ارض للبيع في الحصن مساحة 2 دونم السعر 70 الف دينار قابل للتفاوض'

function App() {
  const [apiState, setApiState] = useState<'loading' | 'ready' | 'error'>('loading')
  const [apiError, setApiError] = useState<string | null>(null)
  const [demoUserDraft, setDemoUserDraft] = useState(() => getStoredDemoUserId())
  const [demoUserId, setDemoUserId] = useState(() => getStoredDemoUserId())
  const [profile, setProfile] = useState<BuyerInvestorProfile | null>(null)
  const [profileForm, setProfileForm] = useState<ProfileFormState>(DEFAULT_PROFILE_FORM)
  const [searchForm, setSearchForm] = useState<ListingFilters>(DEFAULT_SEARCH)
  const [appliedFilters, setAppliedFilters] = useState<ListingFilters>(DEFAULT_SEARCH)
  const [listings, setListings] = useState<Listing[]>([])
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])
  const [selectedListingId, setSelectedListingId] = useState<string | null>(null)
  const [feedbackSummary, setFeedbackSummary] = useState<ListingFeedbackSummary | null>(null)
  const [feedbackForm, setFeedbackForm] = useState<FeedbackFormState>(DEFAULT_FEEDBACK_FORM)
  const [leadForm, setLeadForm] = useState<LeadFormState>(DEFAULT_LEAD_FORM)
  const [leadRoom, setLeadRoom] = useState<LeadRoom | null>(null)
  const [parseText, setParseText] = useState(DEFAULT_PARSE_SAMPLE)
  const [valuationText, setValuationText] = useState(DEFAULT_VALUATION_SAMPLE)
  const [parsedResult, setParsedResult] = useState<ParsedListingTextResponse | null>(null)
  const [valuationResult, setValuationResult] = useState<BaselineValuationResponse | null>(null)
  const [loadingBootstrap, setLoadingBootstrap] = useState(false)
  const [loadingSearch, setLoadingSearch] = useState(false)
  const [savingProfile, setSavingProfile] = useState(false)
  const [savingFeedback, setSavingFeedback] = useState(false)
  const [savingLeadRoom, setSavingLeadRoom] = useState(false)
  const [parsingText, setParsingText] = useState(false)
  const [estimatingValue, setEstimatingValue] = useState(false)
  const [activity, setActivity] = useState<ActivityItem[]>([])
  const appliedFiltersRef = useRef(appliedFilters)

  const selectedListing = useMemo(
    () => listings.find((item) => item.id === selectedListingId) ?? null,
    [listings, selectedListingId],
  )

  const activeFiltersLabel = useMemo(() => {
    const labels: string[] = []

    if (appliedFilters.city) {
      labels.push(appliedFilters.city)
    }
    if (appliedFilters.neighborhood) {
      labels.push(appliedFilters.neighborhood)
    }
    if (appliedFilters.propertyType) {
      labels.push(appliedFilters.propertyType)
    }

    return labels.length ? labels.join(' · ') : 'All listings'
  }, [appliedFilters])

  const topRecommendation = recommendations[0] ?? null

  const summaryCards = useMemo(
    () => [
      {
        label: 'Listings',
        value: listings.length.toString(),
        hint: activeFiltersLabel,
        icon: Home,
      },
      {
        label: 'Top match',
        value: topRecommendation ? formatScore(topRecommendation.recommendation_score) : '—',
        hint: topRecommendation?.listing.title ?? 'No recommendation yet',
        icon: Sparkles,
      },
      {
        label: 'Feedback notes',
        value: feedbackSummary?.feedback_count.toString() ?? '0',
        hint:
          feedbackSummary?.top_missing_information.length
            ? feedbackSummary.top_missing_information.join(' · ')
            : 'Waiting on a selected listing',
        icon: MessageSquareQuote,
      },
      {
        label: 'Lead room',
        value: leadRoom?.stage ?? 'Not started',
        hint: selectedListing ? selectedListing.title : 'Pick a listing first',
        icon: DoorOpen,
      },
      {
        label: 'Profile',
        value: profile ? 'Saved' : 'Draft',
        hint: profile?.purpose ?? 'No intake saved yet',
        icon: UserRound,
      },
    ],
    [activeFiltersLabel, feedbackSummary, leadRoom, listings.length, profile, selectedListing, topRecommendation],
  )

  const bootstrap = useCallback(
    async (filters: ListingFilters) => {
      setLoadingBootstrap(true)
      setApiError(null)

      try {
        const [loadedProfile, loadedListings, loadedRecommendations] = await Promise.all([
          loadProfile(),
          loadListings(filters),
          loadRecommendations(),
        ])

        setProfile(loadedProfile)
        setProfileForm(profileToForm(loadedProfile))
        setListings(loadedListings.items)
        setRecommendations(loadedRecommendations)
        setAppliedFilters(filters)
        setApiState('ready')
        addActivity(
          setActivity,
          'Dashboard synced',
          `${loadedListings.total} listings loaded with the live backend.`,
          'positive',
        )
      } catch (error) {
        setApiState('error')
        setApiError(errorMessage(error))
        addActivity(setActivity, 'Sync failed', errorMessage(error), 'warning')
      } finally {
        setLoadingBootstrap(false)
      }
    },
    [],
  )

  const refreshRecommendations = useCallback(async () => {
    try {
      const loadedRecommendations = await loadRecommendations()
      setRecommendations(loadedRecommendations)
    } catch (error) {
      setApiError(errorMessage(error))
    }
  }, [])

  useEffect(() => {
    appliedFiltersRef.current = appliedFilters
  }, [appliedFilters])

  useEffect(() => {
    setStoredDemoUserId(demoUserId)
    void bootstrap(appliedFiltersRef.current)
  }, [bootstrap, demoUserId])

  useEffect(() => {
    if (!listings.length) {
      setSelectedListingId(null)
      return
    }

    const isCurrentSelectionValid = listings.some((item) => item.id === selectedListingId)
    if (!isCurrentSelectionValid) {
      setSelectedListingId(listings[0].id)
    }
  }, [listings, selectedListingId])

  useEffect(() => {
    if (!selectedListingId) {
      setFeedbackSummary(null)
      return
    }

    void loadFeedbackSummary(selectedListingId)
      .then((summary) => setFeedbackSummary(summary))
      .catch((error) => setApiError(errorMessage(error)))
  }, [selectedListingId])

  useEffect(() => {
    if (!selectedListing) {
      return
    }

    setLeadForm((current) => ({
      ...current,
      intent: profile?.purpose === 'investment' ? 'investment_followup' : 'viewing',
      budget_fit: deriveBudgetFit(selectedListing, profile?.budget_max_jod ?? null),
    }))
  }, [profile?.budget_max_jod, profile?.purpose, selectedListing])

  const handleDemoUserConnect = (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    const next = setStoredDemoUserId(demoUserDraft)
    setDemoUserId(next)
    addActivity(setActivity, 'Connected demo user', next, 'neutral')
  }

  const handleRefreshAll = () => {
    void bootstrap(appliedFiltersRef.current)
  }

  const applySearchFilters = useCallback(
    async (filters: ListingFilters) => {
    setLoadingSearch(true)
    setApiError(null)

    try {
      await recordBehaviorEvent({
        event_type: 'search_applied',
        search_filters: {
          city: filters.city || null,
          neighborhood: filters.neighborhood || null,
          property_type: filters.propertyType || null,
        },
        metadata: {
          source: 'web-dashboard',
        },
      })

      const loadedListings = await loadListings(filters)
      setAppliedFilters(filters)
      setListings(loadedListings.items)
      addActivity(
        setActivity,
        'Search applied',
        `Loaded ${loadedListings.total} listings for ${searchSummary(filters)}.`,
        'positive',
      )
      await refreshRecommendations()
    } catch (error) {
      setApiError(errorMessage(error))
      addActivity(setActivity, 'Search failed', errorMessage(error), 'warning')
    } finally {
      setLoadingSearch(false)
    }
  }, [refreshRecommendations])

  const handleApplyFilters = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    await applySearchFilters(searchForm)
  }

  const handleProfileSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setSavingProfile(true)
    setApiError(null)

    try {
      const savedProfile = await saveProfile(profileFormToPayload(profileForm))
      setProfile(savedProfile)
      setProfileForm(profileToForm(savedProfile))
      addActivity(setActivity, 'Profile saved', 'Buyer and investor intake updated.', 'positive')
      await refreshRecommendations()
    } catch (error) {
      setApiError(errorMessage(error))
      addActivity(setActivity, 'Profile save failed', errorMessage(error), 'warning')
    } finally {
      setSavingProfile(false)
    }
  }

  const handleSelectListing = async (listing: Listing) => {
    setLeadRoom(null)
    setSelectedListingId(listing.id)
    addActivity(setActivity, 'Listing opened', `${listing.title} in ${listing.neighborhood}.`, 'neutral')

    try {
      await recordBehaviorEvent({
        event_type: 'listing_viewed',
        listing_id: listing.id,
        metadata: {
          title: listing.title,
          source: 'web-dashboard',
        },
      })
      await refreshRecommendations()
    } catch (error) {
      setApiError(errorMessage(error))
    }
  }

  const handleFeedbackSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!selectedListing) {
      return
    }

    setSavingFeedback(true)
    setApiError(null)

    try {
      await submitFeedback(selectedListing.id, {
        clarity_rating: numberOrNull(feedbackForm.clarity_rating),
        photo_quality_rating: numberOrNull(feedbackForm.photo_quality_rating),
        price_trust_rating: numberOrNull(feedbackForm.price_trust_rating),
        location_confidence_rating: numberOrNull(feedbackForm.location_confidence_rating),
        interest_level: feedbackForm.interest_level || null,
        missing_information: splitList(feedbackForm.missing_information),
        free_text: feedbackForm.free_text.trim() || null,
      })

      setFeedbackForm(DEFAULT_FEEDBACK_FORM)
      addActivity(
        setActivity,
        'Feedback submitted',
        `Captured feedback for ${selectedListing.title}.`,
        'positive',
      )
      await loadFeedbackSummary(selectedListing.id)
        .then((summary) => setFeedbackSummary(summary))
        .catch((error) => setApiError(errorMessage(error)))
      await refreshRecommendations()
    } catch (error) {
      setApiError(errorMessage(error))
      addActivity(setActivity, 'Feedback save failed', errorMessage(error), 'warning')
    } finally {
      setSavingFeedback(false)
    }
  }

  const handleLeadRoomSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    if (!selectedListing) {
      return
    }

    setSavingLeadRoom(true)
    setApiError(null)

    try {
      const savedRoom = await startLeadRoom({
        listing_id: selectedListing.id,
        intent: leadForm.intent,
        budget_fit: leadForm.budget_fit,
        preferred_contact_method: leadForm.preferred_contact_method,
      })

      setLeadRoom(savedRoom)
      addActivity(
        setActivity,
        'Lead room started',
        `${selectedListing.title} moved into ${savedRoom.stage}.`,
        'positive',
      )
    } catch (error) {
      setApiError(errorMessage(error))
      addActivity(setActivity, 'Lead room failed', errorMessage(error), 'warning')
    } finally {
      setSavingLeadRoom(false)
    }
  }

  const handleParseText = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setParsingText(true)
    setApiError(null)

    try {
      const parsed = await parseListingText(parseText)
      setParsedResult(parsed)
      addActivity(setActivity, 'Text parsed', 'Dialect parser returned a structured listing.', 'positive')
    } catch (error) {
      setApiError(errorMessage(error))
      addActivity(setActivity, 'Parse failed', errorMessage(error), 'warning')
    } finally {
      setParsingText(false)
    }
  }

  const handleEstimateValue = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault()
    setEstimatingValue(true)
    setApiError(null)

    try {
      const result = await estimateBaselineValue(valuationText)
      setValuationResult(result)
      addActivity(
        setActivity,
        'Baseline value estimated',
        result.estimated_price_jod
          ? `Estimated at ${formatMoney(result.estimated_price_jod)}.`
          : 'Estimator did not have enough evidence to price the listing.',
        'positive',
      )
    } catch (error) {
      setApiError(errorMessage(error))
      addActivity(setActivity, 'Estimate failed', errorMessage(error), 'warning')
    } finally {
      setEstimatingValue(false)
    }
  }

  const applyDraftProfile = () => {
    setProfileForm(profileToForm(profile))
    addActivity(setActivity, 'Profile draft reset', 'Pulled the saved intake back into the form.', 'neutral')
  }

  const clearSearch = async () => {
    setSearchForm(DEFAULT_SEARCH)
    addActivity(setActivity, 'Filters cleared', 'Search returned to the full live catalog.', 'neutral')
    await applySearchFilters(DEFAULT_SEARCH)
  }

  const selectedFeedbackNote = feedbackSummary?.investor_note ?? 'No investor note yet.'

  return (
    <div className="app-shell">
      <header className="shell-header">
        <div className="brand-block">
          <p className="eyebrow">AqariX Irbid workspace</p>
          <h1>Buyer and investor command center</h1>
          <p className="lede">
            Intake buyers, search listings, inspect recommendations, collect feedback, and open lead rooms without
            leaving the live backend.
          </p>
          <div className="header-chips">
            <StatusPill
              tone={apiState === 'ready' ? 'positive' : apiState === 'error' ? 'warning' : 'neutral'}
              icon={apiState === 'ready' ? CheckCircle2 : apiState === 'error' ? AlertTriangle : Loader2}
            >
              {apiState === 'ready' ? 'Backend connected' : apiState === 'error' ? 'Backend issue' : 'Connecting'}
            </StatusPill>
            <StatusPill tone="neutral" icon={UserRound}>
              {demoUserId || DEFAULT_DEMO_USER_ID}
            </StatusPill>
            <StatusPill tone="neutral" icon={BarChart3}>
              {getApiBase()}
            </StatusPill>
          </div>
        </div>

        <form className="connection-form" onSubmit={handleDemoUserConnect}>
          <label className="field field--inline">
            <span>Demo user</span>
            <input
              value={demoUserDraft}
              onChange={(event) => setDemoUserDraft(event.target.value)}
              placeholder="demo-buyer-irbid"
              autoComplete="off"
            />
          </label>
          <div className="button-row">
            <button className="button button--primary" type="submit">
              <Save size={16} />
              Connect
            </button>
            <button className="button button--ghost" type="button" onClick={handleRefreshAll}>
              <RefreshCw size={16} className={loadingBootstrap ? 'spin' : ''} />
              Refresh all
            </button>
          </div>
        </form>
      </header>

      {apiError ? (
        <div className="banner banner--error" role="alert">
          <AlertTriangle size={16} />
          <span>{apiError}</span>
        </div>
      ) : null}

      <section className="summary-grid" aria-label="Dashboard summary">
        {summaryCards.map((card) => (
          <MetricCard key={card.label} icon={card.icon} label={card.label} value={card.value} hint={card.hint} />
        ))}
      </section>

      <section className="workspace-grid">
        <aside className="panel panel--side" aria-label="Intake and filters">
          <SectionHeader
            eyebrow="Intake"
            title="Buyer / investor profile"
            description="Save the user's budget and preferences before refining recommendations."
            icon={UserRound}
          />

          <form className="stack" onSubmit={handleProfileSubmit}>
            <div className="field-grid">
              <label className="field">
                <span>Budget min JOD</span>
                <input
                  type="number"
                  min="0"
                  value={profileForm.budget_min_jod}
                  onChange={(event) => setProfileForm((current) => ({ ...current, budget_min_jod: event.target.value }))}
                  placeholder="0"
                />
              </label>
              <label className="field">
                <span>Budget max JOD</span>
                <input
                  type="number"
                  min="0"
                  value={profileForm.budget_max_jod}
                  onChange={(event) => setProfileForm((current) => ({ ...current, budget_max_jod: event.target.value }))}
                  placeholder="750000"
                />
              </label>
            </div>

            <label className="field">
              <span>Preferred cities</span>
              <input
                value={profileForm.preferred_cities}
                onChange={(event) => setProfileForm((current) => ({ ...current, preferred_cities: event.target.value }))}
                placeholder="Irbid, Amman"
              />
            </label>

            <label className="field">
              <span>Preferred neighborhoods</span>
              <input
                value={profileForm.preferred_neighborhoods}
                onChange={(event) =>
                  setProfileForm((current) => ({ ...current, preferred_neighborhoods: event.target.value }))
                }
                placeholder="al_husn, hay_al_jameaa"
              />
            </label>

            <div className="field">
              <span>Property types</span>
              <div className="checkbox-grid">
                {PROPERTY_TYPE_OPTIONS.map((option) => {
                  const checked = profileForm.property_types.includes(option.value)
                  return (
                    <label key={option.value} className="checkbox-chip">
                      <input
                        type="checkbox"
                        checked={checked}
                        onChange={() =>
                          setProfileForm((current) => ({
                            ...current,
                            property_types: checked
                              ? current.property_types.filter((item) => item !== option.value)
                              : [...current.property_types, option.value],
                          }))
                        }
                      />
                      <span>{option.label}</span>
                    </label>
                  )
                })}
              </div>
            </div>

            <div className="field-grid">
              <label className="field">
                <span>Purpose</span>
                <select
                  value={profileForm.purpose}
                  onChange={(event) => setProfileForm((current) => ({ ...current, purpose: event.target.value }))}
                >
                  {PURPOSE_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
              <label className="field">
                <span>Risk tolerance</span>
                <select
                  value={profileForm.risk_tolerance}
                  onChange={(event) => setProfileForm((current) => ({ ...current, risk_tolerance: event.target.value }))}
                >
                  {RISK_OPTIONS.map((option) => (
                    <option key={option.value} value={option.value}>
                      {option.label}
                    </option>
                  ))}
                </select>
              </label>
            </div>

            <label className="field">
              <span>Investment horizon years</span>
              <input
                type="number"
                min="0"
                value={profileForm.investment_horizon_years}
                onChange={(event) =>
                  setProfileForm((current) => ({ ...current, investment_horizon_years: event.target.value }))
                }
                placeholder="5"
              />
            </label>

            <div className="button-row">
              <button className="button button--primary" type="submit" disabled={savingProfile}>
                {savingProfile ? <Loader2 size={16} className="spin" /> : <Save size={16} />}
                Save profile
              </button>
              <button className="button button--ghost" type="button" onClick={applyDraftProfile}>
                <ArrowRight size={16} />
                Reset draft
              </button>
            </div>
          </form>

          <div className="panel-divider" />

          <SectionHeader
            eyebrow="Search"
            title="Listing filters"
            description="Search the live catalog and capture a behavior event for the query."
            icon={Search}
          />

          <form className="stack" onSubmit={handleApplyFilters}>
            <div className="field-grid">
              <label className="field">
                <span>City</span>
                <input
                  value={searchForm.city}
                  onChange={(event) => setSearchForm((current) => ({ ...current, city: event.target.value }))}
                  placeholder="Amman"
                />
              </label>
              <label className="field">
                <span>Neighborhood</span>
                <input
                  value={searchForm.neighborhood}
                  onChange={(event) => setSearchForm((current) => ({ ...current, neighborhood: event.target.value }))}
                  placeholder="Abdoun"
                />
              </label>
            </div>

            <label className="field">
              <span>Property type</span>
              <select
                value={searchForm.propertyType}
                onChange={(event) =>
                  setSearchForm((current) => ({
                    ...current,
                    propertyType: event.target.value as PropertyType | '',
                  }))
                }
              >
                {SEARCH_FIT_OPTIONS.map((option) => (
                  <option key={option.value || 'any'} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </label>

            <div className="button-row">
              <button className="button button--primary" type="submit" disabled={loadingSearch}>
                {loadingSearch ? <Loader2 size={16} className="spin" /> : <Search size={16} />}
                Apply filters
              </button>
              <button className="button button--ghost" type="button" onClick={clearSearch}>
                <SlidersHorizontal size={16} />
                Clear filters
              </button>
            </div>
          </form>
        </aside>

        <section className="panel panel--main" aria-label="Catalog and selected listing">
          <SectionHeader
            eyebrow="Catalog"
            title="Live listing results"
            description={`Showing ${listings.length} listing${listings.length === 1 ? '' : 's'} from ${activeFiltersLabel}.`}
            icon={MapPinned}
            actions={
              <button className="button button--ghost button--compact" type="button" onClick={handleRefreshAll}>
                <RefreshCw size={14} className={loadingBootstrap ? 'spin' : ''} />
                Reload
              </button>
            }
          />

          <div className="listing-list" role="list" aria-label="Listings">
            {listings.map((listing) => (
              <button
                key={listing.id}
                type="button"
                className={`listing-row ${listing.id === selectedListingId ? 'listing-row--active' : ''}`}
                onClick={() => void handleSelectListing(listing)}
              >
                <img className="listing-row__image" src={listing.image_url} alt="" loading="lazy" />
                <div className="listing-row__body">
                  <div className="listing-row__title">
                    <strong>{listing.title}</strong>
                    <span>{listing.city}</span>
                  </div>
                  <p className="listing-row__meta">
                    {listing.neighborhood} · {listing.property_type} · {listing.area_sqm} sqm
                  </p>
                  <div className="chip-row">
                    <StatusPill tone="neutral">{formatMoney(listing.asking_price_jod)}</StatusPill>
                    <StatusPill tone="neutral">Score {listing.aqari_score.toFixed(1)}</StatusPill>
                    <StatusPill tone="neutral">{listing.confidence}</StatusPill>
                    <StatusPill tone="neutral">{listing.price_signal}</StatusPill>
                  </div>
                </div>
                <ChevronRight size={16} className="listing-row__chevron" />
              </button>
            ))}

            {!listings.length ? <EmptyState title="No listings yet" body="Run a search to bring the catalog back." /> : null}
          </div>

          <div className="panel-divider" />

          <div className="detail-layout">
            <div className="selected-card">
              <SectionHeader
                eyebrow="Selected listing"
                title={selectedListing?.title ?? 'Pick a listing'}
                description={
                  selectedListing
                    ? `${selectedListing.city} · ${selectedListing.neighborhood} · ${selectedListing.property_type}`
                    : 'The detail panel updates when you open a listing.'
                }
                icon={Eye}
              />

              {selectedListing ? (
                <>
                  <div className="detail-hero">
                    <img src={selectedListing.image_url} alt={selectedListing.title} loading="lazy" />
                    <div className="detail-hero__overlay">
                      <span>{formatMoney(selectedListing.asking_price_jod)}</span>
                      <span>{selectedListing.area_sqm} sqm</span>
                    </div>
                  </div>

                  <div className="detail-grid">
                    <KeyValue label="Property type" value={selectedListing.property_type} />
                    <KeyValue label="Bedrooms" value={selectedListing.bedrooms?.toString() ?? '—'} />
                    <KeyValue label="Bathrooms" value={selectedListing.bathrooms?.toString() ?? '—'} />
                    <KeyValue label="Aqari score" value={selectedListing.aqari_score.toFixed(1)} />
                    <KeyValue label="Confidence" value={selectedListing.confidence} />
                    <KeyValue label="Price signal" value={selectedListing.price_signal} />
                  </div>

                  <div className="detail-notes">
                    <StatusPill tone="positive">{selectedFeedbackNote}</StatusPill>
                    <p className="muted-copy">
                      Feedback count: {feedbackSummary?.feedback_count ?? 0}
                      {feedbackSummary?.top_missing_information.length
                        ? ` · Missing: ${feedbackSummary.top_missing_information.join(', ')}`
                        : ''}
                    </p>
                  </div>
                </>
              ) : (
                <EmptyState
                  title="No listing selected"
                  body="The first listing in the current search results will open automatically."
                />
              )}
            </div>

            <div className="forms-grid">
              <form className="mini-panel" onSubmit={handleFeedbackSubmit}>
                <SectionHeader
                  eyebrow="Feedback"
                  title="Listing feedback"
                  description="Collect the missing details that improve ads and seller notes."
                  icon={MessageSquareQuote}
                />

                <div className="rating-grid">
                  <RatingField
                    label="Clarity"
                    value={feedbackForm.clarity_rating}
                    onChange={(value) => setFeedbackForm((current) => ({ ...current, clarity_rating: value }))}
                  />
                  <RatingField
                    label="Photos"
                    value={feedbackForm.photo_quality_rating}
                    onChange={(value) => setFeedbackForm((current) => ({ ...current, photo_quality_rating: value }))}
                  />
                  <RatingField
                    label="Price trust"
                    value={feedbackForm.price_trust_rating}
                    onChange={(value) => setFeedbackForm((current) => ({ ...current, price_trust_rating: value }))}
                  />
                  <RatingField
                    label="Location"
                    value={feedbackForm.location_confidence_rating}
                    onChange={(value) =>
                      setFeedbackForm((current) => ({ ...current, location_confidence_rating: value }))
                    }
                  />
                </div>

                <label className="field">
                  <span>Interest level</span>
                  <select
                    value={feedbackForm.interest_level}
                    onChange={(event) =>
                      setFeedbackForm((current) => ({ ...current, interest_level: event.target.value }))
                    }
                  >
                    <option value="">Choose</option>
                    {FEEDBACK_INTEREST_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>Missing information</span>
                  <input
                    value={feedbackForm.missing_information}
                    onChange={(event) =>
                      setFeedbackForm((current) => ({ ...current, missing_information: event.target.value }))
                    }
                    placeholder="floor_plan, balcony, deed"
                  />
                </label>

                <label className="field">
                  <span>Free text</span>
                  <textarea
                    rows={4}
                    value={feedbackForm.free_text}
                    onChange={(event) => setFeedbackForm((current) => ({ ...current, free_text: event.target.value }))}
                    placeholder="What should improve in the listing?"
                  />
                </label>

                <div className="button-row">
                  <button className="button button--primary" type="submit" disabled={!selectedListing || savingFeedback}>
                    {savingFeedback ? <Loader2 size={16} className="spin" /> : <MessageSquareQuote size={16} />}
                    Submit feedback
                  </button>
                  <button className="button button--ghost" type="button" onClick={() => setFeedbackForm(DEFAULT_FEEDBACK_FORM)}>
                    <ArrowRight size={16} />
                    Clear
                  </button>
                </div>
              </form>

              <form className="mini-panel" onSubmit={handleLeadRoomSubmit}>
                <SectionHeader
                  eyebrow="Lead room"
                  title="Start a supervised lead room"
                  description="Create the admin-visible record from the selected listing."
                  icon={DoorOpen}
                />

                <label className="field">
                  <span>Intent</span>
                  <select
                    value={leadForm.intent}
                    onChange={(event) => setLeadForm((current) => ({ ...current, intent: event.target.value }))}
                  >
                    {LEAD_INTENT_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>Budget fit</span>
                  <select
                    value={leadForm.budget_fit}
                    onChange={(event) => setLeadForm((current) => ({ ...current, budget_fit: event.target.value }))}
                  >
                    {BUDGET_FIT_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <label className="field">
                  <span>Preferred contact method</span>
                  <select
                    value={leadForm.preferred_contact_method}
                    onChange={(event) =>
                      setLeadForm((current) => ({ ...current, preferred_contact_method: event.target.value }))
                    }
                  >
                    {CONTACT_OPTIONS.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </label>

                <div className="button-row">
                  <button className="button button--primary" type="submit" disabled={!selectedListing || savingLeadRoom}>
                    {savingLeadRoom ? <Loader2 size={16} className="spin" /> : <DoorOpen size={16} />}
                    Start lead room
                  </button>
                  <button className="button button--ghost" type="button" onClick={() => setLeadForm(DEFAULT_LEAD_FORM)}>
                    <ArrowRight size={16} />
                    Reset
                  </button>
                </div>

                {leadRoom ? (
                  <div className="inline-status">
                    <StatusPill tone="positive">Room {leadRoom.stage}</StatusPill>
                    <p className="muted-copy">Lead room ID {leadRoom.id}</p>
                  </div>
                ) : null}
              </form>
            </div>
          </div>
        </section>

        <aside className="panel panel--side" aria-label="Recommendations and activity">
          <SectionHeader
            eyebrow="Recommendations"
            title="Why recommended"
            description="These items combine profile preferences and recent behavior signals."
            icon={Sparkles}
          />

          <div className="recommendation-list">
            {recommendations.slice(0, 4).map((item) => (
              <button
                key={item.listing.id}
                type="button"
                className={`recommendation-row ${item.listing.id === selectedListingId ? 'recommendation-row--active' : ''}`}
                onClick={() => void handleSelectListing(item.listing)}
              >
                <div className="recommendation-row__header">
                  <strong>{item.listing.title}</strong>
                  <span>{formatScore(item.recommendation_score)}</span>
                </div>
                <p className="muted-copy">{item.explanation}</p>
                <div className="chip-row">
                  {item.reason_codes.slice(0, 3).map((reason) => (
                    <StatusPill key={reason} tone="neutral">
                      {reason}
                    </StatusPill>
                  ))}
                </div>
              </button>
            ))}

            {!recommendations.length ? (
              <EmptyState title="No recommendations yet" body="Save a profile or record a view to update the ranking." />
            ) : null}
          </div>

          <div className="panel-divider" />

          <SectionHeader
            eyebrow="Activity"
            title="Session log"
            description="We keep a compact record of the actions taken in this browser session."
            icon={Activity}
          />

          <div className="activity-list">
            {activity.length ? (
              activity.map((item) => (
                <article key={item.id} className={`activity-item activity-item--${item.tone}`}>
                  <div className="activity-item__top">
                    <strong>{item.title}</strong>
                    <span>{item.time}</span>
                  </div>
                  <p className="muted-copy">{item.detail}</p>
                </article>
              ))
            ) : (
              <EmptyState title="No activity yet" body="Open a listing, save a profile, or run a search." />
            )}
          </div>
        </aside>
      </section>

      <section className="panel panel--analysis" aria-label="AI text lab">
        <SectionHeader
          eyebrow="AI lab"
          title="Parser and valuation tools"
          description="These forms call the live backend parser and baseline estimator using real Irbid-style copy."
          icon={Wand2}
        />

        <div className="analysis-grid">
          <form className="mini-panel mini-panel--analysis" onSubmit={handleParseText}>
            <SectionHeader
              eyebrow="Parser"
              title="Parse listing text"
              description="Normalize the raw post into structured fields and quality signals."
              icon={FileText}
            />

            <label className="field">
              <span>Raw text</span>
              <textarea
                rows={6}
                value={parseText}
                onChange={(event) => setParseText(event.target.value)}
                placeholder="Paste a real listing post here"
              />
            </label>

            <div className="button-row">
              <button className="button button--primary" type="submit" disabled={parsingText}>
                {parsingText ? <Loader2 size={16} className="spin" /> : <Wand2 size={16} />}
                Parse text
              </button>
              <button className="button button--ghost" type="button" onClick={() => setParseText(DEFAULT_PARSE_SAMPLE)}>
                <ArrowRight size={16} />
                Restore sample
              </button>
            </div>

            {parsedResult ? (
              <div className="analysis-result">
                <div className="detail-grid detail-grid--compact">
                  <KeyValue label="Intent" value={parsedResult.intent} />
                  <KeyValue label="Property type" value={parsedResult.property_type ?? '—'} />
                  <KeyValue label="Price" value={parsedResult.price_jod ? formatMoney(parsedResult.price_jod) : '—'} />
                  <KeyValue label="Area" value={parsedResult.area_sqm ? `${parsedResult.area_sqm} sqm` : '—'} />
                </div>
                <div className="chip-row">
                  <StatusPill tone="positive">{parsedResult.quality.grade}</StatusPill>
                  <StatusPill tone="neutral">
                    {parsedResult.quality.is_model_ready ? 'Model ready' : 'Needs cleanup'}
                  </StatusPill>
                  {parsedResult.neighborhoods.slice(0, 2).map((item) => (
                    <StatusPill key={item.key} tone="neutral">
                      {item.display_name}
                    </StatusPill>
                  ))}
                </div>
              </div>
            ) : (
              <p className="muted-copy">Run the parser to see city, property type, quality, and location signals.</p>
            )}
          </form>

          <form className="mini-panel mini-panel--analysis" onSubmit={handleEstimateValue}>
            <SectionHeader
              eyebrow="Estimator"
              title="Baseline valuation"
              description="Estimate a quick price using the current median-unit-price baseline."
              icon={BarChart3}
            />

            <label className="field">
              <span>Raw text</span>
              <textarea
                rows={6}
                value={valuationText}
                onChange={(event) => setValuationText(event.target.value)}
                placeholder="Paste a listing post to estimate value"
              />
            </label>

            <div className="button-row">
              <button className="button button--primary" type="submit" disabled={estimatingValue}>
                {estimatingValue ? <Loader2 size={16} className="spin" /> : <BarChart3 size={16} />}
                Estimate value
              </button>
              <button
                className="button button--ghost"
                type="button"
                onClick={() => setValuationText(DEFAULT_VALUATION_SAMPLE)}
              >
                <ArrowRight size={16} />
                Restore sample
              </button>
            </div>

            {valuationResult ? (
              <div className="analysis-result">
                <div className="detail-grid detail-grid--compact">
                  <KeyValue
                    label="Estimated price"
                    value={valuationResult.estimated_price_jod ? formatMoney(valuationResult.estimated_price_jod) : '—'}
                  />
                  <KeyValue label="Confidence" value={valuationResult.confidence} />
                  <KeyValue label="Method" value={valuationResult.method} />
                  <KeyValue label="Matched count" value={valuationResult.matched_count.toString()} />
                </div>
                <div className="chip-row">
                  <StatusPill tone={valuationResult.estimated_price_jod ? 'positive' : 'warning'}>
                    {valuationResult.reason ?? 'No pricing signal'}
                  </StatusPill>
                  <StatusPill tone="neutral">{valuationResult.model_version}</StatusPill>
                </div>
              </div>
            ) : (
              <p className="muted-copy">Use the estimator to confirm the baseline before heavier modeling work.</p>
            )}
          </form>
        </div>
      </section>
    </div>
  )
}

function SectionHeader({
  eyebrow,
  title,
  description,
  icon: Icon,
  actions,
}: {
  eyebrow: string
  title: string
  description: string
  icon: LucideIcon
  actions?: ReactNode
}) {
  return (
    <div className="section-header">
      <div className="section-header__copy">
        <div className="section-eyebrow">
          <Icon size={14} />
          <span>{eyebrow}</span>
        </div>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
      {actions ? <div className="section-header__actions">{actions}</div> : null}
    </div>
  )
}

function MetricCard({
  icon: Icon,
  label,
  value,
  hint,
}: {
  icon: LucideIcon
  label: string
  value: string
  hint: string
}) {
  return (
    <article className="metric-card">
      <div className="metric-card__top">
        <span className="metric-card__icon">
          <Icon size={16} />
        </span>
        <span className="metric-card__label">{label}</span>
      </div>
      <strong className="metric-card__value">{value}</strong>
      <p className="metric-card__hint">{hint}</p>
    </article>
  )
}

function StatusPill({
  children,
  tone,
  icon: Icon,
}: {
  children: ReactNode
  tone: 'neutral' | 'positive' | 'warning'
  icon?: LucideIcon
}) {
  return (
    <span className={`status-pill status-pill--${tone}`}>
      {Icon ? <Icon size={12} /> : null}
      <span>{children}</span>
    </span>
  )
}

function KeyValue({ label, value }: { label: string; value: string }) {
  return (
    <div className="key-value">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function RatingField({
  label,
  value,
  onChange,
}: {
  label: string
  value: string
  onChange: (value: string) => void
}) {
  return (
    <label className="field rating-field">
      <span>{label}</span>
      <select value={value} onChange={(event) => onChange(event.target.value)}>
        <option value="">Choose</option>
        <option value="1">1</option>
        <option value="2">2</option>
        <option value="3">3</option>
        <option value="4">4</option>
        <option value="5">5</option>
      </select>
    </label>
  )
}

function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="empty-state">
      <p className="empty-state__title">{title}</p>
      <p className="muted-copy">{body}</p>
    </div>
  )
}

function profileToForm(profile: BuyerInvestorProfile | null): ProfileFormState {
  if (!profile) {
    return { ...DEFAULT_PROFILE_FORM }
  }

  return {
    budget_min_jod: profile.budget_min_jod?.toString() ?? '',
    budget_max_jod: profile.budget_max_jod?.toString() ?? '',
    preferred_cities: profile.preferred_cities.join(', '),
    preferred_neighborhoods: profile.preferred_neighborhoods.join(', '),
    property_types: [...profile.property_types],
    purpose: profile.purpose,
    risk_tolerance: profile.risk_tolerance,
    investment_horizon_years: profile.investment_horizon_years?.toString() ?? '',
  }
}

function profileFormToPayload(form: ProfileFormState): BuyerInvestorProfileIn {
  return {
    budget_min_jod: numberOrNull(form.budget_min_jod),
    budget_max_jod: numberOrNull(form.budget_max_jod),
    preferred_cities: splitList(form.preferred_cities),
    preferred_neighborhoods: splitList(form.preferred_neighborhoods),
    property_types: form.property_types,
    purpose: form.purpose,
    risk_tolerance: form.risk_tolerance,
    investment_horizon_years: numberOrNull(form.investment_horizon_years),
  }
}

function splitList(value: string): string[] {
  return value
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean)
}

function numberOrNull(value: string): number | null {
  const trimmed = value.trim()
  if (!trimmed) {
    return null
  }

  const parsed = Number(trimmed)
  return Number.isFinite(parsed) ? parsed : null
}

function formatMoney(value: number): string {
  return `${new Intl.NumberFormat('en-US', { maximumFractionDigits: 0 }).format(value)} JOD`
}

function formatScore(score: number): string {
  return `${score.toFixed(1)}/10`
}

function errorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }

  return 'Something went wrong.'
}

function addActivity(
  setActivity: Dispatch<SetStateAction<ActivityItem[]>>,
  title: string,
  detail: string,
  tone: ActivityItem['tone'],
) {
  const now = new Date()
  const time = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  const id = now.getTime() + Math.floor(Math.random() * 1000)

  setActivity((current) => [
    { id, title, detail, time, tone },
    ...current,
  ].slice(0, 6))
}

function deriveBudgetFit(listing: Listing, budgetMax: number | null): string {
  if (!budgetMax) {
    return 'outside_budget'
  }

  if (listing.asking_price_jod <= budgetMax) {
    return 'inside_budget'
  }

  if (listing.asking_price_jod <= budgetMax * 1.15) {
    return 'stretching_budget'
  }

  return 'outside_budget'
}

function searchSummary(filters: ListingFilters): string {
  const parts = [filters.city, filters.neighborhood, filters.propertyType].filter(Boolean)
  return parts.length ? parts.join(' · ') : 'all filters'
}

export default App
