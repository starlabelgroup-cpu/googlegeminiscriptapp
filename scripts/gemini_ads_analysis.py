import os
import sys
import argparse
import yaml
import google.generativeai as genai
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

"""Gemini + Google Ads analysis helper

Usage:
  - Set environment variables `GEMINI_API_KEY` and `TARGET_CUSTOMER_ID`.
  - Place `google-ads.yaml` next to this repository root (or set `PATH_TO_ADS_CONFIG`).
  - Run: `python3 scripts/gemini_ads_analysis.py`

This script finds high-spend, zero-conversion search terms and asks Gemini
to identify likely negatives and provide explanations.
"""

# Config (can be overridden via environment variables)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
PATH_TO_ADS_CONFIG = os.getenv("PATH_TO_ADS_CONFIG", "google-ads.yaml")
TARGET_CUSTOMER_ID = os.getenv("TARGET_CUSTOMER_ID")
CAMPAIGN_CONFIG = os.getenv("CAMPAIGN_CONFIG", "campaign_config.yaml")


def get_wasted_spend_queries(client, customer_id: str):
    ga_service = client.get_service("GoogleAdsService")
    query = """
        SELECT
          search_term_view.search_term,
          metrics.cost_micros,
          metrics.conversions,
          metrics.impressions
        FROM search_term_view
        WHERE metrics.conversions = 0
          AND metrics.cost_micros > 50000000
          AND segments.date DURING LAST_30_DAYS
        ORDER BY metrics.cost_micros DESC
        LIMIT 10
    """

    search_terms = []
    try:
        stream = ga_service.search_stream(customer_id=customer_id, query=query)
        for batch in stream:
            for row in batch.results:
                term = row.search_term_view.search_term
                cost = row.metrics.cost_micros / 1_000_000
                search_terms.append(f"Term: '{term}' (Spent: ${cost:.2f})")
        return search_terms
    except GoogleAdsException as ex:
        print(f"Ads API Error: {ex.error.message}")
        return []


def analyze_with_gemini(terms_list):
    if not terms_list:
        return "No data found to analyze."

    prompt = (
        "You are a Google Ads specialist. Look at these search terms that are costing money "
        "but resulting in zero conversions:\n\n" + "\n".join(terms_list) +
        "\n\nTask:\n1. Identify which terms likely represent 'junk' or 'irrelevant' intent.\n"
        "2. Provide a list of recommended Negative Keywords to add.\n3. Explain briefly why for each."
    )

    if not GEMINI_API_KEY:
        return f"GEMINI_API_KEY not set. Preview prompt to send to Gemini:\n\n{prompt}"

    genai.configure(api_key=GEMINI_API_KEY)
    try:
        model = genai.GenerativeModel('gemini-3-flash-preview')
    except Exception:
        model = genai.GenerativeModel('gemini-3-flash-preview')

    try:
        response = model.generate_content(prompt)
        text = getattr(response, 'text', None)
        if text:
            return text
        return str(response)
    except Exception as e:
        return f"Gemini API error: {e}"


def mock_gemini_response(terms_list):
    """Return a canned Gemini-like analysis for testing and offline use."""
    total_spend = 0.0
    for t in terms_list:
        try:
            spent = float(t.split("$")[-1].strip(')'))
        except Exception:
            spent = 0.0
        total_spend += spent

    lines = [
        "(Mock) Gemini Analysis Summary:\n",
        f"Total simulated spend: ${total_spend:.2f} across {len(terms_list)} terms.\n",
        "Top recommendations:\n",
        "1) Add informational negative keywords: 'how to', 'video', 'manual', 'youtube'.\n",
        "2) Exclude parts & low-value intents: 'parts', 'cheap', 'coupon', 'used'.\n",
        "3) Verify landing page and geo-targeting for high-spend, high-intent keywords.\n\n",
        "Detailed per-term notes:\n",
    ]

    for t in terms_list:
        lines.append(f"- {t}: Likely informational or parts intent; consider adding related negatives.\n")

    lines.append("\nMock closing note: Review negative keyword list and monitor conversions for 7 days.")
    return "".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="Simulate Ads API using campaign_config.yaml")
    parser.add_argument("--mock-gemini", action="store_true", help="Use a canned Gemini-style response instead of calling the API")
    args = parser.parse_args()

    print("--- Starting Gemini Ads Analysis ---")

    if args.dry_run:
        # Load campaign_config.yaml and synthesize search terms
        if not os.path.exists(CAMPAIGN_CONFIG):
            print(f"Dry-run requested but {CAMPAIGN_CONFIG} not found.")
            return
        with open(CAMPAIGN_CONFIG, "r") as f:
            cfg = yaml.safe_load(f)

        terms = []
        ad_groups = cfg.get("ad_groups", [])
        idx = 0
        for ag in ad_groups:
            for kw in ag.get("keywords", []):
                text = kw.get("text") if isinstance(kw, dict) else kw
                if not text:
                    continue
                # simulate spend > $50 by using micros > 50_000_000
                cost_micros = 60_000_000 + (idx * 10_000_000)
                cost = cost_micros / 1_000_000
                terms.append(f"Term: '{text}' (Spent: ${cost:.2f})")
                idx += 1
                if idx >= 10:
                    break
            if idx >= 10:
                break

        print(f"Dry-run: generated {len(terms)} simulated terms from {CAMPAIGN_CONFIG}.")
        print("Terms preview:")
        for t in terms:
            print(" -", t)

        print("\nSending (simulated) terms to Gemini for analysis...")
        if args.mock_gemini:
            analysis = mock_gemini_response(terms)
        else:
            analysis = analyze_with_gemini(terms)
        print("\n--- GEMINI 3 RECOMMENDATIONS (Dry-run) ---")
        print(analysis)
        return

    # Normal (live) flow
    if not TARGET_CUSTOMER_ID:
        print("TARGET_CUSTOMER_ID not set. Set the env var and retry.")
        return

    try:
        ads_client = GoogleAdsClient.load_from_storage(PATH_TO_ADS_CONFIG)
    except Exception as e:
        print(f"Stop: Could not load {PATH_TO_ADS_CONFIG}. Please add it to the folder or set PATH_TO_ADS_CONFIG.")
        return

    print(f"Fetching data for Account {TARGET_CUSTOMER_ID}...")
    bad_queries = get_wasted_spend_queries(ads_client, TARGET_CUSTOMER_ID)

    if bad_queries:
        print(f"Found {len(bad_queries)} terms. Sending to Gemini 3 for review...")
        if args.mock_gemini:
            analysis = mock_gemini_response(bad_queries)
        else:
            analysis = analyze_with_gemini(bad_queries)
        print("\n--- GEMINI 3 RECOMMENDATIONS ---")
        print(analysis)
    else:
        print("No wasted spend detected based on your filters.")


if __name__ == "__main__":
    main()
