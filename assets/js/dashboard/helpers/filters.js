export function getFilters(){
    let dateFrom = document.getElementById("date-from").value
    let dateTo = document.getElementById("date-to").value
    let languagesCheckbox = document.querySelectorAll("#dropdown-languages .choose input:checked")
    let sources = []
    let languages = []
    for(let languageCheckbox of languagesCheckbox){
        languages.push(languageCheckbox.value)
    }
    let sourcesCheckbox = document.querySelectorAll("#dropdown-sources .choose input:checked")
    for(let sourceCheckbox of sourcesCheckbox){
        sources.push(sourceCheckbox.value)
    }
    return {
        dateFrom: dateFrom,
        dateTo: dateTo,
        sources: sources.join(","),
        languages: languages.join(",")
    }
}