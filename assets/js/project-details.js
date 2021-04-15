import * as graphs from "./dashboard/graphs";
import * as tables from "./dashboard/tables";
import { getFilters } from "./dashboard/helpers/filters";
import {update, resetGraphsTablesContainer} from './dashboard/helpers/helpers'
let timeOut
let currentTab = "overview-tab"
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
    graphs.volumeBySourceGraph()
}

function updateProjectDetailsPage(){
    if(update.canUpdate()){
        resetGraphsTablesContainer()
        switch(currentTab){
            case "overview-tab":
                graphs.overallSentimentGraph()
                graphs.sentimentTrendGraph()
                break
            case "sentiment-tab":
                break
            case "aspect-tab":
                graphs.aspectCountGraph()
                graphs.aspectBySentimentGraph()
                graphs.coOccurrenceGraph()
                tables.aspectTopicTable(1)
                break
            case "entity-tab":
                tables.entityTable(1)
                break
            case "sources-tab":
                graphs.volumeBySourceGraph()
                tables.dataTable(1)
                break
        }
    } else {
        if(timeOut){
            clearTimeout(timeOut)
        }
        timeOut = setTimeout(updateProjectDetailsPage,1000)
    }
}


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

document.querySelectorAll(".check-all").forEach((element) => {
    element.addEventListener("click", (e)=> {
        
        let parent = e.target.parentNode.parentNode
        
        parent.querySelectorAll("input").forEach((input) => {
            input.checked = true
        })
        updateProjectDetailsPage()
    })
})

document.querySelectorAll(".uncheck-all").forEach((element) => {
    element.addEventListener("click", (e)=> {
        let parent = e.target.parentNode.parentNode
        parent.querySelectorAll("input").forEach((input) => {
            input.checked = false
        })
        updateProjectDetailsPage()
    })
})

document.querySelector("#overview-tab").addEventListener("click", (e)=>{
    currentTab = "overview-tab"
    updateProjectDetailsPage()
})
document.querySelector("#sentiment-tab").addEventListener("click", (e)=>{
    currentTab = "sentiment-tab"
    updateProjectDetailsPage()
})
document.querySelector("#aspect-tab").addEventListener("click", (e)=>{
    currentTab = "aspect-tab"
    updateProjectDetailsPage()
})
document.querySelector("#entity-tab").addEventListener("click", (e)=>{
    currentTab = "entity-tab"
    updateProjectDetailsPage()
})
document.querySelector("#sources-tab").addEventListener("click", (e)=>{
    currentTab = "sources-tab"
    updateProjectDetailsPage()
})

updateProjectDetailsPage()