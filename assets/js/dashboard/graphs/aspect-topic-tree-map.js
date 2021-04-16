import config from "../config";
import {getFilters} from "../helpers/filters"
import {update} from '../helpers/helpers'
import {createTable as dataPerAspectTable} from '../tables/data_table_modal_per_aspect'
let chart
let project_id = window.project_id;
let firstRun = true
export function createGraph(){
    if(firstRun){
        firstRun = false
        fetch(`/api/aspect-count/${project_id}/`).then(response => response.json()).then(data => {
            let first = true
            let aspectSelect = document.querySelector("#aspect-topic-tree-map-aspects")
            for(let element of data){
                let option = document.createElement("option")
                if(first){
                    option.selected = true
                    first = false
                }
                option.value = element.aspectLabel
                option.innerHTML = element.aspectLabel
                aspectSelect.append(option)
            }
            createGraph()
        })
    } else {
        update.startUpdate()
        if(chart){
            chart.destroy()
        }
        let filtersValues = getFilters() 
        let aspectLabel = document.querySelector("#aspect-topic-tree-map-aspects").value
        console.log(aspectLabel)
        let maxTopics = document.querySelector("#aspect-topic-tree-map-max-topics").value
        let urlParams = new URLSearchParams({
            "date-from": filtersValues.dateFrom,
            "date-to": filtersValues.dateTo,
            "languages": filtersValues.languages,
            "sources": filtersValues.sources,
            "aspect-label": encodeURIComponent(aspectLabel),
            "max-topics": encodeURIComponent(maxTopics)
        })
        fetch(`/api/topics-per-aspect/${project_id}/?` + urlParams).then(response => response.json()).then(data => {
            console.log(data)
            let chartData = []
            for(let element of data){
                chartData.push({x:element.topicLabel, y:element.topicCount})
            }
            let options = {
                    series: [],
                    legend: {
                    show: false
                },
                chart: {
                    height: 480,
                    type: 'treemap'
                }
            };
            options.series.push({data:chartData})
            console.log(options)
            chart = new ApexCharts(document.querySelector("#aspect-topic-tree-map-container"), options);
            chart.render();
            update.finishUpdate()
        })
    }
}

document.querySelector("#aspect-topic-tree-map-aspects").addEventListener("change", (e)=>{
    createGraph()
})

document.querySelector("#aspect-topic-tree-map-max-topics").addEventListener("change", (e)=>{
    createGraph()
})