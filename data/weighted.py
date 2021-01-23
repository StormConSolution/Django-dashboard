"""
For each data source we have a weighting for to scale its sentiment by reach.
"""
AVG_WEIGHT = 50.0

MAX_SCORE = 100.0

def media(raw_score, alexa):
    if alexa < 100:
        return MAX_SCORE * raw_score
    elif alexa < 1000:
        return 0.6 * MAX_SCORE * raw_score
    elif alexa < 10000:
        return 0.4 * MAX_SCORE * raw_score
    elif alexa < 1000000:
        return 0.2 * MAX_SCORE * raw_score
    else:
        return 0.1 * MAX_SCORE * raw_score

def youtube(raw_score, comments, subscribers, views):
    pass

def youku(raw_score, comments):
    pass

def rolexforums(raw_score, comments):
    pass

def xbiao(raw_score, comments):
    pass

def twitter(raw_score, retweets, followers):
    pass

def reviews(raw_score, comments, starts):
    pass

def default(raw_score):
    return 0.3 * MAX_SCORE * AVG_WEIGHT

def calculate(source, raw_score, *args):
    if source == 'media':
        return media(raw_score, *args)
    else:
        return default(raw_score)
