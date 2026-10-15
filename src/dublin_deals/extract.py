from __future__ import annotations

import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

from .core import Offer

_PRICE = re.compile(r"€\s*(\d+(?:[.,]\d{1,2})?)")
_FREE = re.compile(r"\bfree\b", re.IGNORECASE)


def _price(text: str) -> float | None:
    match = _PRICE.search(text)
    if match:
        return float(match.group(1).replace(",", "."))
    if _FREE.search(text):
        return 0.0
    return None


def extract_offers(html: str, source_url: str, category: str) -> list[Offer]:
    soup = BeautifulSoup(html, "html.parser")
    for node in soup(["script", "style", "noscript"]):
        node.decompose()

    cards = soup.find_all(["article", "li"])
    if not cards:
        cards = soup.find_all("div", recursive=True)

    offers: list[Offer] = []
    for card in cards:
        text = " ".join(card.stripped_strings)
        price = _price(text)
        if price is None:
            continue
        heading = card.find(["h1", "h2", "h3", "h4"])
        link = card.find("a", href=True)
        if heading:
            title = " ".join(heading.stripped_strings)
        elif link:
            title = " ".join(link.stripped_strings)
        else:
            title = text[:120].strip()
        if not title:
            continue
        url = urljoin(source_url, link["href"]) if link else source_url
        offers.append(
            Offer(
                title=title,
                category=category,
                location=text,
                price_eur=price,
                url=url,
                terms=text[:500],
            )
        )
    return offers
