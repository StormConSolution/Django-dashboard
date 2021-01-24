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
    if comments < 10:
        comments_score = 0
    elif comments < 1000:
        comments_score = 10
    else:
        comments_score = 20
    
    if subscribers < 1000:
        subscribers_score = 0
    elif subscribers < 10000:
        subscribers_score = 5
    elif subscribers < 100000:
        subscribers_score = 15
    elif subscribers < 1000000:
        subscribers_score = 20
    else:
        subscribers_score = 30
    
    if views < 1000:
        views_score = 0
    elif views < 10000:
        views_score = 10
    elif views < 100000:
        views_score = 25
    elif views < 1000000:
        views_score = 30
    else:
        views_score = 50

    return (comments_score + subscribers_score + views_score) * raw_score

def youku(raw_score, comments):
    if comments > 5:
        return 0.7 * MAX_SCORE * raw_score
    else:
        return 0.3 * MAX_SCORE * raw_score

def rolexforums(raw_score, comments):
    if comments < 10:
        return 10 * raw_score
    else:
        return 30 * raw_score

def xbiao(raw_score, comments):
    if comments < 10:
        return 10 * raw_score
    else:
        return 30 * raw_score

def twitter(raw_score, retweets, followers):
    # NOTE for now until we add Twitter
    return default(raw_score)

def reviews(raw_score, comments, stars):
    if comments < 10:
        comments_score = comments
    elif comments < 50:
        comments_score = 25
    else:
       comments_score = 40

    return ((stars * 5) + comments_score) * raw_score

def default(raw_score):
    return 0.3 * MAX_SCORE * AVG_WEIGHT

def calculate(source, raw_score, *args):
    if source == 'media':
        return media(raw_score, *args)
    elif source == 'youtube':
        return youtube(raw_score, *args)
    elif source == 'youku':
        return youku(raw_score, *args)
    elif source == 'rolexforums':
        return rolexforums(raw_score, *args)
    elif source == 'xbiao':
        return xbiao(raw_score, *args)
    elif source == 'reviews':
        return reviews(raw_score, *args)
    elif source == 'twitter':
        return twitter(raw_score, *args)
    else:
        return default(raw_score)
