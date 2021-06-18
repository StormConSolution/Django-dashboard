export function getFilters(){
    let dateFrom = document.getElementById("date-from").value
    let dateTo = document.getElementById("date-to").value
    let languagesCheckbox = document.querySelectorAll("#dropdown-languages-project-details .choose input:checked")
    let sources = []
    let languages = []
    let sourcesID = []
    for(let languageCheckbox of languagesCheckbox){
        languages.push(languageCheckbox.value)
    }
    let sourcesCheckbox = document.querySelectorAll("#dropdown-sources .choose input:checked")
    for(let sourceCheckbox of sourcesCheckbox){
        sources.push(sourceCheckbox.value)
        sourcesID.push(sourceCheckbox.getAttribute("data-id"))
    }

    return {
        dateFrom: dateFrom,
        dateTo: dateTo,
        sources: "",
        sourcesID: sourcesID.join(","),
        languages: languages.join(",")
    }
}

export function getMetadataFilters(){
    let moreFiltersSelects = document.querySelectorAll("[data-role='more-filters-select']")
    let moreFiltersValues = {}
    for(let element of moreFiltersSelects){
        let filterValue = element.value
        if (filterValue != ""){
            moreFiltersValues["filter_" + element.name] = filterValue
        }
    }
    return moreFiltersValues
}

export function convertFiltersToURL(filters){
    let aux = {}
    for(let key in filters){
        aux[encodeURIComponent(key)] = encodeURIComponent(filters[key])
    }
    let URLParams = new URLSearchParams(aux)
    return URLParams
}

export function metadataFiltersURL(){
    let filters = getMetadataFilters()
    return convertFiltersToURL(filters)
}