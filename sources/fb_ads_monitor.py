# ─────────────────────────────────────────────
#  Facebook Ad Library Monitor
#  Uses the public Graph API (no auth for basic search)
# ─────────────────────────────────────────────
import requests

# Facebook Ad Library public search endpoint
# Note: Full API requires a Facebook app token.
# This uses the public web search URL and parses what's available.
# For deeper access: get a free Facebook App token at
# developers.facebook.com → create app → Ad Library API access

FB_AD_LIBRARY_URL = "https://www.facebook.com/ads/library/async/search_typeahead/"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


def search_fb_ads_api(keyword: str, countries: list, access_token: str = None) -> list:
    """
    Search Facebook Ad Library via Graph API.
    Requires a Facebook access token for full results.
    Get one free at: developers.facebook.com

    Without token: returns instructions to set up.
    With token: returns active ads matching keyword.
    """
    leads = []

    if not access_token:
        print(
            f"[FB Ads] No access token. To enable:\n"
            f"  1. Go to developers.facebook.com\n"
            f"  2. Create a free app\n"
            f"  3. Request Ad Library API access\n"
            f"  4. Add your token to config.py as FB_ACCESS_TOKEN\n"
            f"  Keyword '{keyword}' skipped."
        )
        return leads

    for country in countries:
        url = (
            "https://graph.facebook.com/v18.0/ads_archive"
            f"?search_terms={requests.utils.quote(keyword)}"
            f"&ad_reached_countries={country}"
            "&ad_type=ALL"
            "&fields=id,page_name,page_id,ad_creative_body,ad_snapshot_url"
            "&limit=25"
            f"&access_token={access_token}"
        )

        try:
            r = requests.get(url, timeout=15)
            if r.status_code != 200:
                print(f"[FB Ads] {r.status_code}: {r.text[:200]}")
                continue

            ads = r.json().get("data", [])

            for ad in ads:
                page_name = ad.get("page_name", "Unknown")
                body      = ad.get("ad_creative_body", "")
                snap_url  = ad.get("ad_snapshot_url", "")
                uid       = f"fbad_{ad.get('id', '')}"

                leads.append({
                    "uid":     uid,
                    "source":  f"FB Ads ({country})",
                    "title":   f"Ad by {page_name}",
                    "body":    body,
                    "url":     snap_url,
                    "keyword": keyword,
                    "page":    page_name,
                })

        except Exception as e:
            print(f"[FB Ads error] {keyword} / {country}: {e}")

    return leads
