from dublin_deals.tracker import collect
from dublin_deals.report import render_markdown


def test_collect_fetches_sources_filters_and_ranks():
    sources = [
        {"name": "Fitness", "url": "https://example.test/fitness", "category": "fitness", "reliability": 9},
        {"name": "Spa", "url": "https://example.test/spa", "category": "wellness", "reliability": 8},
    ]
    pages = {
        "https://example.test/fitness": "<article><h2>Free Dublin yoga class</h2><p>Dublin 4</p></article>",
        "https://example.test/spa": "<article><h2>Spa day</h2><p>Dublin 2 €70</p></article>",
    }

    offers, failures = collect(sources, fetcher=lambda url: pages[url], max_price=25)

    assert failures == []
    assert [offer.title for offer in offers] == ["Free Dublin yoga class"]
    assert offers[0].source_reliability == 9


def test_collect_records_failed_source_without_losing_good_results():
    sources = [
        {"name": "Broken", "url": "https://bad.test", "category": "sports"},
        {"name": "Good", "url": "https://good.test", "category": "sports"},
    ]

    def fetch(url):
        if "bad" in url:
            raise RuntimeError("blocked")
        return "<article><h2>Dublin match</h2><p>Tallaght, Dublin €20</p></article>"

    offers, failures = collect(sources, fetcher=fetch)
    assert len(offers) == 1
    assert failures == ["Broken: blocked"]


def test_collect_uses_verified_offer_when_live_page_matches():
    sources = [{
        "name": "Gym",
        "url": "https://gym.test",
        "category": "fitness",
        "reliability": 10,
        "verified_offer": {
            "title": "Free four-day trial",
            "location": "Dublin 2",
            "price_eur": 0,
            "match_regex": "free\\s+4-day.*trial"
        },
    }]
    offers, failures = collect(sources, fetcher=lambda _: "Claim a FREE 4-day gym trial today")
    assert failures == []
    assert len(offers) == 1
    assert offers[0].title == "Free four-day trial"


def test_collect_skips_verified_offer_when_validation_text_disappears():
    sources = [{
        "name": "Gym",
        "url": "https://gym.test",
        "category": "fitness",
        "verified_offer": {
            "title": "Free trial",
            "location": "Dublin",
            "price_eur": 0,
            "match_regex": "free trial"
        },
    }]
    offers, failures = collect(sources, fetcher=lambda _: "Standard memberships only")
    assert offers == []
    assert failures == []


def test_markdown_report_contains_price_category_and_link():
    sources = [{"name": "Good", "url": "https://good.test", "category": "sports"}]
    offers, _ = collect(
        sources,
        fetcher=lambda _: "<article><h2>Dublin match</h2><p>Tallaght, Dublin €20</p><a href='/tickets'>Tickets</a></article>",
    )
    report = render_markdown(offers, generated_at="2026-10-15T09:00:00Z")
    assert "# Dublin Deals" in report
    assert "€20.00" in report
    assert "sports" in report
    assert "https://good.test/tickets" in report
