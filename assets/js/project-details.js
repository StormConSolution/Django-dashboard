import * as graphs from "./dashboard/graphs";
import * as tables from "./dashboard/tables";
import { getFilters } from "./dashboard/helpers/filters";
import {update, hideAllGraphsTables, showGraphTable} from './dashboard/helpers/helpers'

import  "./dashboard/countrymap.js";

let timeOut
let timeOutUpdateDelay
let currentTab = "overview-tab"
let renderAspect = true
let renderEntity = true
let tabLoadingCounter = 2
let tabLoadingDiv = document.querySelector("#tab-loading")
let showEmotionAspectCoOccurrence = true
export function setShowEmotionAspectCoOccurrence(value) {
    showEmotionAspectCoOccurrence = value
}
function updateProjectTables() {
    if (renderAspect) {
        tables.aspectTopicTable(1)
    }
    if (renderEntity) {
        tables.entityTable(1)
    }
    if (renderEntity && renderAspect) {
        tables.topEntitiesPerAspectTable(1)
    }
}

function updateGraphs() {
    if (renderAspect) {
        graphs.aspectBySentimentPercentageGraph()
        graphs.aspectBySentimentAbsoluteGraph()
        graphs.aspectTopicTreeMap()
        graphs.aspectCountGraph()
        graphs.emotionAspectCoOccurrence()
        graphs.coOccurrenceGraph()
        graphs.mostCommonChunks()
    }
    if (renderEntity) {
        graphs.entityBySentimentGraph()
        graphs.classificationBySentimentGraph()
    }
    graphs.overallSentimentGraph()
    graphs.sentimentTrendGraph()
    graphs.volumeBySourceGraph()
    graphs.sourceBySentimentGraph()
}

function updateProjectDetailsPageWithDelay() {
    if (timeOutUpdateDelay) {
        clearTimeout(timeOutUpdateDelay)
    } else {
        setTimeout(updateProjectDetailsPage, 3000)
    }
}

function updateProjectDetailsPage() {
    if (update.canUpdate()) {
        updateProjectTables()
        updateGraphs()
    } else {
        if (timeOut) {
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
for(let languageCheckbox of languagesCheckbox) {
    languageCheckbox.addEventListener("change", (e)=>{
        updateProjectDetailsPageWithDelay()
    })
}

let sourcesCheckbox = document.querySelectorAll("#dropdown-sources .choose input")
for(let sourceCheckbox of sourcesCheckbox) {
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

function activeProjectDetailsTab(id) {
    document.querySelector(`#${id}`).className="active"
}

function showHideGraphsTables() {
    hideAllGraphsTables()
    document.querySelectorAll(".project-menu ul li a").forEach(element=>{
        element.className = ""
    })
    
	switch(currentTab) {
        case "overview-tab":
            showGraphTable("overall-sentiment")
            showGraphTable("sentiment-trend")
            if (document.querySelector("#most-common-chunks-graph").getAttribute("data-show") == "true") {
                showGraphTable("most-common-chunks")
            }
            break
        case "aspect-tab":
            showGraphTable("aspect-count")
            showGraphTable("aspect-by-sentiment-percentage")
            showGraphTable("aspect-by-sentiment-absolute")
            showGraphTable("aspect-co-occurrence")
            showGraphTable("aspect-topic")
            showGraphTable("aspect-topic-tree-map")
            if (showEmotionAspectCoOccurrence) {
                showGraphTable("emotion-aspect-co-occurrence")
            }
            break
        case "entity-tab":
            showGraphTable("entities-table")
            if (renderEntity && renderAspect) {
                showGraphTable("top-entities-per-aspect-table")
            }
            showGraphTable("entity-by-sentiment")
            showGraphTable("classification-by-sentiment")
            break
        case "sources-tab":
            showGraphTable("volume-by-source")
            showGraphTable("source-by-sentiment")
            break
        case "geo-tab":
            showGraphTable("map")
            showGraphTable("most-recent-bullying-table")
            showGraphTable("region-bullying-table")
            showGraphTable("school-bullying-table")
            showGraphTable("active-bullying-graph")
            showGraphTable("time-bullying-graph")
            showGraphTable("gender-bullying-graph")
            showGraphTable("school-bullying-trend")
            showGraphTable("map")
            break
    }

    activeProjectDetailsTab(currentTab)
}

showHideGraphsTables()

document.querySelector("#overview-tab").addEventListener("click", (e)=>{
    currentTab = "overview-tab"
    showHideGraphsTables()
})

if (document.getElementById("geo-tab")) {
	document.getElementById('geo-tab').addEventListener("click", (e)=> {
		currentTab = "geo-tab"
		showHideGraphsTables()
	});
}

// check if theres aspect data to render aspect graphs
fetch(`/api/aspect-count/${window.project_id}/`).then(response=>response.json()).then(data => {
    let liContainer = document.querySelector("#li-aspect-tab") 
    tabLoadingCounter--;
    if (tabLoadingCounter == 0) {
        tabLoadingDiv.innerHTML = ""
    }
    if (data.length != 0) {
        liContainer.innerHTML = '<a style="cursor:pointer;" id="aspect-tab">Aspects</a>'
        document.querySelector("#aspect-tab").addEventListener("click", (e)=>{
            currentTab = "aspect-tab"
            showHideGraphsTables()
        })
        document.querySelector("#most-common-chunks-graph").setAttribute("data-show", "true")
    } else {
        liContainer.style.display = "none"
        renderAspect = false
    }
})

fetch(`/api/entity-by-sentiment/${window.project_id}/`).then(response=>response.json()).then(data => {
    let liContainer =document.querySelector("#li-entity-tab") 
    tabLoadingCounter--;
    if (tabLoadingCounter == 0) {
        tabLoadingDiv.innerHTML = ""
    }
    if (data.length != 0) {
        liContainer.innerHTML = '<a style="cursor:pointer;" id="entity-tab">Entity</a>'
        document.querySelector("#entity-tab").addEventListener("click", (e)=>{
            currentTab = "entity-tab"
            showHideGraphsTables()
        })
    } else {
        liContainer.style.display = "none"
        renderEntity = false
    }
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
