
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
        where_clauses.append("dd.date_created > '" + dateFrom + "'")
    if dateTo != "":
        filters.append("dd.date_created < '" + dateTo + "'")
        where_clauses.append("dd.date_created < '" + dateTo + "'")
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
    languages = request.GET.get("languages").split(",")
    sources = request.GET.get("sources").split(",")
    if not dateFrom:
        dateFrom = ""
    if not dateTo:
        dateTo = ""
    if dateFrom != "" :
        where_clauses.append("dd.date_created > '" + dateFrom + "'")
    if dateTo != "":
        where_clauses.append("dd.date_created < '" + dateTo + "'")
    map(lambda x: "''%s''" % x, sources)
    map(lambda x: "''%s''" % x, languages)
    where_clauses.append("dd.language in (%s)" % ("'" + "','".join(languages) + "'"))
    where_clauses.append('ds."label" in (%s)' % ("'" + "','".join(sources) + "'"))
    return where_clauses

def getWhereClauses(request, where_clauses):
    filter_clauses = getFiltersSQL2(request)
    where_clauses = where_clauses + filter_clauses
    return " and ".join(where_clauses)