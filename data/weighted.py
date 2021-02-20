"""
For each data source we have a weighting for to scale its sentiment by reach.
"""
AVG_WEIGHT = 50.0

MAX_SCORE = 100.0

def media(source, raw_score, alexa_rank):
    if alexa_rank < 100:
        return MAX_SCORE * raw_score
    elif alexa_rank < 1000:
        return 0.6 * MAX_SCORE * raw_score
    elif alexa_rank < 10000:
        return 0.4 * MAX_SCORE * raw_score
    elif alexa_rank < 1000000:
        return 0.2 * MAX_SCORE * raw_score
    else:
        return 0.1 * MAX_SCORE * raw_score

def youtube(source, raw_score, comments, views):
    if comments < 10:
        comments_score = 10
    elif comments < 1000:
        comments_score = 30
    else:
        comments_score = 40
    
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

    return (comments_score + views_score) * raw_score

def youku(source, raw_score, comments):
    if comments > 5:
        return 0.7 * MAX_SCORE * raw_score
    else:
        return 0.3 * MAX_SCORE * raw_score

def rolexforums(source, raw_score, comments):
    if comments < 10:
        return 10 * raw_score
    else:
        return 30 * raw_score

def xbiao(source, raw_score, comments):
    if comments < 10:
        return 10 * raw_score
    else:
        return 30 * raw_score

def reviews(source, raw_score, comments, stars):
    if comments < 10:
        comments_score = comments
    elif comments < 50:
        comments_score = 25
    else:
       comments_score = 40

    return ((stars * 5) + comments_score) * raw_score

def default(raw_score):
    return 0.5 * AVG_WEIGHT * raw_score

def calculate(**kwargs):
    source = kwargs.get('source')
    if source == 'media':
        return media(**kwargs)
    elif source == 'youtube':
        return youtube(**kwargs)
    elif source == 'youku':
        return youku(**kwargs)
    elif source == 'rolexforums':
        return rolexforums(**kwargs)
    elif source == 'xbiao':
        return xbiao(**kwargs)
    elif source == 'reviews':
        return reviews(**kwargs)
    else:
        return default(kwargs.get('raw_score'))
