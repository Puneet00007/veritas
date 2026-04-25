from veritas.credibility_data import score_for_domain


def test_known_tier1():
    cred, _bias, kind = score_for_domain("reuters.com")
    assert cred >= 0.9
    assert kind == "news"


def test_fact_checker():
    cred, _bias, kind = score_for_domain("snopes.com")
    assert kind == "fact_check"
    assert cred >= 0.85


def test_satire():
    cred, _bias, kind = score_for_domain("theonion.com")
    assert kind == "satire"
    assert cred <= 0.2


def test_low_cred():
    cred, _, _ = score_for_domain("infowars.com")
    assert cred < 0.2


def test_fallback_unknown():
    cred, bias, kind = score_for_domain("somecompletelyunknownsite.example")
    assert cred == 0.5
    assert bias == "unknown"
    assert kind == "news"


def test_gov_domain_heuristic():
    cred, _, kind = score_for_domain("some-agency.gov")
    assert kind == "official"
    assert cred >= 0.8
