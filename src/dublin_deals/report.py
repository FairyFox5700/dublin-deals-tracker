from __future__ import annotations

from .core import Offer, score


def render_markdown(offers: list[Offer], *, generated_at: str) -> str:
    lines = ["# Dublin Deals", "", f"Updated: {generated_at}", ""]
    if not offers:
        lines.append("No qualifying free or sub-€25 deals were found.")
        return "\n".join(lines) + "\n"
    for offer in offers:
        price = "Free" if offer.price_eur == 0 else f"€{offer.price_eur:.2f}"
        lines.extend(
            [
                f"## [{offer.title}]({offer.url})",
                f"- **Category:** {offer.category}",
                f"- **Price:** {price}",
                f"- **Match score:** {score(offer):.2f}/10",
                f"- **Location/details:** {offer.location[:300]}",
                "",
            ]
        )
    return "\n".join(lines)
