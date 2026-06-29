from pathlib import Path

from nike_catalog.parsers import parse_product_html


def test_parse_nike_product_fixture_required_fields():
    html = Path("fixtures/nike_product_fixture.html").read_text(encoding="utf-8")
    item = parse_product_html(
        html,
        "https://www.nike.com/id/t/academy-erling-haaland-football-ERATCGJV",
    )

    assert item["name"] == "Nike Academy 'Erling Haaland' Football - Green Strike/Flash Crimson/Black"
    assert item["brand"] == "Nike"
    assert item["product_url"] == "https://www.nike.com/id/t/academy-erling-haaland-football-ERATCGJV"
    assert item["category"] == "Football"
    assert item["gender_or_department"] == "Unisex"
    assert item["price"] == 439000
    assert item["currency"] == "IDR"
    assert item["sale_price"] is None
    assert item["color"] == "Green Strike/Flash Crimson/Black"
    assert item["sizes"] == []
    assert item["availability"] == "In stock"
    assert item["image_url"].startswith("https://static.nike.com/")
    assert item["description"]
    assert item["sku"] == "IR4337-398"
    assert item["source_url"].startswith("https://www.nike.com/id/t/")
    assert item["fetched_at"]
