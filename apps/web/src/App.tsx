import { useEffect, useMemo, useState } from 'react'
import {
  ArrowRight,
  BarChart3,
  BedDouble,
  Bell,
  Bookmark,
  Building2,
  CalendarClock,
  CheckCircle2,
  ChevronRight,
  CircleDollarSign,
  ClipboardList,
  Heart,
  Home,
  LineChart,
  Map,
  MessageSquare,
  Search,
  Languages,
  ShieldCheck,
  SlidersHorizontal,
  Sparkles,
  Star,
  Moon,
  Sun,
  UserRound,
} from 'lucide-react'
import './App.css'
import { copy, localeMeta, type Locale } from './i18n'

type Listing = {
  id: string
  title: string
  area: string
  district: string
  type: string
  price: string
  pricePerSqm: string
  specs: string[]
  score: string
  priceSignal: string
  confidence: 'High' | 'Medium'
  image: string
  recommendedBecause: string[]
  investorNote: string
}

type ApiListing = {
  id: string
  title: string
  city: string
  neighborhood: string
  property_type: string
  asking_price_jod: number
  area_sqm: number
  bedrooms: number | null
  bathrooms: number | null
  aqari_score: number
  confidence: 'high' | 'medium'
  price_signal: string
  image_url: string
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL as string | undefined

const fallbackListings: Listing[] = [
  {
    id: 'aqx-1024',
    title: 'Stately Limestone Residence',
    area: 'Abdoun',
    district: 'West Amman',
    type: 'Villa',
    price: 'JOD 850,000',
    pricePerSqm: 'JOD 1,410 / sqm',
    specs: ['5 beds', '4 baths', '602 sqm'],
    score: '9.2',
    priceSignal: 'Fair price',
    confidence: 'High',
    image:
      'https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=80',
    recommendedBecause: ['Matches Abdoun searches', 'Similar to saved villas', 'Strong location confidence'],
    investorNote: 'Users ask for clearer garden photos and maintenance fee details.',
  },
  {
    id: 'aqx-1188',
    title: 'Skyline View Penthouse',
    area: '5th Circle',
    district: 'Amman',
    type: 'Apartment',
    price: 'JOD 245,000',
    pricePerSqm: 'JOD 1,225 / sqm',
    specs: ['3 beds', '3 baths', '200 sqm'],
    score: '7.8',
    priceSignal: 'Slight premium',
    confidence: 'Medium',
    image:
      'https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?auto=format&fit=crop&w=1200&q=80',
    recommendedBecause: ['Near viewed map area', 'Good fit for rental watchlist', 'Comparable price gap'],
    investorNote: 'Photo quality is strong; users want building age and service fee clarity.',
  },
  {
    id: 'aqx-1302',
    title: 'Village Prime Retail Space',
    area: 'Sweifieh',
    district: 'Commercial corridor',
    type: 'Commercial',
    price: 'JOD 1,200,000',
    pricePerSqm: 'Investment grade',
    specs: ['100% occupancy', 'Street frontage', '420 sqm'],
    score: '8.6',
    priceSignal: 'High demand',
    confidence: 'High',
    image:
      'https://images.unsplash.com/photo-1494526585095-c41746248156?auto=format&fit=crop&w=1200&q=80',
    recommendedBecause: ['Matches commercial intent', 'Strong liquidity signal', 'High lead-room starts'],
    investorNote: 'Users request tenant mix and lease duration before starting negotiations.',
  },
]

const leadStages = [
  {
    name: 'New Leads',
    count: '03',
    items: [
      { name: 'Abdullah Mansour', asset: 'Villa in West Amman', value: 'JOD 450,000', score: 88 },
      { name: 'Mariam Khalid', asset: 'Commercial Space - Al Abdali', value: 'JOD 220,000', score: 72 },
    ],
  },
  {
    name: 'Qualified',
    count: '02',
    items: [{ name: 'Capital Trust Group', asset: 'Mixed-use Development Lot', value: 'JOD 1,200,000', score: 95 }],
  },
  {
    name: 'Viewing',
    count: '04',
    items: [{ name: 'Nasser Al-Qadi', asset: 'Luxury Penthouse - Dahiyat Al-Amir', value: 'JOD 550,000', score: 91 }],
  },
]

const tabIds = ['explore', 'detail', 'lead-room', 'seller', 'dealer'] as const

function App() {
  const [locale, setLocale] = useState<Locale>('ar')
  const [theme, setTheme] = useState<'light' | 'dark'>('light')
  const [listings, setListings] = useState<Listing[]>(fallbackListings)
  const [searchQuery, setSearchQuery] = useState('')
  const [debouncedQuery, setDebouncedQuery] = useState('')
  const activeListing = listings[0] ?? fallbackListings[0]
  const t = copy[locale]
  const meta = localeMeta[locale]
  const navItems = useMemo(
    () => tabIds.map((id, index) => ({ id, label: t.nav[index] })),
    [t.nav],
  )

  useEffect(() => {
    document.documentElement.dir = meta.dir
    document.documentElement.lang = meta.lang
  }, [meta.dir, meta.lang])

  useEffect(() => {
    document.documentElement.dataset.theme = theme
  }, [theme])

  useEffect(() => {
    const timeout = window.setTimeout(() => setDebouncedQuery(searchQuery.trim()), 300)
    return () => window.clearTimeout(timeout)
  }, [searchQuery])

  useEffect(() => {
    if (!apiBaseUrl) return

    const controller = new AbortController()
    const params = new URLSearchParams()
    if (debouncedQuery) params.set('neighborhood', debouncedQuery)
    const query = params.size ? `?${params.toString()}` : ''

    fetch(`${apiBaseUrl}/listings${query}`, { signal: controller.signal })
      .then((response) => (response.ok ? response.json() : Promise.reject(new Error(response.statusText))))
      .then((body: { items?: ApiListing[] }) => {
        setListings(body.items ? body.items.map(mapApiListing) : fallbackListings)
      })
      .catch(() => undefined)

    return () => controller.abort()
  }, [debouncedQuery])

  return (
    <div className="app-shell">
      <header className="topbar">
        <a className="brand" href="#top" aria-label="AqariX home">
          <span className="brand-mark">
            <BarChart3 size={20} aria-hidden="true" />
          </span>
          <span>{t.brand}</span>
        </a>
        <nav className="topnav" aria-label="Primary">
          {navItems.map((tab) => (
            <a key={tab.id} href={`#${tab.id}`}>
              {tab.label}
            </a>
          ))}
        </nav>
        <div className="top-actions">
          <button
            className="icon-button text-control"
            type="button"
            onClick={() => setLocale(locale === 'ar' ? 'en' : 'ar')}
            aria-label="Switch language"
            title="Switch language"
          >
            <Languages size={18} aria-hidden="true" />
            <span>{meta.nextLabel}</span>
          </button>
          <button
            className="icon-button"
            type="button"
            onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
            aria-label={theme === 'dark' ? t.themeLight : t.themeDark}
            title={theme === 'dark' ? t.themeLight : t.themeDark}
          >
            {theme === 'dark' ? <Sun size={20} aria-hidden="true" /> : <Moon size={20} aria-hidden="true" />}
          </button>
          <button className="icon-button" type="button" aria-label={t.notifications} title={t.notifications}>
            <Bell size={20} aria-hidden="true" />
          </button>
          <div className="avatar" aria-label="Demo user">
            <UserRound size={20} aria-hidden="true" />
          </div>
        </div>
      </header>

      <main id="top">
        <section className="hero-band" aria-labelledby="hero-title">
          <div className="hero-copy">
            <span className="eyebrow">{t.heroEyebrow}</span>
            <h1 id="hero-title">{t.heroTitle}</h1>
            <p>{t.heroBody}</p>
          </div>
          <div className="hero-panel" aria-label="MVP scope">
            <div>
              <span className="metric-label">{t.verticalSlice}</span>
              <strong>{t.sliceValue}</strong>
            </div>
            <div>
              <span className="metric-label">{t.aiIntegration}</span>
              <strong>{t.aiValue}</strong>
            </div>
            <div>
              <span className="metric-label">{t.localMarket}</span>
              <strong>{t.localValue}</strong>
            </div>
          </div>
        </section>

        <section className="workspace" id="explore" aria-labelledby="explore-title">
          <div className="mobile-frame">
            <div className="section-heading">
              <div>
                <span className="eyebrow">{t.explore}</span>
                <h2 id="explore-title">{t.propertiesInAmman}</h2>
              </div>
              <button className="text-button" type="button">
                <Map size={18} aria-hidden="true" />
                {t.map}
              </button>
            </div>

            <form className="search-card" aria-label="Search listings">
              <label htmlFor="search">{t.searchLabel}</label>
              <div className="search-row">
                <Search size={20} aria-hidden="true" />
                <input
                  id="search"
                  name="search"
                  placeholder={t.searchPlaceholder}
                  value={searchQuery}
                  onChange={(event) => setSearchQuery(event.currentTarget.value)}
                />
              </div>
              <div className="filter-row">
                <button type="button">
                  <CircleDollarSign size={16} aria-hidden="true" /> {t.price}
                </button>
                <button type="button">
                  <Building2 size={16} aria-hidden="true" /> {t.type}
                </button>
                <button type="button">
                  <SlidersHorizontal size={16} aria-hidden="true" /> {t.filters}
                </button>
              </div>
            </form>

            <div className="listing-stack">
              {listings.map((listing) => (
                <ListingCard key={listing.id} listing={listing} viewAnalysis={t.viewAnalysis} />
              ))}
            </div>
          </div>

          <aside className="insight-rail" aria-label="Recommendation context">
            <div className="rail-card">
              <span className="eyebrow">{t.behaviorSignals}</span>
              <h3>{t.recommendationsUpdate}</h3>
              <ul className="signal-list">
                <li>
                  <CheckCircle2 size={16} aria-hidden="true" /> {t.savedVillas}
                </li>
                <li>
                  <CheckCircle2 size={16} aria-hidden="true" /> {t.openedPricing}
                </li>
                <li>
                  <CheckCircle2 size={16} aria-hidden="true" /> {t.dismissedPremium}
                </li>
              </ul>
            </div>
            <div className="rail-card">
              <span className="eyebrow">{t.feedbackLoop}</span>
              <h3>{locale === 'ar' ? 'ملاحظات الإعلان تعزز ثقة المستثمر.' : 'Listing notes improve ads and investor confidence.'}</h3>
              <p>{t.feedbackLoopBody}</p>
            </div>
          </aside>
        </section>

        <section className="detail-grid" id="detail" aria-labelledby="detail-title">
          <div className="detail-media" style={{ backgroundImage: `url(${activeListing.image})` }}>
            <span className="score-badge">AqariX Score {activeListing.score}</span>
          </div>
          <div className="detail-panel">
            <span className="eyebrow">{t.detailEyebrow}</span>
            <h2 id="detail-title">{activeListing.title}</h2>
            <div className="price-row">
              <strong>{activeListing.price}</strong>
              <span>{activeListing.pricePerSqm}</span>
            </div>
            <div className="spec-grid">
              {activeListing.specs.map((spec) => (
                <span key={spec}>
                  <BedDouble size={16} aria-hidden="true" />
                  {spec}
                </span>
              ))}
            </div>
            <div className="analysis-shell">
              <div className="analysis-header">
                <Sparkles size={18} aria-hidden="true" />
                <div>
                  <h3>Offering analysis shell</h3>
                  <p>{t.analysisShellBody}</p>
                </div>
              </div>
              <div className="analysis-grid">
                <Metric label={t.fairValue} value="JOD 812k - 875k" />
                <Metric label={t.bargainRange} value="JOD 805k - 835k" />
                <Metric label={t.confidence} value={t.high} />
                <Metric label={t.liquidity} value={t.strong} />
              </div>
            </div>
            <div className="feedback-box">
              <h3>{t.investorNote}</h3>
              <p>{activeListing.investorNote}</p>
            </div>
            <ListingFeedback t={t} />
          </div>
        </section>

        <section className="lead-room" id="lead-room" aria-labelledby="lead-room-title">
          <div className="section-heading">
            <div>
              <span className="eyebrow">{t.leadEyebrow}</span>
              <h2 id="lead-room-title">{t.leadTitle}: {activeListing.title}</h2>
            </div>
            <button className="primary-button" type="button">
              <CalendarClock size={18} aria-hidden="true" />
              {t.scheduleViewing}
            </button>
          </div>
          <div className="stage-track">
            {['New inquiry', 'Qualified', 'Viewing scheduled', 'Offer made', 'Negotiation'].map((stage, index) => (
              <div className={index < 3 ? 'stage active' : 'stage'} key={stage}>
                <span>{index + 1}</span>
                <p>{stage}</p>
              </div>
            ))}
          </div>
          <div className="room-grid">
            <div className="message-panel">
              <h3>{t.messages}</h3>
              <Message from="Investor" text="I want to confirm garden size and annual maintenance fees before viewing." />
              <Message from="Dealer" text="Documents are being attached. Suggested viewing window is Thursday afternoon." />
              <Message from="AqariX Admin" text="Qualification complete. Contact reveal remains inside room record." />
            </div>
            <div className="task-panel">
              <h3>{t.nextActions}</h3>
              <Task label="Attach ownership verification" done />
              <Task label="Confirm maintenance fee" />
              <Task label="Collect viewing attendance" />
            </div>
          </div>
        </section>

        <section className="seller-grid" id="seller" aria-labelledby="seller-title">
          <div className="seller-card">
            <span className="eyebrow">{t.sellerEyebrow}</span>
            <h2 id="seller-title">{t.sellerTitle}</h2>
            <div className="checklist">
              <Task label="Add exterior evening photo" />
              <Task label="Clarify exact location confidence" done />
              <Task label="Add floor plan or room dimensions" />
              <Task label="State negotiability range" />
            </div>
          </div>
          <div className="seller-card">
            <span className="eyebrow">{t.feedbackSummary}</span>
            <h3>{t.userSignals}</h3>
            <div className="rating-bars">
              <Bar label="Clarity" value={82} />
              <Bar label="Photo quality" value={68} />
              <Bar label="Price trust" value={74} />
              <Bar label="Location confidence" value={79} />
            </div>
          </div>
        </section>

        <section className="dealer-dashboard" id="dealer" aria-labelledby="dealer-title">
          <aside className="dealer-sidebar">
            <div className="dealer-id">
              <div className="brand-mark">
                <Building2 size={22} aria-hidden="true" />
              </div>
              <div>
                <strong>{t.dealerDashboard}</strong>
                <span>Amman, Jordan</span>
              </div>
            </div>
            {[
              ['Market Overview', Home],
              ['Properties', Building2],
              ['Lead Room', MessageSquare],
              ['Analytics', LineChart],
              ['CRM Pipeline', ClipboardList],
            ].map(([label, Icon]) => (
              <button className={label === 'CRM Pipeline' ? 'side-link active' : 'side-link'} key={label as string}>
                <Icon size={20} aria-hidden="true" />
                {label as string}
              </button>
            ))}
            <div className="pipeline-health">
              <span>Pipeline health</span>
              <strong>94%</strong>
              <div>
                <i style={{ width: '94%' }} />
              </div>
            </div>
          </aside>
          <div className="pipeline-main">
            <span className="live-badge">{t.liveMarket}</span>
            <h2 id="dealer-title">{t.pipeline}</h2>
            <div className="mini-chart" aria-label="Conversion velocity chart">
              {[42, 65, 53, 58, 47, 76, 42, 65, 53, 58, 47].map((value, index) => (
                <span key={`${value}-${index}`} style={{ height: `${value}%` }} />
              ))}
            </div>
            <div className="kanban">
              {leadStages.map((stage) => (
                <div className="kanban-column" key={stage.name}>
                  <h3>
                    {stage.name} <span>({stage.count})</span>
                  </h3>
                  {stage.items.map((item) => (
                    <article className="lead-card" key={item.name}>
                      <div>
                        <span>{item.value}</span>
                        <ChevronRight size={22} aria-hidden="true" />
                      </div>
                      <h4>{item.name}</h4>
                      <p>{item.asset}</p>
                      <footer>
                        <span>
                          <Star size={14} aria-hidden="true" />
                          {item.score}
                        </span>
                      </footer>
                    </article>
                  ))}
                </div>
              ))}
            </div>
          </div>
        </section>
      </main>
    </div>
  )
}

function ListingCard({ listing, viewAnalysis }: { listing: Listing; viewAnalysis: string }) {
  return (
    <article className="listing-card">
      <div className="listing-image" style={{ backgroundImage: `url(${listing.image})` }}>
        <span className="score-badge">AqariX Score {listing.score}</span>
        <button className="save-button" type="button" aria-label={`Save ${listing.title}`} title="Save listing">
          <Heart size={19} aria-hidden="true" />
        </button>
      </div>
      <div className="listing-body">
        <div className="listing-meta">
          <span>{listing.type} / {listing.area}</span>
          <span>{listing.priceSignal}</span>
        </div>
        <div className="listing-title-row">
          <h3>{listing.title}</h3>
          <div>
            <strong>{listing.price}</strong>
            <span>{listing.pricePerSqm}</span>
          </div>
        </div>
        <div className="spec-grid">
          {listing.specs.map((spec) => (
            <span key={spec}>{spec}</span>
          ))}
        </div>
        <div className="recommendation-note">
          <ShieldCheck size={16} aria-hidden="true" />
          <span>{listing.recommendedBecause[0]}</span>
        </div>
        <button className="analysis-button" type="button">
          {viewAnalysis}
          <ArrowRight size={16} aria-hidden="true" />
        </button>
      </div>
    </article>
  )
}

function ListingFeedback({ t }: { t: (typeof copy)[Locale] }) {
  return (
    <form className="feedback-form" aria-label="Listing feedback">
      <h3>{t.improveListing}</h3>
      <div className="feedback-grid">
        {[t.clearDetails, t.usefulPhotos, t.trustworthyPrice, t.enoughLocation].map((label) => (
          <label key={label}>
            <span>{label}</span>
            <select defaultValue="good">
              <option value="good">{t.good}</option>
              <option value="missing">{t.needsWork}</option>
              <option value="unsure">{t.unsure}</option>
            </select>
          </label>
        ))}
      </div>
      <label className="full-field">
        <span>{t.missing}</span>
        <input placeholder={t.missingPlaceholder} />
      </label>
      <button className="secondary-button" type="button">
        <Bookmark size={17} aria-hidden="true" />
        {t.saveFeedback}
      </button>
    </form>
  )
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="metric">
      <span>{label}</span>
      <strong>{value}</strong>
    </div>
  )
}

function Message({ from, text }: { from: string; text: string }) {
  return (
    <div className="message">
      <strong>{from}</strong>
      <p>{text}</p>
    </div>
  )
}

function Task({ label, done = false }: { label: string; done?: boolean }) {
  return (
    <div className={done ? 'task done' : 'task'}>
      <CheckCircle2 size={17} aria-hidden="true" />
      <span>{label}</span>
    </div>
  )
}

function Bar({ label, value }: { label: string; value: number }) {
  return (
    <div className="bar-row">
      <div>
        <span>{label}</span>
        <strong>{value}%</strong>
      </div>
      <div className="bar-track">
        <i style={{ width: `${value}%` }} />
      </div>
    </div>
  )
}

export default App

function mapApiListing(listing: ApiListing): Listing {
  const pricePerSqm = Math.round(listing.asking_price_jod / listing.area_sqm)
  const specs = [
    listing.bedrooms === null ? null : `${listing.bedrooms} beds`,
    listing.bathrooms === null ? null : `${listing.bathrooms} baths`,
    `${listing.area_sqm} sqm`,
  ].filter((value): value is string => Boolean(value))

  return {
    id: listing.id,
    title: listing.title,
    area: listing.neighborhood,
    district: listing.city,
    type: titleCase(listing.property_type),
    price: `JOD ${formatNumber(listing.asking_price_jod)}`,
    pricePerSqm: `JOD ${formatNumber(pricePerSqm)} / sqm`,
    specs,
    score: listing.aqari_score.toFixed(1),
    priceSignal: titleCase(listing.price_signal.replaceAll('_', ' ')),
    confidence: listing.confidence === 'high' ? 'High' : 'Medium',
    image: `${listing.image_url}?auto=format&fit=crop&w=1200&q=80`,
    recommendedBecause: [`Listed in ${listing.neighborhood}`],
    investorNote: 'Listing feedback summary appears here after enough private signals are collected.',
  }
}

function formatNumber(value: number) {
  return new Intl.NumberFormat('en-US').format(value)
}

function titleCase(value: string) {
  return value.replace(/\b\w/g, (match) => match.toUpperCase())
}
