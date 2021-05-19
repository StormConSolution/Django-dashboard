from urllib import parse
def getFiltersSQL(request):
    where_clauses = []
    dateFrom = request.GET.get("date-from")
    dateTo = request.GET.get("date-to")
    if not dateFrom:
        dateFrom = ""
    if not dateTo:
        dateTo = ""
    filters = []
    if dateFrom != "" :
        filters.append("dd.date_created > '" + dateFrom + "'")
        where_clauses.append("dd.date_created >= '" + dateFrom + "'")
    if dateTo != "":
        filters.append("dd.date_created <= '" + dateTo + "'")
        where_clauses.append("dd.date_created <= '" + dateTo + "'")
    filtersSQL = " and ".join(filters)
    if filtersSQL != "":
        filtersSQL = " and " + filtersSQL
    else:
        filtersSQL = ""
    where_clauses = []
    return filtersSQL

def getFiltersSQL2(request):
    where_clauses = []
    dateFrom = request.GET.get("date-from")
    dateTo = request.GET.get("date-to")
    languages =parse.unquote(request.GET.get("languages", "")).split(",")
    #sources = parse.unquote(request.GET.get("sources", "")).split(",")
    sourcesID = request.GET.get("sourcesID", "").split(",")
    if not dateFrom:
        dateFrom = ""
    if not dateTo:
        dateTo = ""
    if dateFrom != "" :
        where_clauses.append("dd.date_created >= '" + dateFrom + "'")
    if dateTo != "":
        where_clauses.append("dd.date_created <= '" + dateTo + "'")
    if languages != ['']:
        map(lambda x: "''%s''" % x, languages)
        where_clauses.append("dd.language in (%s)" % ("'" + "','".join(languages) + "'"))

    #if sources != ['']:
    if sourcesID != ['']:
        #map(lambda x: "''%s''" % x, sources)
        #where_clauses.append('ds."label" in (%s)' % ("'" + "','".join(sources) + "'"))
        where_clauses.append('ds.id in (%s)' % (",".join(sourcesID)))
    return where_clauses

def getWhereClauses(request, where_clauses):
    filter_clauses = getFiltersSQL2(request)
    where_clauses = where_clauses + filter_clauses
    return " and ".join(where_clauses)