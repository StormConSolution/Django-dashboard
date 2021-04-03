import config from "../config";

export function createGraph(){
    var projectId = window.project_id;
    fetch(`/api/sentiment-trend/${projectId}/`)
        .then((response) => response.json())
        .then((data) => {
            let chartOptions = {
                series: [],
                colors: ["#28C76F", "#EA5455"],
                chart: {
                    height: 320,
                    type: "line",
                    toolbar: {
                        show: false,
                    },
                },
    
                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    curve: "smooth",
                    width: 3,
                },
                legend: {
                    show: false,
                },
                xaxis: {
                    categories: [],
                },
                tooltip: {
                    x: {
                        format: "MM/yyyy",
                    },
                },
            };
            let positives = [];
            let negatives = [];
            let categories = [];
            let totalPositives = 0
            let totalNegatives = 0
            for (let element of data) {
                totalPositives += element.positivesCount
                totalNegatives += element.negativesCount
                positives.push(totalPositives);
                negatives.push(totalNegatives);
                categories.push(element.date);
            }
            chartOptions.series.push(
                { name: "Positives", data: positives },
                { name: "Negatives", data: negatives }
            );
    
            chartOptions.xaxis.categories = categories;
    
            document.getElementById("sentiment-trend-total").innerHTML = totalPositives + totalNegatives
            document.getElementById("sentiment-trend-total-positives").innerHTML = totalPositives
            document.getElementById("sentiment-trend-total-negatives").innerHTML = totalNegatives
            let chart = new ApexCharts(
                document.querySelector("#sentiment-trend-graph"),
                chartOptions
            );
            chart.render();
        });
}

