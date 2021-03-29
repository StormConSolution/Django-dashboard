import config from "../config";

function overallSentiment(data){
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
    chartOptions.series = [data.positive_count, data.negative_count, data.neutral_count]
    let chart = new ApexCharts(document.querySelector("#overall-sentiment-chart"), chartOptions);
    chart.render();
}

function aspectAndSourceCount(data){
    let aspectCount = document.getElementById("aspect-count")
    let sourceCount = document.getElementById("source-count")
    aspectCount.innerHTML = data.aspectCount
    sourceCount.innerHTML = data.sourceCount
}

let project_id = window.project_id
fetch(`/api/project-overview/${project_id}/`).then(response => response.json()).then(data => {
    overallSentiment(data)
    aspectAndSourceCount(data)
})

