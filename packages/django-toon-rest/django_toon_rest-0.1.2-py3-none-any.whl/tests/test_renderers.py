"""
Unit tests for TOONRenderer.
"""

from decimal import Decimal

import pytest

from django_toon_rest.renderers import TOONRenderer


def render_to_text(data):
    renderer = TOONRenderer()
    output = renderer.render(data)
    assert isinstance(output, (bytes, bytearray))
    return output.decode("utf-8")


def test_render_none_returns_empty_bytes():
    renderer = TOONRenderer()
    assert renderer.render(None) == b""


def test_render_simple_dict_produces_toon_text():
    data = {"name": "Alice", "age": 30}
    text = render_to_text(data)
    # Should contain key-value lines in TOON-like form
    assert "name" in text
    assert "Alice" in text
    assert "age" in text
    assert "30" in text


def test_render_list_of_dicts_as_table_uses_pipes():
    data = [
        {"id": 1, "name": "A"},
        {"id": 2, "name": "B"},
    ]
    text = render_to_text(data)
    # Expect table header with pipes and rows
    assert "|" in text
    assert "id" in text and "name" in text
    assert "1" in text and "A" in text
    assert "2" in text and "B" in text


def test_render_converts_decimals_to_float_without_error():
    data = {
        "price": Decimal("9.99"),
        "items": [
            {"subtotal": Decimal("1.25")},
            {"subtotal": Decimal("2.50")},
        ],
    }
    text = render_to_text(data)
    # Ensure it rendered and decimals appeared as floats/strings (no exception)
    assert "9.99" in text
    assert "1.25" in text
    # json-toon normalizes trailing zeros (2.50 -> 2.5)
    assert ("2.50" in text) or ("2.5" in text)

