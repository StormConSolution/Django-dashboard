import config from "../config";
import * as filters from "../utils/filters"
let chart
function overallSentiment(data){
    if(chart){
        chart.destroy()
    }
    var chartOptions = {
        colors: [config.positive, config.negative, config.neutral],
        chart: {
            height: 250,
            type: "donut",
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
    let filtersValues = filters.getFilters()
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo
    })

    fetch(`/api/project-overview/${project_id}/?` + urlParams).then(response => response.json()).then(data => {
        console.log(data)
        overallSentiment(data)
        aspectAndSourceCount(data)
        seeAllTotalItems(data)
    })
}


