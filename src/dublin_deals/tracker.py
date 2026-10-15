from __future__ import annotations

from dataclasses import replace
import re
from typing import Callable

import httpx

from .core import Offer, deduplicate, qualifies, rank_offers
from .extract import extract_offers


USER_AGENT = "DublinDealsTracker/0.1 (+https://github.com/)"


def fetch_page(url: str) -> str:
    with httpx.Client(follow_redirects=True, timeout=25, headers={"User-Agent": USER_AGENT}) as client:
        response = client.get(url)
        response.raise_for_status()
        return response.text


def collect(
    sources: list[dict],
    *,
    fetcher: Callable[[str], str] = fetch_page,
    max_price: float = 25.0,
) -> tuple[list[Offer], list[str]]:
    offers: list[Offer] = []
    failures: list[str] = []
    for source in sources:
        name = source.get("name", source["url"])
        try:
            html = fetcher(source["url"])
            reliability = float(source.get("reliability", 7))
            verified = source.get("verified_offer")
            if verified is not None:
                if re.search(verified["match_regex"], html, flags=re.IGNORECASE | re.DOTALL):
                    offers.append(
                        Offer(
                            title=verified["title"],
                            category=source["category"],
                            location=verified["location"],
                            price_eur=float(verified["price_eur"]),
                            url=verified.get("url", source["url"]),
                            source_reliability=reliability,
                            terms=verified.get("terms", "Validated against the live source page."),
                        )
                    )
                continue
            extracted = extract_offers(html, source["url"], source["category"])
            offers.extend(replace(offer, source_reliability=reliability) for offer in extracted)
        except Exception as exc:
            failures.append(f"{name}: {exc}")
    qualifying = [offer for offer in offers if qualifies(offer, max_price)]
    return rank_offers(deduplicate(qualifying)), failures
