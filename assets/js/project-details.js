import * as graphs from "./dashboard/graphs";
import * as tables from "./dashboard/tables";
import { getFilters } from "./dashboard/helpers/filters";
import {update, hideAllGraphsTables, showGraphTable} from './dashboard/helpers/helpers'
let timeOut
let currentTab = "overview-tab"
function updateProjectTables(){
    tables.aspectTopicTable(1)
    tables.dataTable(1)
    tables.entityTable(1)
    tables.topEntitiesPerAspectTable(1)
}
function updateGraphs(){
    graphs.aspectBySentimentGraph()
    graphs.aspectCountGraph()
    graphs.coOccurrenceGraph()
    graphs.overallSentimentGraph()
    graphs.sentimentTrendGraph()
    graphs.volumeBySourceGraph()
    graphs.aspectTopicTreeMap()
    graphs.emotionAspectCoOccurrence()
}

function updateProjectDetailsPage(){
    if(update.canUpdate()){
        updateProjectTables()
        updateGraphs()
    } else {
        if(timeOut){
            clearTimeout(timeOut)
        }
        timeOut = setTimeout(updateProjectDetailsPage,1000)
    }
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

function showHideGraphsTables(){
    hideAllGraphsTables()
    switch(currentTab){
        case "overview-tab":
            showGraphTable("overall-sentiment")
            showGraphTable("sentiment-trend")
            break
        case "sentiment-tab":
            break
        case "aspect-tab":
            showGraphTable("aspect-count")
            showGraphTable("aspect-by-sentiment")
            showGraphTable("aspect-co-occurrence")
            showGraphTable("aspect-topic")
            showGraphTable("aspect-topic-tree-map")
            showGraphTable("emotion-aspect-co-occurrence")
            break
        case "entity-tab":
            showGraphTable("entities-table")
            showGraphTable("top-entities-per-aspect-table")
            break
        case "sources-tab":
            showGraphTable("volume-by-source")
            showGraphTable("data-table")
            break
        case "word-cloud-tab":
            showGraphTable("word-cloud")
    }
}

showHideGraphsTables()
document.querySelector("#overview-tab").addEventListener("click", (e)=>{
    currentTab = "overview-tab"
    showHideGraphsTables()
})
document.querySelector("#sentiment-tab").addEventListener("click", (e)=>{
    currentTab = "sentiment-tab"
    showHideGraphsTables()
})
document.querySelector("#aspect-tab").addEventListener("click", (e)=>{
    currentTab = "aspect-tab"
    showHideGraphsTables()
})
document.querySelector("#entity-tab").addEventListener("click", (e)=>{
    currentTab = "entity-tab"
    showHideGraphsTables()
})
document.querySelector("#sources-tab").addEventListener("click", (e)=>{
    currentTab = "sources-tab"
    showHideGraphsTables()
})
document.querySelector("#word-cloud-tab").addEventListener("click", (e)=>{
    currentTab = "word-cloud-tab"
    showHideGraphsTables()
})
