# Dublin Deals Tracker

A small Python tracker for free trials and activities costing no more than €25 per person in Dublin and nearby suburbs. It checks fitness, wellness, sports and entertainment sources, verifies known offers against live page text, extracts additional listings, filters competitions and out-of-area results, ranks matches, and produces Markdown and JSON reports.

## Current report

See [`output/report.md`](output/report.md) for the latest generated results.

## Features

- Configurable source list in `config/sources.json`
- Live validation for known promotions using regular expressions
- Generic HTML extraction for event and deal listing pages
- Dublin-location and all-in-price filtering
- Competition/giveaway exclusion
- Deduplication and weighted ranking
- Source failures recorded without discarding good results
- Daily GitHub Actions run plus an independent test workflow
- No API key required

## Install

```bash
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows PowerShell
# .venv\Scripts\Activate.ps1

pip install -e .
```

## Run

```bash
python -m dublin_deals \
  --config config/sources.json \
  --output output \
  --max-price 25 \
  --limit 20
```

Generated files:

- `output/report.md` — readable roundup
- `output/deals.json` — structured offers and source failures

## Configure sources

A generic listing source needs a name, URL and category:

```json
{
  "name": "Example listings",
  "url": "https://example.com/dublin-deals",
  "category": "entertainment",
  "reliability": 8
}
```

For a known promotion, add a declarative live-page check:

```json
{
  "name": "Example gym",
  "url": "https://example.com/trial",
  "category": "fitness",
  "reliability": 10,
  "verified_offer": {
    "title": "Free three-day trial",
    "location": "Dublin 2",
    "price_eur": 0,
    "match_regex": "free.{0,20}three-day.{0,20}trial",
    "terms": "New customers only."
  }
}
```

The verified offer is included only while its regular expression still matches the live page.

## Automation

`.github/workflows/daily.yml` runs at 07:00 UTC and can also be triggered manually. It commits a changed report using the repository's built-in `GITHUB_TOKEN`. Scheduled GitHub Actions times are UTC and may not exactly match Dublin local time around daylight-saving changes.

## Tests

```bash
pip install -e . pytest
pytest -q
```

The suite covers filtering, ranking, deduplication, HTML extraction, source failures, live offer validation and report rendering.

## Limitations

Websites can change markup or block automated clients. Generic extraction is deliberately conservative, while important known promotions use explicit validation rules. Always confirm availability, eligibility and final checkout fees with the provider before travelling or buying.

## License

MIT
