import config from "../config";
import {getFilters} from "../helpers/filters"
import {update} from '../helpers/helpers'
import {createTable} from '../tables/data_table_modal_aspect_topic_tree_map'
import wordCloud from './word-cloud-modal'
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
        let maxTopics = document.querySelector("#aspect-topic-tree-map-max-topics").value
        let sentiment = document.querySelector("#aspect-topic-tree-map-sentiment").value
        let urlParams = new URLSearchParams({
            "date-from": filtersValues.dateFrom,
            "date-to": filtersValues.dateTo,
            "languages": filtersValues.languages,
            "sources": filtersValues.sources,
            "sourcesID": filtersValues.sourcesID,
            "aspect-label": encodeURIComponent(aspectLabel),
            "max-topics": encodeURIComponent(maxTopics),
            "sentiment": sentiment
        })
        fetch(`/api/topics-per-aspect/${project_id}/?` + urlParams).then(response => response.json()).then(data => {
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
                    type: 'treemap',
                    events: {
                        dataPointSelection: function(event, chartContext, config) {
                            let topicLabel = config.w.config.series[0].data[config.dataPointIndex].x
                            document.querySelector("#data-table-modal").style.display = "block"
                            filtersValues = getFilters()
                            let wordCloudURL = `/api/data-per-aspect-topic/${window.project_id}/?format=word-cloud&` + new URLSearchParams({
                                "aspect-label": encodeURIComponent(aspectLabel),
                                "topic-label": encodeURIComponent(topicLabel),
                                "sentiment": options.sentiment,
                                "date-from": filtersValues.dateFrom,
                                "date-to": filtersValues.dateTo,
                                "languages": encodeURIComponent(filtersValues.languages),
                                "sources": filtersValues.sources,
                                "sourcesID": filtersValues.sourcesID
                            })
                            wordCloud(wordCloudURL)
                            createTable(1, {topicLabel:topicLabel, sentiment: sentiment, aspectLabel: aspectLabel})
                        }            
                    }
                }
            };
            options.series.push({data:chartData})
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

document.querySelector("#aspect-topic-tree-map-sentiment").addEventListener("change", (e)=>{
    createGraph()
})