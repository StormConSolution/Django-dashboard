import json

from .weighted import calculate

def test_media():
    w = calculate(source='media', raw_score=0.975, alexa_rank=75)
    assert w > 0

def test_unknown_source():
    w = calculate(source='xxx', raw_score=0.975)
    assert 100 > w > 0

def test_youtube():
    w = calculate(source='youtube', raw_score=0.975, comments=4730, subscribers=97800, views=981000)
    assert 100 > w > 0

def test_kwargs():
    weight_args = {'comments':10, 'subscribers':100, 'views':1000, 'source':'youtube'}
    weight_args['raw_score'] = 0.75

    assert 100 > calculate(**weight_args) > 0
