import { getFilters } from "../helpers/filters";
import { update } from "../helpers/helpers";
import { createTable as dataPerAspectTable } from "../tables/data_table_modal";
import wordCloud from "./word-cloud-modal";
import config from "../config";
let chart;
let graphContainer = document.querySelector("#aspect-count-graphs")
export function createGraph() {
    update.startUpdate();
    if (chart) {
        chart.destroy();
    }

    let aspectCountGraphs = document.querySelector("#aspect-count-graphs");
    aspectCountGraphs.innerHTML = "Loading...";
    let filtersValues = getFilters();
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        languages: filtersValues.languages,
        sources: filtersValues.sources,
        sourcesID: filtersValues.sourcesID,
    });
    let project_id = window.project_id;
    fetch(`/api/aspect-count/${project_id}/?` + urlParams)
        .then((response) => response.json())
        .then((data) => {
            let totalCount = 0
            for (let element of data) {
                totalCount += element.aspectCount;
            }
            let chartdData = [];
            let aspects = [];
            let maxNumber = 0;
            for (let element of data) {

                chartdData.push(element.aspectCount)
                aspects.push(element.aspectLabel);
                if (element.aspectCount > maxNumber) {
                    maxNumber = element.aspectCount
                }
            }
            let chartOptions = {
                series: [],
                chart: {
                    type: "bar",
                    height: 440,
                    stacked: true,
                    events: {
                        dataPointSelection: function(event, chartContext, config) {
                            let aspectLabel = config.w.config.xaxis.categories[config.dataPointIndex]
                            let options = {};
                            document.querySelector("#data-table-modal").style.display =
                                "block";
                            options.aspectLabel = aspectLabel;
                            let wordCloudURL =
                                `/api/data-per-aspect/${window.project_id}/?format=word-cloud&` +
                                new URLSearchParams({
                                    "date-from": filtersValues.dateFrom,
                                    "date-to": filtersValues.dateTo,
                                    "aspect-label": encodeURIComponent(
                                        options.aspectLabel
                                    ),
                                    languages: encodeURIComponent(
                                        filtersValues.languages
                                    ),
                                    sources: encodeURIComponent(filtersValues.sources),
                                    sourcesID: filtersValues.sourcesID,
                                });
                            options.csvURL =
                                `/api/data-per-aspect/${window.project_id}/?format=csv&` +
                                new URLSearchParams({
                                    "date-from": filtersValues.dateFrom,
                                    "date-to": filtersValues.dateTo,
                                    "aspect-label": encodeURIComponent(
                                        options.aspectLabel
                                    ),
                                    languages: encodeURIComponent(
                                        filtersValues.languages
                                    ),
                                    sources: encodeURIComponent(filtersValues.sources),
                                    sourcesID: filtersValues.sourcesID,
                                });
                            options.dataURL =
                                `/api/data-per-aspect/${window.project_id}/?` +
                                new URLSearchParams({
                                    "aspect-label": encodeURIComponent(
                                        options.aspectLabel
                                    ),
                                    "date-from": filtersValues.dateFrom,
                                    "date-to": filtersValues.dateTo,
                                    languages: encodeURIComponent(
                                        filtersValues.languages
                                    ),
                                    sources: encodeURIComponent(filtersValues.sources),
                                    sourcesID: filtersValues.sourcesID,
                                });
                            wordCloud(wordCloudURL);
                            dataPerAspectTable(1, options);
                        }            
                    }
                },
                legend: { show: false },
                colors: [config.neutral],
                plotOptions: {
                    bar: {
                        horizontal: true,
                        borderRadius: 6,
                        barHeight: "50",
                    },
                },
                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    width: 1,
                    colors: ["#fff"],
                },
        
                grid: {
                    xaxis: {
                        lines: {
                            show: false,
                        },
                    },
                },
                yaxis: {
                    min: -85,
                    max: 85,
                    title: {
                        // text: 'Age',
                    },
                },
                tooltip: {
                    shared: false,
                    x: {
                        formatter: function (val) {
                            return val;
                        },
                    },
                    y: {
                        formatter: function (val) {
                            return Math.abs(val);
                        },
                    },
                },
        
                xaxis: {
                    categories: [],
        
                    labels: {
                        formatter: function (val) {
                            return Math.abs(Math.round(val));
                        },
                    },
                },
            };
            chartOptions.series.push({
                name: "Count",
                data: chartdData,
            });
            chartOptions.yaxis = {}
            chartOptions.yaxis.max = maxNumber + Math.round(maxNumber * 0.1)
            chartOptions.xaxis = {}
            chartOptions.xaxis.categories = aspects;
            graphContainer.innerHTML = ""
            chartOptions.chart.height = 40 * data.length
            if(chartOptions.chart.height < 100){
                chartOptions.chart.height = 100
            } 
            if(Object.keys(data).length !== 0){
            chart = new ApexCharts(
                graphContainer,
                chartOptions
            );
            chart.render();
            }
            update.finishUpdate();
        });
}

/*
let totalCount = 0;
            for (let element of data) {
                totalCount += element.aspectCount;
            }
            for (let element of data) {
                let percentage = (
                    (element.aspectCount / totalCount) *
                    100
                ).toFixed(2);
                let id = `aspect-count-${element.aspectLabel}`;
                id = id.replace(/\W/g, '')
                let li = document.createElement("li");

                let domElement = `
                <a class="d-flex color-1" style="cursor:pointer">
                <small>${element.aspectLabel}</small>
                <b style="color:${colors[colorsIndex]};">${element.aspectCount}</b>
                <span>${percentage}%</span>
                <div class="round-chart">
                  <div id="${id}"></div>
                </div>
                </a>
                `;
                li.innerHTML = domElement;
                li.setAttribute("data-aspect-label", element.aspectLabel);
                aspectCountGraphs.append(li);
                let color = colors[colorsIndex];
                if (colorsIndex == colors.length - 1) {
                    colorsIndex = 0;
                } else {
                    colorsIndex++;
                }

                let chartOptions = {
                    series: [percentage],
                    chart: {
                        type: "radialBar",
                        width: 30,
                        height: 30,
                        sparkline: {
                            enabled: true,
                        },
                    },

                    colors: [color],
                    dataLabels: {
                        enabled: false,
                    },
                    plotOptions: {
                        radialBar: {
                            hollow: {
                                margin: 0,
                                size: "40%",
                            },
                            track: {
                                margin: 0,
                            },
                            dataLabels: {
                                show: false,
                            },
                        },
                    },
                };
                if (Object.keys(data).length !== 0) {
                    chart = new ApexCharts(
                        document.querySelector(`#${id}`),
                        chartOptions
                    );
                    chart.render();
                }
            }
            let aspectCountElements = aspectCountGraphs.querySelectorAll("li");
            for (let element of aspectCountElements) {
                element.addEventListener("click", (e) => {
                    let aspectLabel =
                        e.currentTarget.getAttribute("data-aspect-label");
                    let options = {};
                    document.querySelector("#data-table-modal").style.display =
                        "block";
                    options.aspectLabel = aspectLabel;
                    let wordCloudURL =
                        `/api/data-per-aspect/${window.project_id}/?format=word-cloud&` +
                        new URLSearchParams({
                            "date-from": filtersValues.dateFrom,
                            "date-to": filtersValues.dateTo,
                            "aspect-label": encodeURIComponent(
                                options.aspectLabel
                            ),
                            languages: encodeURIComponent(
                                filtersValues.languages
                            ),
                            sources: encodeURIComponent(filtersValues.sources),
                            sourcesID: filtersValues.sourcesID,
                        });
                    options.csvURL =
                        `/api/data-per-aspect/${window.project_id}/?format=csv&` +
                        new URLSearchParams({
                            "date-from": filtersValues.dateFrom,
                            "date-to": filtersValues.dateTo,
                            "aspect-label": encodeURIComponent(
                                options.aspectLabel
                            ),
                            languages: encodeURIComponent(
                                filtersValues.languages
                            ),
                            sources: encodeURIComponent(filtersValues.sources),
                            sourcesID: filtersValues.sourcesID,
                        });
                    options.dataURL =
                        `/api/data-per-aspect/${window.project_id}/?` +
                        new URLSearchParams({
                            "aspect-label": encodeURIComponent(
                                options.aspectLabel
                            ),
                            "date-from": filtersValues.dateFrom,
                            "date-to": filtersValues.dateTo,
                            languages: encodeURIComponent(
                                filtersValues.languages
                            ),
                            sources: encodeURIComponent(filtersValues.sources),
                            sourcesID: filtersValues.sourcesID,
                        });
                    wordCloud(wordCloudURL);
                    dataPerAspectTable(1, options);
                });
            }
            */
