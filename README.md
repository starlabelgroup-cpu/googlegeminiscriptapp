# googlegeminiscriptapp

## Overview

This repo currently contains a small helper script that combines Google Ads
data with Gemini (Google generative AI) to identify high-spend, zero-conversion
search terms and generate recommended Negative Keywords.

## Files added

- `scripts/gemini_ads_analysis.py`: Main analysis script.
- `requirements.txt`: Minimum Python dependencies.

## Usage

1. Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

2. Provide credentials:

- Place your `google-ads.yaml` next to the repo root (do not commit it).
- Set `GEMINI_API_KEY` and `TARGET_CUSTOMER_ID` environment variables.

Example run:

```bash
export GEMINI_API_KEY="YOUR_GEMINI_API_KEY"
export TARGET_CUSTOMER_ID="1234567890"
python3 scripts/gemini_ads_analysis.py
```

Notes:

- The script expects `google-ads.yaml` for Google Ads client configuration.
- Keep secrets out of source control; add `google-ads.yaml` to `.gitignore`.
# googlegeminiscriptapp