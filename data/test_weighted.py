from .weighted import calculate

def test_media():
    w = calculate('media', 0.975, 75)
    assert w > 0

def test_unknown_source():
    w = calculate('xxx', 0.975)
    assert w > 0
