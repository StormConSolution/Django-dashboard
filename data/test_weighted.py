from .weighted import calculate

def test_media():
    w = calculate('media', 0.975, 75)
    assert w > 0

def test_unknown_source():
    w = calculate('xxx', 0.975)
    assert w > 0

def test_youtube():
    w = calculate('youtube', 0.975, 4730, 97800, 981000)
    assert 100 > w > 0
