from dublin_deals.extract import extract_offers


HTML = """
<html><body>
<article>
  <h2>First Pilates Class Free</h2>
  <p>67 Mespil Road, Dublin 4. New customers only.</p>
  <a href="/book">Book now</a>
</article>
<article>
  <h2>Sauna session</h2>
  <p>Coal Harbour, Dún Laoghaire, Co. Dublin</p>
  <span>€19.95</span>
  <a href="https://example.test/sauna">Details</a>
</article>
<article>
  <h2>Premium spa day</h2><p>Dublin €85</p>
</article>
</body></html>
"""


def test_extract_offers_finds_free_and_priced_cards():
    offers = extract_offers(HTML, "https://example.test", "wellness")
    by_title = {o.title: o for o in offers}
    assert by_title["First Pilates Class Free"].price_eur == 0
    assert by_title["Sauna session"].price_eur == 19.95
    assert by_title["Sauna session"].url == "https://example.test/sauna"
    assert by_title["Premium spa day"].price_eur == 85


def test_extract_offers_ignores_free_as_part_of_unrelated_word():
    html = "<article><h2>Carefree evening</h2><p>Dublin</p></article>"
    assert extract_offers(html, "https://example.test", "entertainment") == []
