import { useEffect, useState } from 'react'

// ============================================================
// 🎨 BUSINESS CONFIG — Fill in these ~20 fields, ship it.
// ============================================================
const config = {
  // ── Business Identity ────────────────────────────────────
  businessName: "Summit Pro Services",
  tagline: "Fast. Reliable. Done Right.",
  subTagline: "Serving homeowners & businesses in the metro area since 2008.",
  city: "Austin, TX",
  phone: "(512) 555-0192",
  email: "hello@summitproservices.com",
  address: "4821 Burnet Rd, Austin, TX 78756",
  hours: "Mon–Fri 7am–7pm · Sat 8am–4pm",

  // ── Hero Section ─────────────────────────────────────────
  heroHeadline: "Austin's Most Trusted",
  heroHighlight: "Plumbing & Repair",   // appears in accent color / gradient
  heroCTA: "Get a Free Quote",
  heroSecondary: "See Our Work",
  heroBadges: [
    "Licensed & Insured",
    "Same-Day Service",
    "100% Satisfaction Guarantee",
  ],
  heroStats: [
    { value: "15+", label: "Years in Business" },
    { value: "4,800+", label: "Jobs Completed" },
    { value: "4.9★", label: "Google Rating" },
  ],

  // ── Services ─────────────────────────────────────────────
  servicesHeadline: "What We Do",
  servicesSubtitle: "From small repairs to full installations — we handle it all with the same level of care.",
  services: [
    {
      icon: "🔧",
      name: "Pipe Repair & Installation",
      description: "Leaks, bursts, re-piping, and new installs. We use only code-compliant materials and back every job with a 2-year warranty.",
      tag: "Most Popular",
    },
    {
      icon: "🚿",
      name: "Drain Cleaning",
      description: "Slow drains, full clogs, and hydro-jetting for stubborn buildup. We diagnose first, then fix — no surprise charges.",
      tag: null,
    },
    {
      icon: "🔥",
      name: "Water Heater Services",
      description: "Repair, replacement, and tankless upgrades. Most installs completed the same day you call.",
      tag: "Fast Turnaround",
    },
    {
      icon: "🏠",
      name: "Fixture Replacement",
      description: "Faucets, toilets, showerheads, and garbage disposals. We supply the parts or work with what you've chosen.",
      tag: null,
    },
    {
      icon: "🌊",
      name: "Sewer Line Inspection",
      description: "Camera inspection and full sewer line diagnosis. Catch problems before they become expensive emergencies.",
      tag: null,
    },
    {
      icon: "⚡",
      name: "Emergency Service",
      description: "Urgent issues don't wait for business hours. We offer priority scheduling for flooding, gas smells, or complete outages.",
      tag: "24hr Priority",
    },
  ],

  // ── About / Trust Section ────────────────────────────────
  aboutHeadline: "Why Customers Choose Us",
  aboutText: "We started Summit Pro in 2008 with one truck and a simple promise: show up on time, do the job right, and be honest about the bill. Fifteen years later, that's still how we operate. Our team is fully licensed, background-checked, and trained to solve problems — not upsell you on things you don't need.",
  aboutHighlights: [
    { icon: "🛡️", title: "Licensed & Insured", desc: "Fully covered. You're protected." },
    { icon: "⏱️", title: "On-Time Guarantee", desc: "We call 30 min before arrival." },
    { icon: "💰", title: "Upfront Pricing", desc: "No surprise fees. Ever." },
    { icon: "🏆", title: "Warranty on Work", desc: "2-year labor guarantee." },
  ],
  certifications: ["TSBPE Licensed", "BBB A+ Rated", "Angi Super Service", "Google Guaranteed"],

  // ── Reviews Section ──────────────────────────────────────
  reviewsHeadline: "What Our Customers Say",
  reviewsSubtitle: "Over 400 five-star reviews on Google. Here's a taste.",
  reviews: [
    {
      name: "Maria T.",
      location: "South Austin",
      rating: 5,
      text: "Showed up in under 2 hours when our water heater burst. Fixed it same day, explained everything, left the place spotless. Couldn't ask for more.",
      service: "Water Heater Replacement",
    },
    {
      name: "James K.",
      location: "Cedar Park",
      rating: 5,
      text: "Called three plumbers before Summit — the other quotes were double the price for the same job. Honest, fast, and the work held up perfectly six months later.",
      service: "Pipe Repair",
    },
    {
      name: "Sandra L.",
      location: "Round Rock",
      rating: 5,
      text: "The tech walked me through exactly what was wrong with my drain and why. I felt educated, not taken advantage of. This is how all tradespeople should operate.",
      service: "Drain Cleaning",
    },
  ],

  // ── Contact / Footer ─────────────────────────────────────
  contactHeadline: "Ready to Get Started?",
  contactSubtitle: "Call us now for same-day service, or fill out the form and we'll reach out within the hour.",
  footerTagline: "Serving Austin since 2008. Licensed, insured, and proud of it.",
  socialLinks: {
    facebook: "https://facebook.com/",
    instagram: "https://instagram.com/",
    google: "https://google.com/maps",
  },

  // ── Brand Colors (hex) ───────────────────────────────────
  // Change these to instantly re-skin the site for any client.
  colors: {
    brand: {
      50:  "#eff6ff",
      100: "#dbeafe",
      200: "#bfdbfe",
      300: "#93c5fd",
      400: "#60a5fa",
      500: "#3b82f6",
      600: "#2563eb",
      700: "#1d4ed8",
      800: "#1e3a8a",
      900: "#1e3a5f",
    },
    accent: {
      400: "#fb923c",
      500: "#f97316",
      600: "#ea580c",
    },
  },
}
// ============================================================
// END CONFIG — everything below is template code.
// ============================================================


// ── Inject CSS variables from config ─────────────────────────
function injectColorVars(colors) {
  const root = document.documentElement
  Object.entries(colors.brand).forEach(([k, v]) => {
    root.style.setProperty(`--color-brand-${k}`, v)
  })
  Object.entries(colors.accent).forEach(([k, v]) => {
    root.style.setProperty(`--color-accent-${k}`, v)
  })
}


// ── Icons (inline SVG — zero deps) ───────────────────────────
const PhoneIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.79 19.79 0 0 1-8.63-3.07A19.5 19.5 0 0 1 4.69 12 19.79 19.79 0 0 1 1.61 3.35 2 2 0 0 1 3.6 1h3a2 2 0 0 1 2 1.72c.127.96.361 1.903.7 2.81a2 2 0 0 1-.45 2.11L7.91 8.65a16 16 0 0 0 5.94 5.94l.94-.94a2 2 0 0 1 2.11-.45c.907.339 1.85.573 2.81.7A2 2 0 0 1 22 16.92z"/>
  </svg>
)

const MailIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect width="20" height="16" x="2" y="4" rx="2"/>
    <path d="m22 7-8.97 5.7a1.94 1.94 0 0 1-2.06 0L2 7"/>
  </svg>
)

const MapPinIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/>
    <circle cx="12" cy="10" r="3"/>
  </svg>
)

const ClockIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-5 h-5" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <circle cx="12" cy="12" r="10"/>
    <polyline points="12 6 12 12 16 14"/>
  </svg>
)

const CheckIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <polyline points="20 6 9 17 4 12"/>
  </svg>
)

const ArrowRightIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M5 12h14"/><path d="m12 5 7 7-7 7"/>
  </svg>
)

const MenuIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <line x1="4" x2="20" y1="12" y2="12"/><line x1="4" x2="20" y1="6" y2="6"/><line x1="4" x2="20" y1="18" y2="18"/>
  </svg>
)

const XIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-6 h-6" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M18 6 6 18"/><path d="m6 6 12 12"/>
  </svg>
)

const StarIcon = ({ filled = true }) => (
  <svg xmlns="http://www.w3.org/2000/svg" className="w-4 h-4" viewBox="0 0 24 24" fill={filled ? "currentColor" : "none"} stroke="currentColor" strokeWidth="1.5">
    <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/>
  </svg>
)


// ── Navbar ────────────────────────────────────────────────────
function Navbar() {
  const [scrolled, setScrolled] = useState(false)
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20)
    window.addEventListener('scroll', onScroll)
    return () => window.removeEventListener('scroll', onScroll)
  }, [])

  const navLinks = [
    { href: '#services', label: 'Services' },
    { href: '#about', label: 'About' },
    { href: '#reviews', label: 'Reviews' },
    { href: '#contact', label: 'Contact' },
  ]

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-white/95 backdrop-blur-md shadow-sm border-b border-gray-100'
          : 'bg-transparent'
      }`}
    >
      <nav className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16 lg:h-20">
          {/* Logo */}
          <a href="#" className="flex items-center gap-2 flex-shrink-0">
            <div className="w-8 h-8 rounded-lg hero-gradient flex items-center justify-center">
              <span className="text-white font-extrabold text-sm">
                {config.businessName.charAt(0)}
              </span>
            </div>
            <span className={`font-bold text-lg transition-colors ${scrolled ? 'text-gray-900' : 'text-white'}`}>
              {config.businessName}
            </span>
          </a>

          {/* Desktop links */}
          <div className="hidden md:flex items-center gap-8">
            {navLinks.map(link => (
              <a
                key={link.href}
                href={link.href}
                className={`text-sm font-medium transition-colors hover:opacity-80 ${
                  scrolled ? 'text-gray-600 hover:text-gray-900' : 'text-white/80 hover:text-white'
                }`}
              >
                {link.label}
              </a>
            ))}
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center gap-3">
            <a
              href={`tel:${config.phone.replace(/[^+\d]/g, '')}`}
              className={`flex items-center gap-2 text-sm font-semibold transition-colors ${
                scrolled ? 'text-brand-600 hover:text-brand-700' : 'text-white hover:text-white/80'
              }`}
            >
              <PhoneIcon />
              {config.phone}
            </a>
            <a href="#contact" className="btn-primary text-sm px-4 py-2.5 rounded-lg">
              Free Quote
            </a>
          </div>

          {/* Mobile menu button */}
          <button
            className={`md:hidden transition-colors ${scrolled ? 'text-gray-700' : 'text-white'}`}
            onClick={() => setMobileOpen(!mobileOpen)}
            aria-label="Toggle menu"
          >
            {mobileOpen ? <XIcon /> : <MenuIcon />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileOpen && (
          <div className="md:hidden bg-white border-t border-gray-100 py-4 space-y-1">
            {navLinks.map(link => (
              <a
                key={link.href}
                href={link.href}
                className="block px-4 py-3 text-gray-700 font-medium hover:bg-gray-50 rounded-lg transition-colors"
                onClick={() => setMobileOpen(false)}
              >
                {link.label}
              </a>
            ))}
            <div className="pt-3 px-4 space-y-2 border-t border-gray-100 mt-3">
              <a
                href={`tel:${config.phone.replace(/[^+\d]/g, '')}`}
                className="flex items-center gap-2 text-brand-600 font-semibold py-2"
              >
                <PhoneIcon />
                {config.phone}
              </a>
              <a href="#contact" className="btn-primary w-full text-sm justify-center rounded-lg py-3">
                Get a Free Quote
              </a>
            </div>
          </div>
        )}
      </nav>
    </header>
  )
}


// ── Hero Section ──────────────────────────────────────────────
function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center hero-gradient overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-[0.04]" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      }} />

      {/* Radial glow */}
      <div className="absolute top-1/4 right-1/4 w-[600px] h-[600px] rounded-full opacity-20 blur-3xl"
        style={{ background: 'var(--color-brand-400)' }} />

      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 pt-24 pb-20 lg:pt-32">
        <div className="grid lg:grid-cols-2 gap-12 items-center">

          {/* Left: Copy */}
          <div className="text-white space-y-8">
            {/* City badge */}
            <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-sm rounded-full border border-white/20 text-sm font-medium">
              <MapPinIcon />
              <span>{config.city}</span>
            </div>

            {/* Headline */}
            <div>
              <h1 className="text-4xl sm:text-5xl lg:text-6xl font-extrabold leading-tight tracking-tight">
                {config.heroHeadline}{' '}
                <span className="block" style={{ color: 'var(--color-accent-400)' }}>
                  {config.heroHighlight}
                </span>
              </h1>
              <p className="mt-5 text-xl text-white/80 leading-relaxed max-w-lg">
                {config.subTagline}
              </p>
            </div>

            {/* Trust badges */}
            <div className="flex flex-wrap gap-3">
              {config.heroBadges.map((badge, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 bg-white/10 border border-white/20 rounded-lg text-sm font-medium text-white"
                >
                  <CheckIcon />
                  {badge}
                </span>
              ))}
            </div>

            {/* CTAs */}
            <div className="flex flex-col sm:flex-row gap-4">
              <a href="#contact" className="btn-primary text-base">
                {config.heroCTA}
                <ArrowRightIcon />
              </a>
              <a href="#services" className="btn-secondary text-base">
                {config.heroSecondary}
              </a>
            </div>

            {/* Phone inline */}
            <a
              href={`tel:${config.phone.replace(/[^+\d]/g, '')}`}
              className="inline-flex items-center gap-3 group"
            >
              <div className="w-10 h-10 rounded-full flex items-center justify-center animate-pulse-ring"
                style={{ background: 'var(--color-accent-500)' }}>
                <PhoneIcon />
              </div>
              <div>
                <p className="text-xs text-white/60 font-medium">Call or text anytime</p>
                <p className="text-lg font-bold text-white group-hover:opacity-80 transition-opacity">
                  {config.phone}
                </p>
              </div>
            </a>
          </div>

          {/* Right: Stats card */}
          <div className="hidden lg:flex justify-end">
            <div className="relative">
              {/* Main card */}
              <div className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-3xl p-8 w-80 space-y-6">
                <div className="text-white font-semibold text-lg">
                  Why customers choose us
                </div>
                <div className="grid grid-cols-3 gap-4">
                  {config.heroStats.map((stat, i) => (
                    <div key={i} className="text-center">
                      <div className="text-3xl font-extrabold text-white">{stat.value}</div>
                      <div className="text-xs text-white/60 mt-1 leading-tight">{stat.label}</div>
                    </div>
                  ))}
                </div>
                <div className="border-t border-white/20 pt-4 space-y-3">
                  {config.heroBadges.map((badge, i) => (
                    <div key={i} className="flex items-center gap-3">
                      <div className="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0"
                        style={{ background: 'var(--color-accent-500)' }}>
                        <CheckIcon />
                      </div>
                      <span className="text-sm text-white/80">{badge}</span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Floating review pill */}
              <div className="absolute -bottom-6 -left-8 bg-white rounded-2xl shadow-xl px-4 py-3 flex items-center gap-3 animate-float">
                <div className="flex gap-0.5 stars">
                  {[...Array(5)].map((_, i) => <StarIcon key={i} />)}
                </div>
                <div>
                  <div className="text-xs font-semibold text-gray-900">4.9 / 5.0</div>
                  <div className="text-xs text-gray-500">400+ reviews</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Wave bottom */}
      <div className="absolute bottom-0 left-0 right-0">
        <svg viewBox="0 0 1440 60" xmlns="http://www.w3.org/2000/svg" className="w-full">
          <path fill="white" d="M0,40 C360,80 1080,0 1440,40 L1440,60 L0,60 Z"/>
        </svg>
      </div>
    </section>
  )
}


// ── Services Section ──────────────────────────────────────────
function ServicesSection() {
  return (
    <section id="services" className="py-24 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="text-center space-y-4 mb-16">
          <span className="section-label">What We Do</span>
          <h2 className="section-title">{config.servicesHeadline}</h2>
          <p className="section-subtitle mx-auto">{config.servicesSubtitle}</p>
        </div>

        {/* Services grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {config.services.map((service, i) => (
            <ServiceCard key={i} service={service} />
          ))}
        </div>

        {/* Bottom CTA */}
        <div className="mt-14 text-center">
          <p className="text-gray-500 mb-5">Not sure what you need? We'll figure it out together.</p>
          <a href="#contact" className="btn-outline">
            Talk to an Expert <ArrowRightIcon />
          </a>
        </div>
      </div>
    </section>
  )
}

function ServiceCard({ service }) {
  return (
    <div className="card card-hover p-6 group cursor-default">
      <div className="flex items-start justify-between mb-4">
        <div className="text-4xl">{service.icon}</div>
        {service.tag && (
          <span className="inline-block px-2.5 py-1 text-xs font-semibold rounded-full"
            style={{
              background: 'var(--color-brand-50)',
              color: 'var(--color-brand-700)',
              border: '1px solid var(--color-brand-100)',
            }}>
            {service.tag}
          </span>
        )}
      </div>
      <h3 className="text-lg font-bold text-gray-900 mb-2">{service.name}</h3>
      <p className="text-gray-500 text-sm leading-relaxed">{service.description}</p>
      <div className="mt-5 flex items-center gap-1 text-sm font-semibold transition-colors"
        style={{ color: 'var(--color-brand-600)' }}>
        <span>Learn more</span>
        <span className="transform group-hover:translate-x-1 transition-transform"><ArrowRightIcon /></span>
      </div>
    </div>
  )
}


// ── About / Trust Section ─────────────────────────────────────
function AboutSection() {
  return (
    <section id="about" className="py-24" style={{ background: 'var(--color-brand-50)' }}>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-16 items-center">

          {/* Left: Text */}
          <div className="space-y-8">
            <div className="space-y-4">
              <span className="section-label">Our Story</span>
              <h2 className="section-title">{config.aboutHeadline}</h2>
              <p className="text-lg text-gray-600 leading-relaxed">{config.aboutText}</p>
            </div>

            {/* Highlight grid */}
            <div className="grid grid-cols-2 gap-4">
              {config.aboutHighlights.map((item, i) => (
                <div key={i} className="bg-white rounded-2xl p-5 shadow-sm border border-gray-100">
                  <div className="text-2xl mb-3">{item.icon}</div>
                  <div className="font-bold text-gray-900 text-sm">{item.title}</div>
                  <div className="text-gray-500 text-xs mt-1">{item.desc}</div>
                </div>
              ))}
            </div>

            {/* Certifications */}
            <div>
              <p className="text-xs font-semibold text-gray-400 uppercase tracking-wider mb-3">
                Certifications & Recognition
              </p>
              <div className="flex flex-wrap gap-2">
                {config.certifications.map((cert, i) => (
                  <span key={i} className="px-3 py-1.5 bg-white border border-gray-200 rounded-lg text-sm text-gray-600 font-medium shadow-sm">
                    {cert}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Right: Visual accent card */}
          <div className="relative">
            <div className="rounded-3xl overflow-hidden relative"
              style={{ background: 'linear-gradient(135deg, var(--color-brand-700), var(--color-brand-900))' }}>
              <div className="p-10 text-white space-y-8">
                <div className="text-5xl font-extrabold">{config.heroStats[0].value}</div>
                <div className="space-y-2">
                  <p className="text-xl font-semibold">{config.heroStats[0].label}</p>
                  <p className="text-white/70 text-sm">helping homeowners and businesses across {config.city}.</p>
                </div>
                <div className="grid grid-cols-2 gap-6 pt-4 border-t border-white/20">
                  {config.heroStats.slice(1).map((stat, i) => (
                    <div key={i}>
                      <div className="text-3xl font-extrabold text-white">{stat.value}</div>
                      <div className="text-xs text-white/60 mt-1">{stat.label}</div>
                    </div>
                  ))}
                </div>
              </div>
              {/* Decorative circle */}
              <div className="absolute -top-20 -right-20 w-64 h-64 rounded-full opacity-10"
                style={{ background: 'var(--color-brand-400)' }} />
            </div>

            {/* Floating contact card */}
            <div className="mt-4 bg-white rounded-2xl shadow-lg border border-gray-100 p-5">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl hero-gradient flex items-center justify-center flex-shrink-0">
                  <PhoneIcon />
                </div>
                <div>
                  <p className="text-sm font-semibold text-gray-900">Ready to talk?</p>
                  <a
                    href={`tel:${config.phone.replace(/[^+\d]/g, '')}`}
                    className="text-lg font-bold hover:opacity-70 transition-opacity"
                    style={{ color: 'var(--color-brand-600)' }}
                  >
                    {config.phone}
                  </a>
                </div>
                <a href="#contact" className="ml-auto btn-primary text-sm px-4 py-2.5 rounded-xl">
                  Quote
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}


// ── Reviews Section ───────────────────────────────────────────
function ReviewsSection() {
  const stars = Array(5).fill(0)
  return (
    <section id="reviews" className="py-24 bg-white">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center space-y-4 mb-16">
          <span className="section-label">Customer Reviews</span>
          <h2 className="section-title">{config.reviewsHeadline}</h2>
          <p className="section-subtitle mx-auto">{config.reviewsSubtitle}</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {config.reviews.map((review, i) => (
            <ReviewCard key={i} review={review} />
          ))}
        </div>

        {/* Google CTA */}
        <div className="mt-12 text-center">
          <a
            href={config.socialLinks.google}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-3 px-6 py-3.5 bg-white border-2 border-gray-200 hover:border-gray-300 rounded-xl font-semibold text-gray-700 shadow-sm hover:shadow-md transition-all duration-200"
          >
            <svg className="w-5 h-5" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
              <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
              <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
              <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
              <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            Read all reviews on Google
            <ArrowRightIcon />
          </a>
        </div>
      </div>
    </section>
  )
}

function ReviewCard({ review }) {
  return (
    <div className="card p-6 space-y-4">
      <div className="flex items-center gap-1 stars">
        {[...Array(review.rating)].map((_, i) => <StarIcon key={i} />)}
      </div>
      <blockquote className="text-gray-700 text-sm leading-relaxed">
        "{review.text}"
      </blockquote>
      <div className="flex items-center justify-between pt-2 border-t border-gray-100">
        <div>
          <div className="font-semibold text-gray-900 text-sm">{review.name}</div>
          <div className="text-xs text-gray-400 mt-0.5">{review.location}</div>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-full font-medium"
          style={{
            background: 'var(--color-brand-50)',
            color: 'var(--color-brand-700)',
          }}>
          {review.service}
        </span>
      </div>
    </div>
  )
}


// ── Contact / Footer ──────────────────────────────────────────
function ContactSection() {
  const [formState, setFormState] = useState({ name: '', phone: '', email: '', message: '', sent: false })

  const handleSubmit = (e) => {
    e.preventDefault()
    // TODO: Wire to Formspree / EmailJS / backend
    setFormState(prev => ({ ...prev, sent: true }))
  }

  return (
    <section id="contact" className="py-24 hero-gradient relative overflow-hidden">
      {/* Background pattern */}
      <div className="absolute inset-0 opacity-[0.04]" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
      }} />

      <div className="relative max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid lg:grid-cols-2 gap-16">

          {/* Left: Info */}
          <div className="text-white space-y-8">
            <div>
              <span className="inline-block px-4 py-1.5 bg-white/10 border border-white/20 rounded-full text-sm font-semibold mb-4">
                Contact Us
              </span>
              <h2 className="text-4xl font-extrabold leading-tight">{config.contactHeadline}</h2>
              <p className="mt-4 text-white/70 text-lg">{config.contactSubtitle}</p>
            </div>

            <div className="space-y-5">
              <a href={`tel:${config.phone.replace(/[^+\d]/g, '')}`}
                className="flex items-center gap-4 group">
                <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center flex-shrink-0 group-hover:bg-white/20 transition-colors">
                  <PhoneIcon />
                </div>
                <div>
                  <p className="text-xs text-white/50 font-medium uppercase tracking-wide">Phone</p>
                  <p className="text-lg font-bold text-white">{config.phone}</p>
                </div>
              </a>

              <a href={`mailto:${config.email}`}
                className="flex items-center gap-4 group">
                <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center flex-shrink-0 group-hover:bg-white/20 transition-colors">
                  <MailIcon />
                </div>
                <div>
                  <p className="text-xs text-white/50 font-medium uppercase tracking-wide">Email</p>
                  <p className="text-lg font-bold text-white">{config.email}</p>
                </div>
              </a>

              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center flex-shrink-0">
                  <MapPinIcon />
                </div>
                <div>
                  <p className="text-xs text-white/50 font-medium uppercase tracking-wide">Address</p>
                  <p className="text-base font-semibold text-white">{config.address}</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-white/10 border border-white/20 flex items-center justify-center flex-shrink-0">
                  <ClockIcon />
                </div>
                <div>
                  <p className="text-xs text-white/50 font-medium uppercase tracking-wide">Hours</p>
                  <p className="text-base font-semibold text-white">{config.hours}</p>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Form */}
          <div className="bg-white rounded-3xl shadow-2xl p-8">
            {formState.sent ? (
              <div className="h-full flex flex-col items-center justify-center text-center py-8 space-y-4">
                <div className="w-16 h-16 rounded-full flex items-center justify-center text-3xl"
                  style={{ background: 'var(--color-brand-50)' }}>
                  ✓
                </div>
                <h3 className="text-2xl font-bold text-gray-900">We'll be in touch!</h3>
                <p className="text-gray-500">Thanks for reaching out. We typically respond within the hour during business hours.</p>
                <a href={`tel:${config.phone.replace(/[^+\d]/g, '')}`} className="btn-primary mt-4">
                  <PhoneIcon />
                  Or call us now
                </a>
              </div>
            ) : (
              <form onSubmit={handleSubmit} className="space-y-5">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">Get a Free Quote</h3>
                  <p className="text-gray-500 text-sm mt-1">We'll get back to you within 1 hour.</p>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Name *</label>
                    <input
                      type="text"
                      required
                      placeholder="Your name"
                      value={formState.name}
                      onChange={e => setFormState(p => ({ ...p, name: e.target.value }))}
                      className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-900 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                      style={{ '--tw-ring-color': 'var(--color-brand-400)' }}
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1.5">Phone *</label>
                    <input
                      type="tel"
                      required
                      placeholder="(555) 000-0000"
                      value={formState.phone}
                      onChange={e => setFormState(p => ({ ...p, phone: e.target.value }))}
                      className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-900 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">Email</label>
                  <input
                    type="email"
                    placeholder="you@example.com"
                    value={formState.email}
                    onChange={e => setFormState(p => ({ ...p, email: e.target.value }))}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-900 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:border-transparent transition-all"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1.5">How can we help?</label>
                  <textarea
                    rows={4}
                    placeholder="Describe the issue or service you need…"
                    value={formState.message}
                    onChange={e => setFormState(p => ({ ...p, message: e.target.value }))}
                    className="w-full px-4 py-3 rounded-xl border border-gray-200 text-gray-900 text-sm placeholder-gray-400 focus:outline-none focus:ring-2 focus:border-transparent transition-all resize-none"
                  />
                </div>

                <button type="submit" className="btn-primary w-full justify-center text-base py-4">
                  Send Message <ArrowRightIcon />
                </button>

                <p className="text-xs text-gray-400 text-center">
                  Or call us directly at{' '}
                  <a href={`tel:${config.phone.replace(/[^+\d]/g, '')}`}
                    className="font-semibold underline"
                    style={{ color: 'var(--color-brand-600)' }}>
                    {config.phone}
                  </a>
                </p>
              </form>
            )}
          </div>
        </div>
      </div>
    </section>
  )
}


// ── Footer ────────────────────────────────────────────────────
function Footer() {
  const year = new Date().getFullYear()
  return (
    <footer className="bg-gray-950 text-white py-12">
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex flex-col md:flex-row items-center justify-between gap-6">
          {/* Brand */}
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl hero-gradient flex items-center justify-center">
              <span className="text-white font-extrabold text-sm">
                {config.businessName.charAt(0)}
              </span>
            </div>
            <div>
              <div className="font-bold text-base">{config.businessName}</div>
              <div className="text-xs text-gray-400">{config.footerTagline}</div>
            </div>
          </div>

          {/* Links */}
          <nav className="flex flex-wrap justify-center gap-5 text-sm text-gray-400">
            {['#services', '#about', '#reviews', '#contact'].map((href) => (
              <a key={href} href={href} className="hover:text-white transition-colors capitalize">
                {href.replace('#', '')}
              </a>
            ))}
            <a href={`tel:${config.phone.replace(/[^+\d]/g, '')}`} className="hover:text-white transition-colors">
              {config.phone}
            </a>
          </nav>

          {/* Social */}
          <div className="flex items-center gap-3">
            {config.socialLinks.facebook && (
              <SocialLink href={config.socialLinks.facebook} label="Facebook">
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3z"/>
                </svg>
              </SocialLink>
            )}
            {config.socialLinks.instagram && (
              <SocialLink href={config.socialLinks.instagram} label="Instagram">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" strokeWidth="2" viewBox="0 0 24 24">
                  <rect width="20" height="20" x="2" y="2" rx="5" ry="5"/><path d="M16 11.37A4 4 0 1 1 12.63 8 4 4 0 0 1 16 11.37z"/><line x1="17.5" x2="17.51" y1="6.5" y2="6.5"/>
                </svg>
              </SocialLink>
            )}
            {config.socialLinks.google && (
              <SocialLink href={config.socialLinks.google} label="Google">
                <svg className="w-4 h-4" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.94-.49-7-3.85-7-7.93s3.06-7.44 7-7.93v15.86zm2-15.86c1.03.13 2 .45 2.87.93H13v-.93zM13 7h5.24c.25.31.48.65.68 1H13V7zm0 3h6.74c.08.32.15.65.19 1H13v-1zm0 9.93V19h2.87c-.87.48-1.84.8-2.87.93zM18.24 17H13v-1h5.92c-.2.35-.43.69-.68 1zm1.5-3H13v-1h6.93c-.04.35-.11.68-.19 1z"/>
                </svg>
              </SocialLink>
            )}
          </div>
        </div>

        <div className="mt-8 pt-8 border-t border-gray-800 text-center text-xs text-gray-500">
          © {year} {config.businessName}. All rights reserved. · {config.city}
        </div>
      </div>
    </footer>
  )
}

function SocialLink({ href, label, children }) {
  return (
    <a
      href={href}
      target="_blank"
      rel="noopener noreferrer"
      aria-label={label}
      className="w-9 h-9 rounded-lg bg-gray-800 hover:bg-gray-700 flex items-center justify-center text-gray-400 hover:text-white transition-all duration-200"
    >
      {children}
    </a>
  )
}


// ── App Root ──────────────────────────────────────────────────
export default function App() {
  useEffect(() => {
    // Inject color variables from config
    injectColorVars(config.colors)

    // Update document title and meta
    document.title = `${config.businessName} — ${config.tagline}`
    const metaDesc = document.querySelector('meta[name="description"]')
    if (metaDesc) metaDesc.setAttribute('content', `${config.businessName}: ${config.subTagline}`)
    const ogTitle = document.querySelector('meta[property="og:title"]')
    if (ogTitle) ogTitle.setAttribute('content', `${config.businessName} — ${config.tagline}`)
    const ogDesc = document.querySelector('meta[property="og:description"]')
    if (ogDesc) ogDesc.setAttribute('content', config.subTagline)
  }, [])

  return (
    <div className="min-h-screen">
      <Navbar />
      <main>
        <HeroSection />
        <ServicesSection />
        <AboutSection />
        <ReviewsSection />
        <ContactSection />
      </main>
      <Footer />
    </div>
  )
}
