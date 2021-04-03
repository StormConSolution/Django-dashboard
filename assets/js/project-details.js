import * as graphs from "./dashboard/graphs";
import * as tables from "./dashboard/tables";
import { getFilters } from "./dashboard/utils/filters";

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