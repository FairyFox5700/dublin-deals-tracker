from dublin_deals.core import Offer, deduplicate, qualifies, rank_offers


def test_qualifies_accepts_free_and_sub_limit_dublin_offer():
    assert qualifies(Offer("Free class", "fitness", "Dublin 4", 0, "https://x.test"), 25)
    assert qualifies(Offer("Match", "sports", "Tallaght, Dublin", 21.5, "https://x.test"), 25)


def test_qualifies_rejects_over_limit_or_non_dublin_offer():
    assert not qualifies(Offer("Spa", "wellness", "Dublin 2", 25.01, "https://x.test"), 25)
    assert not qualifies(Offer("Concert", "entertainment", "Cork", 10, "https://x.test"), 25)


def test_qualifies_rejects_competitions_and_giveaways():
    competition = Offer(
        "Win concert tickets",
        "entertainment",
        "Dublin",
        0,
        "https://x.test",
        terms="Enter the prize draw",
    )
    assert not qualifies(competition, 25)


def test_deduplicate_keeps_cheapest_version_of_same_offer():
    offers = [
        Offer("Yoga Intro", "fitness", "Dublin 4", 10, "https://a.test"),
        Offer(" yoga  intro ", "fitness", "Dublin 4", 5, "https://b.test"),
    ]
    result = deduplicate(offers)
    assert len(result) == 1
    assert result[0].price_eur == 5


def test_rank_prioritises_free_current_reliable_offers():
    free = Offer("Free class", "fitness", "Dublin 2", 0, "https://official.test", source_reliability=10, freshness=10)
    paid = Offer("Paid class", "fitness", "Dublin 2", 20, "https://other.test", source_reliability=5, freshness=5)
    assert rank_offers([paid, free])[0] == free
