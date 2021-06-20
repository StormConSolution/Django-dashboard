import { update } from "../helpers/helpers";
import { metadataFiltersURL , normalFiltersURL} from "../helpers/filters";

let chart;
let graphContainer = document.querySelector("#most-common-chunks")
let maxChunks = document.querySelector("#max-most-common-chunks")

export function createGraph() {
    update.startUpdate();
    if (chart) {
        chart.destroy();
    }
    graphContainer.innerHTML = "Loading...";
    
    let urlParams = new URLSearchParams({
        'limit':maxChunks.value
    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
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

maxChunks.addEventListener("change", (e)=>{
    createGraph()
})
