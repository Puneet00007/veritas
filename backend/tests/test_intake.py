from veritas.intake import detect_kind, parse_domain
from veritas.schemas import InputKind


def test_detect_kind_text():
    kind, url = detect_kind("The earth is flat")
    assert kind == InputKind.TEXT
    assert url is None


def test_detect_kind_url():
    kind, url = detect_kind("check this https://www.bbc.com/news/article")
    assert kind == InputKind.URL
    assert url.startswith("https://www.bbc.com")


def test_parse_domain():
    assert parse_domain("https://www.reuters.com/world/something") == "reuters.com"
    assert parse_domain("https://theonion.com/foo") == "theonion.com"
