import * as graphs from "./dashboard/graphs";
import * as tables from "./dashboard/tables";
import {update, hideAllGraphsTables, showGraphTable} from './dashboard/helpers/helpers';
import "./project-details/filters";
import {getGraphs, generatePDF} from './dashboard/pdf/pdf';
import "./project-details/text-search"
import  "./dashboard/countrymap.js";

let timeOut
let timeOutUpdateDelay
let currentTab = "overview-tab"
if (window.geo_enabled) {
	currentTab = "geo-tab"
}
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

export function updateProjectDetailsPage() {
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
            showGraphTable("volume-by-source")
            showGraphTable("source-by-sentiment")
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
        case "geo-tab":
            showGraphTable("map")
            showGraphTable("most-recent-bullying-table")
            showGraphTable("today-bullying-numbers")
            showGraphTable("region-bullying-table")
            showGraphTable("school-bullying-table")
            showGraphTable("active-bullying-graph")
            showGraphTable("time-bullying-graph")
            showGraphTable("gender-bullying-graph")
            showGraphTable("school-bullying-trend")
            break
        case "user-tab":
            showGraphTable("users")
			break
    }

    activeProjectDetailsTab(currentTab)
}

showHideGraphsTables()

document.querySelector("#overview-tab").addEventListener("click", (e)=>{
    currentTab = "overview-tab"
    showHideGraphsTables()
})

document.querySelector("#user-tab").addEventListener("click", (e)=>{
    currentTab = "user-tab"
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
    if (window.has_aspects) {
        liContainer.innerHTML = '<a style="cursor:pointer;" id="aspect-tab">Aspects</a>'
        document.querySelector("#aspect-tab").addEventListener("click", (e)=>{
            currentTab = "aspect-tab"
            showHideGraphsTables()
        })
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

document.querySelector("#show-word-cloud-modal").addEventListener("click", (e)=>{
    document.querySelector("#word-cloud-modal").style.display = "block"
})

document.querySelector("#close-word-cloud-modal").addEventListener("click", (e)=>{
    document.querySelector("#word-cloud-modal").style.display = "none"
})

document.getElementById('reset-filters').addEventListener("click", (e) => {
	// Clear the filter form, set the dates to earliest/latest and then refresh.
	document.getElementById("filter-form").reset()
	document.getElementById("date-from").value = window.earliest_date
	document.getElementById("date-to").value = window.latest_date

	// TODO: Clear all of our metadata filters.
	
	let openFilterBtn = document.getElementById('open-more-filters-modal')
	openFilterBtn.classList.remove('btn-info');
	openFilterBtn.classList.add('btn-secondary');
	e.target.classList.add('d-none')
	updateProjectDetailsPage()
})

/* document.querySelector("#generate-pdf-report").addEventListener("click", (e)=>{
    console.log(getGraphs())
    generatePDF()
}) */
