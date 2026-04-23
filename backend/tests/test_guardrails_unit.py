from app.agent.guardrails.competitor_check import find_competitor_mentions, find_placeholders


def test_competitor_detection() -> None:
    text = "We love Nike shoes but not adidas today."
    hits = find_competitor_mentions(text, ["Nike", "Adidas"])
    assert "Nike" in hits
    assert "Adidas" in hits


def test_placeholder_detection() -> None:
    text = "Hi [Insert Name Here] ... please TODO soon"
    ph = find_placeholders(text)
    assert any("Insert Name Here" in p for p in ph)
    assert "..." in ph or any("TODO" in p for p in ph)
