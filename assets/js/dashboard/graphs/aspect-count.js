import config from "../config";
import { getFilters } from "../helpers/filters";
import { update } from "../helpers/helpers";
import { createTable as dataPerAspectTable } from "../tables/data_table_modal";
import wordCloud from "./word-cloud-modal";
let chart;
export function createGraph() {
    update.startUpdate();
    if (chart) {
        chart.destroy();
    }
    let colors = ["#28C76F", "#EA5455", "#00CFE8", "#7367F0", "#FF9F43"];
    let colorsIndex = 0;

    let aspectCountGraphs = document.querySelector("#aspect-count-graphs");
    aspectCountGraphs.innerHTML = "";
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
            update.finishUpdate();
        });
}
