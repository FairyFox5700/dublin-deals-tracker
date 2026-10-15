from __future__ import annotations

from dataclasses import dataclass, replace
import re


@dataclass(frozen=True, slots=True)
class Offer:
    title: str
    category: str
    location: str
    price_eur: float
    url: str
    source_reliability: float = 7.0
    freshness: float = 7.0
    savings: float = 5.0
    convenience: float = 7.0
    novelty: float = 5.0
    terms: str = ""
    date: str | None = None


def qualifies(offer: Offer, max_price: float = 25.0) -> bool:
    location = offer.location.casefold()
    in_dublin = "dublin" in location or "dún laoghaire" in location or "dun laoghaire" in location or "tallaght" in location
    promotional_text = f"{offer.title} {offer.terms}".casefold()
    is_competition = bool(re.search(r"\b(win|competition|giveaway|prize draw|chance to win)\b", promotional_text))
    return (
        in_dublin
        and not is_competition
        and 0 <= offer.price_eur <= max_price
        and offer.url.startswith(("http://", "https://"))
    )


def _key(offer: Offer) -> tuple[str, str]:
    title = re.sub(r"[^a-z0-9]+", " ", offer.title.casefold()).strip()
    return title, offer.category.casefold().strip()


def deduplicate(offers: list[Offer]) -> list[Offer]:
    best: dict[tuple[str, str], Offer] = {}
    for offer in offers:
        key = _key(offer)
        current = best.get(key)
        if current is None or offer.price_eur < current.price_eur:
            best[key] = offer
    return list(best.values())


def score(offer: Offer) -> float:
    price_value = 10.0 if offer.price_eur == 0 else max(0.0, 10.0 - offer.price_eur / 2.5)
    savings = max(offer.savings, price_value)
    return round(
        offer.freshness * 0.30
        + savings * 0.25
        + offer.source_reliability * 0.20
        + offer.convenience * 0.15
        + offer.novelty * 0.10,
        3,
    )


def rank_offers(offers: list[Offer]) -> list[Offer]:
    return sorted(offers, key=lambda offer: (-score(offer), offer.price_eur, offer.title.casefold()))
