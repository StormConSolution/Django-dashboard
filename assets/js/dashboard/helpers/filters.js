export function getFilters(){
    let dateFrom = document.getElementById("date-from").value
    let dateTo = document.getElementById("date-to").value
	let sourcesID = $("#sources-filter").val();
	let languages = $("#languages-filter").val();

    return {
        dateFrom: dateFrom,
        dateTo: dateTo,
        sources: "",
        sourcesID: sourcesID.join(","),
        languages: languages.join(",")
    }
}

export function getMetadataFilters(){
/*     let moreFiltersSelects = document.querySelectorAll("[data-role='more-filters-select']")
    let moreFiltersValues = {}
    for(let element of moreFiltersSelects){
        let filterValue = element.value
        if (filterValue != ""){
            moreFiltersValues["filter_" + element.name] = filterValue
        }
    }
 */

    let moreFiltersSelects = document.querySelectorAll("[data-role='metadata-filter']")
    let moreFiltersValues = {}
    for(let element of moreFiltersSelects){
        let filterValue = $(element).val()
        if (filterValue != ""){
            moreFiltersValues["filter_" + element.name] = filterValue.join(",")
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

export function normalFiltersURL(){
    let filters = getFilters()
    let aux = {}
    for(let key in filters){
        switch(key){
            case "dateFrom":
                aux["date-from"] = filters[key]
                break
            case "dateTo":
                aux["date-to"] = filters[key]
                break
            case "languages":
                aux["languages"] = filters[key]
                break
            case "sources":
                aux["sources"] = encodeURIComponent(filters[key])
                break
            case "sourcesID":
                aux["sourcesID"] = filters[key]
                break
        }
    }
    return new URLSearchParams(aux)
}

function getActiveOrderElement(tableElement){
    return tableElement.querySelector("[data-order-by].active")
}

export function orderFilters(tableElement){
    let aux = {}

    let orderElement = getActiveOrderElement(tableElement)
    let orderBy = ""
    let orderRule = ""

    if(orderElement){
        orderBy = orderElement.getAttribute("data-order-by")
        orderRule = orderElement.getAttribute("data-order-rule") 
    }

    aux["order-by"] = orderBy
    aux["order-rule"] = orderRule
    return new URLSearchParams(aux)
}
