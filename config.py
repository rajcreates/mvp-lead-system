# ─────────────────────────────────────────────
#  MVP Lead System — Configuration
# ─────────────────────────────────────────────

# ── Telegram ──────────────────────────────────
# Reads from environment variable (GitHub Actions secret) if set,
# falls back to hardcoded value for local use.
import os
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "8609095175:AAFp8ElYAdCOINq4Xcdko3-usnUApXFwJ_8")
TELEGRAM_CHAT_ID   = os.environ.get("TELEGRAM_CHAT_ID",   "6809966227")

# ── HIGH SIGNAL: keyword must appear in post TITLE (reduces noise) ───────────
# These are broad phrases that appear in many irrelevant comments/posts.
# System will only alert if the title itself contains these.
HIGH_SIGNAL_TITLE_ONLY = [
    "looking for developer",
    "need a developer",
    "need developer",
    "hire developer",
    "build my app",
    "build a platform",
    "build my startup",
    "startup development",
    "need a tech team",
    "looking for a tech",
    "how much to build",
    "build my idea",
    "need CTO",
    "need a CTO",
]

# ── Funded startup signals (Reddit — founders announce their own raises) ──────
FUNDING_KEYWORDS = [
    "just raised",
    "we raised",
    "closed our seed",
    "closed our round",
    "raised our seed",
    "pre-seed round",
    "seed funding",
    "just closed",
    "announced our funding",
]

# ── Keywords that signal MVP buying intent ────
MONITOR_KEYWORDS = [
    "looking for developer",
    "need a developer",
    "need developer",
    "hire developer",
    "build my MVP",
    "build an MVP",
    "MVP development",
    "MVP developer",
    "technical co-founder",
    "need a CTO",
    "need CTO",
    "build my app",
    "build my startup",
    "build a platform",
    "build a marketplace",
    "build my idea",
    "app development agency",
    "startup development",
    "need a tech team",
    "looking for a tech",
    "software development agency",
    "how much to build",
    "cost to build an app",
    "prototype developer",
    "build a prototype",
    "no-code isn't enough",
    "outgrown no-code",
    "outgrown bubble",
    "beyond no-code",
]

# ── Subreddits to monitor ────────────────────
# Only BUYER subreddits — removed r/forhire and r/slavelabour
# (those are people offering services, not looking to buy)
SUBREDDITS = [
    "startups",
    "entrepreneur",
    "Entrepreneur",
    "SaaS",
    "indiehackers",
    "nocode",
    "smallbusiness",
    "growmybusiness",
    "business",
    "venturecapital",
    "startup",
    "cofounder",
    "sideproject",
    "EntrepreneurRideAlong",
]

# ── Hacker News tags to search ───────────────
HN_TAGS = ["story", "comment"]

# ── How far back to look (hours) ────────────
LOOKBACK_HOURS = 24

# ── Outbound: Funded Startup Filters ─────────
TARGET_FUNDING_STAGES = ["pre-seed", "seed", "series-a"]
TARGET_COUNTRIES      = ["United States", "United Kingdom"]
TARGET_INDUSTRIES     = [
    "software", "saas", "marketplace", "fintech", "healthtech",
    "edtech", "proptech", "ecommerce", "logistics", "ai",
    "mobile", "platform", "app",
]

# ── FB Ad Library: Intent keywords ───────────
AD_LIBRARY_KEYWORDS = [
    "join our waitlist",
    "coming soon",
    "early access",
    "beta testers",
    "launching soon",
    "join the waitlist",
    "get early access",
    "be the first",
    "founding members",
]
AD_LIBRARY_COUNTRIES = ["US", "GB"]
