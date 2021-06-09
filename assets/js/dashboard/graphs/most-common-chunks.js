import { getFilters } from "../helpers/filters";
import { update } from "../helpers/helpers";
let chart;
let graphContainer = document.querySelector("#most-common-chunks")
export function createGraph() {
    update.startUpdate();
    if (chart) {
        chart.destroy();
    }
    graphContainer.innerHTML = "Loading...";
    
    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": filtersValues.languages,
        "sources": filtersValues.sources,
        "sourcesID": filtersValues.sourcesID,
    })
    fetch(`/api/most-common-chunks/${window.project_id}/?` + urlParams)
    .then((response) => response.json())
    .then((data) => {
        graphContainer.innerHTML = "";
        for (let element of data) {
            let button = document.createElement("button")
            button.style.margin = "1rem"
            button.disabled = true
            if(element.positiveCount > element.negativeCount){
                button.className = "btn btn-success"
                button.innerHTML = `${element.chunk} <span class="badge badge-light">${element.positiveCount}</span>`
            } else {
                button.className = "btn btn-danger"
                button.innerHTML = `${element.chunk} <span class="badge badge-light">${element.negativeCount}</span>`
            }
            graphContainer.appendChild(button)
        }
        update.finishUpdate()
    });
}
