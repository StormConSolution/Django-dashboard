import config from "../config";
import {metadataFiltersURL, normalFiltersURL} from "../helpers/filters";
import {update} from '../helpers/helpers'
import {createTable as dataTableModalPerSentiment} from "../tables/data_table_modal"
import wordlCloud from './word-cloud-modal'
let chart
let div = document.querySelector("#overall-sentiment-chart")
normalFiltersURL()
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
                    document.querySelector("#data-table-modal").style.display = "block"
                    wordlCloud(`/api/new-data/project/${window.project_id}/?format=word-cloud&` + new URLSearchParams({
                        "sentiment": encodeURIComponent(options.sentiment),
                    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL())
                    options.csvURL =`/api/new-data/project/${window.project_id}/?format=csv&` + new URLSearchParams({
                        "sentiment": encodeURIComponent(options.sentiment),
                    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL() 
                    options.dataURL =`/api/new-data/project/${window.project_id}/?` + new URLSearchParams({
                        "sentiment": encodeURIComponent(options.sentiment),
                    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
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
    if(data.aspectCount>1){
        document.querySelector("#overall-sentiment-different-aspects").innerHTML = "Different Aspects"
    } else {
        document.querySelector("#overall-sentiment-different-aspects").innerHTML = "Different Aspect"
    }
    if(data.sourceCount>1){
        document.querySelector("#overall-sentiment-different-sources").innerHTML = "Different Sources"
    } else {
        document.querySelector("#overall-sentiment-different-sources").innerHTML = "Different Source"
    }
}
function seeAllTotalItems(data){
    //document.getElementById("see-all-total-items").innerHTML = `See all ${data.positive_count + data.negative_count + data.neutral_count} data items`
}

let project_id = window.project_id
export function createGraph(){
    update.startUpdate()
    let urlParams = metadataFiltersURL()+ "&" + normalFiltersURL()
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


