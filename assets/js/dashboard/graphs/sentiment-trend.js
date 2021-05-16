import config from "../config";
import { update } from "../helpers/helpers";
import { getFilters } from "../helpers/filters";
let chart;
let def = 1;
let div = document.querySelector("#sentiment-trend-graph");
export function createGraph() {
    update.startUpdate();
    if (chart) {
        chart.destroy();
    }
    div.innerHTML = "Loading...";
    document.getElementById("sentiment-trend-total").innerHTML = 0;
    document.getElementById("sentiment-trend-total-positives").innerHTML = 0;
    document.getElementById("sentiment-trend-total-negatives").innerHTML = 0;
    var projectId = window.project_id;
    let filtersValues = getFilters();
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        languages: filtersValues.languages,
        sources: filtersValues.sources,
        sourcesID: filtersValues.sourcesID,
        default: def,
    });
    fetch(`/api/sentiment-trend/${projectId}/?` + urlParams)
        .then((response) => response.json())
        .then((data) => {
            def = 0;
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
            let totalPositives = 0;
            let totalNegatives = 0;
            if (Object.keys(data).length !== 0) {
                for (let element of data) {
                    totalPositives += element.positivesCount;
                    totalNegatives += element.negativesCount;
                    positives.push(totalPositives);
                    negatives.push(totalNegatives);
                    categories.push(element.date);
                }
                chartOptions.series.push(
                    { name: "Positives", data: positives },
                    { name: "Negatives", data: negatives }
                );

                chartOptions.xaxis.categories = categories;

                document.getElementById("sentiment-trend-total").innerHTML =
                    totalPositives + totalNegatives;
                document.getElementById(
                    "sentiment-trend-total-positives"
                ).innerHTML = totalPositives;
                document.getElementById(
                    "sentiment-trend-total-negatives"
                ).innerHTML = totalNegatives;
                div.innerHTML = "";
                chart = new ApexCharts(div, chartOptions);

                chart.render();
            } else {
                div.innerHTML = "";
            }
            update.finishUpdate();
        });
}
