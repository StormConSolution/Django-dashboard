import config from "../config";
import * as filters from "../helpers/filters"
import {update} from '../helpers/helpers'
import {createTable as dataTableModalPerSentiment} from "../tables/data_table_modal"
import wordlCloud from './word-cloud-modal'
let chart
let div = document.querySelector("#overall-sentiment-chart")
function overallSentiment(data){
    var chartOptions = {
        colors: [config.positive, config.negative, config.neutral],
        chart: {
            height: 250,
            type: "donut",
            events: {
                dataPointSelection: function(event, chartContext, config) {
                    let sentiment = config.w.config.labels[config.dataPointIndex].toLowerCase()
                    let options = {}
                    options.sentiment = sentiment
                    let filtersValues = filters.getFilters()
                    document.querySelector("#data-table-modal").style.display = "block"
                    wordlCloud(`/api/new-data/project/${window.project_id}/?format=word-cloud&` + new URLSearchParams({
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo,
                        "sentiment": encodeURIComponent(options.sentiment),
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": encodeURIComponent(filtersValues.sources),
                        "sourcesID": filtersValues.sourcesID
                    }))
                    options.csvURL =`/api/new-data/project/${window.project_id}/?format=csv&` + new URLSearchParams({
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo,
                        "sentiment": encodeURIComponent(options.sentiment),
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": encodeURIComponent(filtersValues.sources),
                        "sourcesID": filtersValues.sourcesID
                    }) 
                    options.dataURL =`/api/new-data/project/${window.project_id}/?` + new URLSearchParams({
                        "sentiment": encodeURIComponent(options.sentiment),
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo,
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": encodeURIComponent(filtersValues.sources),
                        "sourcesID": filtersValues.sourcesID
                    })
                    dataTableModalPerSentiment(1, options)
                }            
            }
        },
        dataLabels: {
            enabled: false,
        },
        legend: {
            position: "left",
        },
        plotOptions: {
            pie: {
                donut: {
                    labels: {
                        show: true,
                        total: {
                            showAlways: true,
                            show: true,
                        },
                    },
                },
            },
            radialBar: {
                hollow: {
                    size: "60%",
                },
            },
        },
        labels: ["Positive", "Negative", "Neutral"],
    };
    chartOptions.series = [data.positivesCount, data.negativesCount, data.neutralsCount]
    chart = new ApexCharts(div, chartOptions);
    chart.render();
}

function aspectAndSourceCount(data){
    let aspectCount = document.getElementById("aspect-count")
    let sourceCount = document.getElementById("source-count")
    aspectCount.innerHTML = data.aspectCount
    sourceCount.innerHTML = data.sourceCount
}
function seeAllTotalItems(data){
    //document.getElementById("see-all-total-items").innerHTML = `See all ${data.positive_count + data.negative_count + data.neutral_count} data items`
}

let project_id = window.project_id
export function createGraph(){
    update.startUpdate()
    let filtersValues = filters.getFilters()
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": encodeURIComponent(filtersValues.languages),
        "sources": encodeURIComponent(filtersValues.sources),
        "sourcesId": filtersValues.sourcesId
    })
    if(chart){
        chart.destroy()
    }
    div.innerHTML = "Loading..."

    fetch(`/api/project-overview/${project_id}/?` + urlParams).then(response => response.json()).then(data => {
        div.innerHTML = ""
        overallSentiment(data)
        aspectAndSourceCount(data)
        seeAllTotalItems(data)
        update.finishUpdate()
    })
}


