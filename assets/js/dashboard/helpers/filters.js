export function getFilters(){
    let dateFrom = document.getElementById("date-from").value
    let dateTo = document.getElementById("date-to").value
    let languagesCheckbox = document.querySelectorAll("#dropdown-languages .choose input:checked")
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