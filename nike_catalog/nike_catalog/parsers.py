import json
import re
from datetime import datetime, timezone
from html import unescape
from typing import Any

from parsel import Selector


def parse_product_html(html: str, source_url: str) -> dict[str, Any]:
    selector = Selector(text=html)
    product_group = _find_product_json_ld(selector)
    variant = _first_variant(product_group)
    offers = _as_dict(variant.get("offers") or product_group.get("offers"))

    name = _text(variant.get("name")) or _text(product_group.get("name"))
    category = _css_text(selector, '[data-testid="product_subtitle"]::text')
    price = _number(offers.get("price")) or _visible_price(selector)
    currency = _text(offers.get("priceCurrency")) or "IDR"
    sku = _text(variant.get("mpn")) or _visible_after_label(selector, "Style:")
    color = _text(variant.get("color")) or _visible_after_label(selector, "Colour Shown:")
    description = _text(variant.get("description")) or _text(product_group.get("description"))
    image_url = _image(variant.get("image")) or _image(product_group.get("image"))

    return {
        "name": name,
        "brand": _brand(product_group, variant),
        "product_url": _text(product_group.get("url")) or _canonical_product_url(source_url),
        "category": category,
        "gender_or_department": _audience(product_group),
        "price": price,
        "currency": currency,
        "sale_price": _sale_price(selector, price),
        "color": color,
        "sizes": _sizes(selector),
        "availability": _availability(product_group, variant, html),
        "image_url": image_url,
        "description": description,
        "sku": sku,
        "source_url": source_url,
        "fetched_at": datetime.now(timezone.utc).isoformat(),
    }


def _find_product_json_ld(selector: Selector) -> dict[str, Any]:
    candidates: list[dict[str, Any]] = []
    for raw in selector.css('script[type="application/ld+json"]::text').getall():
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            continue
        candidates.extend(_flatten_json_ld(data))

    for item in candidates:
        if item.get("@type") == "ProductGroup":
            return item
    for item in candidates:
        if item.get("@type") == "Product":
            return item
    return {}


def _flatten_json_ld(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        values = [data]
        graph = data.get("@graph")
        if isinstance(graph, list):
            values.extend(x for x in graph if isinstance(x, dict))
        return values
    if isinstance(data, list):
        values: list[dict[str, Any]] = []
        for item in data:
            values.extend(_flatten_json_ld(item))
        return values
    return []


def _first_variant(product_group: dict[str, Any]) -> dict[str, Any]:
    variants = product_group.get("hasVariant")
    if isinstance(variants, list) and variants:
        return _as_dict(variants[0])
    return product_group


def _brand(product_group: dict[str, Any], variant: dict[str, Any]) -> str | None:
    brand = variant.get("brand") or product_group.get("brand")
    if isinstance(brand, dict):
        return _text(brand.get("name"))
    return _text(brand) or "Nike"


def _audience(product_group: dict[str, Any]) -> str | None:
    audience = _as_dict(product_group.get("audience"))
    gender = _text(audience.get("suggestedGender"))
    if gender and gender.startswith("https://schema.org/"):
        gender = gender.rsplit("/", 1)[-1]
    return gender


def _availability(product_group: dict[str, Any], variant: dict[str, Any], html: str) -> str | None:
    offers = _as_dict(variant.get("offers") or product_group.get("offers"))
    availability = _text(offers.get("availability"))
    if availability:
        if "OutOfStock" in availability:
            return "Sold out"
        if "InStock" in availability:
            return "In stock"
        return availability.rsplit("/", 1)[-1]
    if re.search(r"\bSold Out\b", html, re.I):
        return "Sold out"
    return "In stock"


def _sizes(selector: Selector) -> list[str]:
    values = []
    for text in selector.css('[data-testid*="size"]::text').getall():
        text = _clean(text)
        if text and not re.search(r"size|error|select", text, re.I):
            values.append(text)
    return sorted(set(values))


def _sale_price(selector: Selector, price: float | int | None) -> float | None:
    prices = [_number(text) for text in selector.css('[data-testid*="Price"]::text').getall()]
    prices = [value for value in prices if value is not None]
    unique = sorted(set(prices))
    if price is not None and len(unique) > 1:
        return min(unique)
    return None


def _visible_price(selector: Selector) -> float | None:
    for text in selector.css('[data-testid="currentPrice-container"]::text').getall():
        value = _number(text)
        if value is not None:
            return value
    return None


def _visible_after_label(selector: Selector, label: str) -> str | None:
    text = " ".join(selector.css("body ::text").getall())
    match = re.search(re.escape(label) + r"\s*([^|]+?)(?:\s{2,}|$)", text)
    return _clean(match.group(1)) if match else None


def _css_text(selector: Selector, query: str) -> str | None:
    return _clean(selector.css(query).get())


def _image(value: Any) -> str | None:
    if isinstance(value, list) and value:
        return _text(value[0])
    return _text(value)


def _canonical_product_url(source_url: str) -> str:
    return source_url.split("?", 1)[0].rsplit("/", 1)[0] if re.search(r"/[A-Z0-9]{6}-\d{3}$", source_url) else source_url.split("?", 1)[0]


def _as_dict(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def _text(value: Any) -> str | None:
    return _clean(value) if isinstance(value, str) else None


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = re.sub(r"\s+", " ", unescape(value)).strip()
    return cleaned or None


def _number(value: Any) -> float | int | None:
    if isinstance(value, (int, float)):
        return value
    if not isinstance(value, str):
        return None
    digits = re.sub(r"[^\d.,]", "", value)
    if not digits:
        return None
    normalized = digits.replace(".", "").replace(",", ".")
    number = float(normalized)
    return int(number) if number.is_integer() else number
