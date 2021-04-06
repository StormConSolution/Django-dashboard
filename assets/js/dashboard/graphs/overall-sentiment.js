import config from "../config";
import * as filters from "../helpers/filters"
import {update} from '../helpers/helpers'
import {createTable as dataTableModalPerSentiment} from "../tables/data_table_modal_data_per_sentiment"
let chart
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
    chart = new ApexCharts(document.querySelector("#overall-sentiment-chart"), chartOptions);
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
        "sources": encodeURIComponent(filtersValues.sources)
    })
    if(chart){
        chart.destroy()
    }

    fetch(`/api/project-overview/${project_id}/?` + urlParams).then(response => response.json()).then(data => {
        overallSentiment(data)
        aspectAndSourceCount(data)
        seeAllTotalItems(data)
        update.finishUpdate()
    })
}


