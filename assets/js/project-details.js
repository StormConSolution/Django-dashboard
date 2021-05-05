import * as graphs from "./dashboard/graphs";
import * as tables from "./dashboard/tables";
import { getFilters } from "./dashboard/helpers/filters";
import {update, hideAllGraphsTables, showGraphTable} from './dashboard/helpers/helpers'
let timeOut
let timeOutUpdateDelay
let currentTab = "overview-tab"
function updateProjectTables(){
    tables.aspectTopicTable(1)
    tables.dataTable(1)
    tables.entityTable(1)
    tables.topEntitiesPerAspectTable(1)
}
function updateGraphs(){
    graphs.aspectBySentimentPercentageGraph()
    graphs.aspectBySentimentAbsoluteGraph()
    graphs.aspectCountGraph()
    graphs.coOccurrenceGraph()
    graphs.overallSentimentGraph()
    graphs.sentimentTrendGraph()
    graphs.volumeBySourceGraph()
    graphs.aspectTopicTreeMap()
    graphs.emotionAspectCoOccurrence()
    graphs.sourceBySentimentGraph()
    graphs.entityBySentimentGraph()
}

function updateProjectDetailsPageWithDelay(){
    if(timeOutUpdateDelay){
        clearTimeout(timeOutUpdateDelay)
    } else {
        setTimeout(updateProjectDetailsPage, 4000)
    }
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
    updateProjectDetailsPageWithDelay()
})

document.getElementById("date-to").addEventListener("change", (e)=>{
    updateProjectDetailsPageWithDelay()
})

let languagesCheckbox = document.querySelectorAll("#dropdown-languages .choose input")
for(let languageCheckbox of languagesCheckbox){
    languageCheckbox.addEventListener("change", (e)=>{
        updateProjectDetailsPageWithDelay()
    })
}
let sourcesCheckbox = document.querySelectorAll("#dropdown-sources .choose input")
for(let sourceCheckbox of sourcesCheckbox){
    sourceCheckbox.addEventListener("change", (e)=>{
        updateProjectDetailsPageWithDelay()
    })
}

document.querySelectorAll(".check-all").forEach((element) => {
    element.addEventListener("click", (e)=> {
        
        let parent = e.target.parentNode.parentNode
        
        parent.querySelectorAll("input").forEach((input) => {
            input.checked = true
        })
        updateProjectDetailsPageWithDelay()
    })
})

document.querySelectorAll(".uncheck-all").forEach((element) => {
    element.addEventListener("click", (e)=> {
        let parent = e.target.parentNode.parentNode
        parent.querySelectorAll("input").forEach((input) => {
            input.checked = false
        })
        updateProjectDetailsPageWithDelay()
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
            showGraphTable("aspect-by-sentiment-percentage")
            showGraphTable("aspect-by-sentiment-absolute")
            showGraphTable("aspect-co-occurrence")
            showGraphTable("aspect-topic")
            showGraphTable("aspect-topic-tree-map")
            showGraphTable("emotion-aspect-co-occurrence")
            break
        case "entity-tab":
            showGraphTable("entities-table")
            showGraphTable("top-entities-per-aspect-table")
            showGraphTable("entity-by-sentiment")
            break
        case "sources-tab":
            showGraphTable("volume-by-source")
            showGraphTable("data-table")
            showGraphTable("source-by-sentiment")
            break
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

document.querySelector("#show-word-cloud-modal").addEventListener("click", (e)=>{
    document.querySelector("#word-cloud-modal").style.display = "block"
})

document.querySelector("#close-word-cloud-modal").addEventListener("click", (e)=>{
    document.querySelector("#word-cloud-modal").style.display = "none"
})
