import * as graphs from "./dashboard/graphs";
import * as tables from "./dashboard/tables";
import { getFilters } from "./dashboard/helpers/filters";

function updateProjectTables(){
    tables.aspectTopicTable(1)
    tables.dataTable(1)
    tables.entityTable(1)
}
function updateGraphs(){
    graphs.aspectBySentimentGraph()
    graphs.aspectCountGraph()
    graphs.coOccurrenceGraph()
    graphs.overallSentimentGraph()
    graphs.sentimentTrendGraph()
    graphs.volumeBySourceGraph()
}

function updateProjectDetailsPage(){
    updateProjectTables()
    updateGraphs()
}

updateProjectDetailsPage()

document.getElementById("date-from").addEventListener("change", (e)=>{
    updateProjectDetailsPage()
})

document.getElementById("date-to").addEventListener("change", (e)=>{
    updateProjectDetailsPage()
})

let languagesCheckbox = document.querySelectorAll("#dropdown-languages .choose input")
for(let languageCheckbox of languagesCheckbox){
    languageCheckbox.addEventListener("change", (e)=>{
        updateProjectDetailsPage()
    })
}
let sourcesCheckbox = document.querySelectorAll("#dropdown-sources .choose input")
for(let sourceCheckbox of sourcesCheckbox){
    sourceCheckbox.addEventListener("change", (e)=>{
        updateProjectDetailsPage()
    })
}