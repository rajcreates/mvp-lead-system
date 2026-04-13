#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys, io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
# ─────────────────────────────────────────────
#  Outreach Message Generator
#  Run: python outreach_templates.py
#  Reads leads.csv, generates personalized outreach messages
# ─────────────────────────────────────────────
import csv
import os


TEMPLATES = {
    # ── For Reddit / HN posts ─────────────────────────────────────────────────
    "inbound_reddit": """\
Hi {name},

I saw your post about {topic} — are you still looking for a dev team or did you find someone?
""",

    # ── For IndieHackers / HN community posts ─────────────────────────────────
    "inbound_community": """\
Hi {name},

Noticed your question about {topic}.

Have you figured out a solution or are you still working through it?

A) Sorted
B) Still figuring it out

A or B?
""",

    # ── For recently funded startups (Crunchbase) ─────────────────────────────
    "outbound_funded": """\
Subject: MVP for {company}

Hi {name},

Saw {company} just raised {stage} funding — congrats.

We build MVPs for funded startups. 100+ products shipped, most go from idea to launch in 8–12 weeks.

Are you working with a dev team already or still figuring out the build?
""",

    # ── For ProductHunt launches ───────────────────────────────────────────────
    "outbound_launch": """\
Subject: {company} — v2 / next phase

Hi {name},

Saw {company} launched on ProductHunt — great product.

Founders who launch often have a backlog of features they couldn't ship in v1. We help with exactly that.

Is there a next phase you're planning or are you focusing on traction first?
""",

    # ── For FB Ad Library (running waitlist/coming soon ads) ──────────────────
    "outbound_ad": """\
Subject: {company} — building the product

Hi {name},

I saw your ad for {company} — {ad_snippet}

Are you building the product in-house or looking for a team to get it built?

A or B?
""",
}


def generate_messages(leads_file: str = "leads.csv"):
    if not os.path.exists(leads_file):
        print("No leads.csv found. Run monitor.py first.")
        return

    output_file = "outreach_queue.csv"
    headers = ["source", "type", "title", "url", "message", "status"]

    with open(leads_file, newline="", encoding="utf-8") as fin, \
         open(output_file, "w", newline="", encoding="utf-8") as fout:

        reader = csv.DictReader(fin)
        writer = csv.DictWriter(fout, fieldnames=headers)
        writer.writeheader()

        count = 0
        for row in reader:
            lead_type = row.get("type", "")
            source    = row.get("source", "")
            title     = row.get("title", "")
            url       = row.get("url", "")
            snippet   = row.get("snippet", "")

            # Pick template
            if "reddit" in source.lower():
                tpl_key = "inbound_reddit"
                msg = TEMPLATES[tpl_key].format(
                    name  = "[Founder Name]",
                    topic = title[:60],
                )
            elif lead_type == "inbound":
                tpl_key = "inbound_community"
                msg = TEMPLATES[tpl_key].format(
                    name  = "[Founder Name]",
                    topic = title[:60],
                )
            elif lead_type == "outbound_funded":
                tpl_key = "outbound_funded"
                msg = TEMPLATES[tpl_key].format(
                    name    = "[Founder Name]",
                    company = title,
                    stage   = "seed",
                )
            elif lead_type == "outbound_launch":
                tpl_key = "outbound_launch"
                msg = TEMPLATES[tpl_key].format(
                    name    = "[Founder Name]",
                    company = title,
                )
            elif lead_type == "outbound_ad":
                tpl_key = "outbound_ad"
                msg = TEMPLATES[tpl_key].format(
                    name       = "[Founder Name]",
                    company    = title,
                    ad_snippet = snippet[:80],
                )
            else:
                msg = TEMPLATES["inbound_community"].format(
                    name  = "[Founder Name]",
                    topic = title[:60],
                )

            writer.writerow({
                "source":  source,
                "type":    lead_type,
                "title":   title,
                "url":     url,
                "message": msg.strip(),
                "status":  "pending",
            })
            count += 1

    print(f"✓ {count} outreach messages written to {output_file}")
    print("  Open outreach_queue.csv, find the founder on LinkedIn/email, paste the message.")


if __name__ == "__main__":
    generate_messages()
