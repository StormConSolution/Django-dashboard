import { metadataFiltersURL, normalFiltersURL} from "../helpers/filters";
import { update } from "../helpers/helpers";
import { createTable } from "../tables/data_table_modal";
import wordCloud from "./word-cloud-modal";
let chart;
let project_id = window.project_id;
let firstRun = true;
export function createGraph() {
    if (firstRun) {
        firstRun = false;
        fetch(`/api/aspect-count/${project_id}/?order-by=label`)
            .then((response) => response.json())
            .then((data) => {
                let first = true;
                let aspectSelect = document.querySelector(
                    "#aspect-topic-tree-map-aspects"
                );
                for (let element of data) {
                    let option = document.createElement("option");
                    if (first) {
                        option.selected = true;
                        first = false;
                    }
                    option.value = element.aspectLabel;
                    option.innerHTML = element.aspectLabel;
                    aspectSelect.append(option);
                }
                createGraph();
            });
    } else {
        update.startUpdate();
        if (chart) {
            chart.destroy();
        }
        let aspectLabel = document.querySelector(
            "#aspect-topic-tree-map-aspects"
        ).value;
        let maxTopics = document.querySelector(
            "#aspect-topic-tree-map-max-topics"
        ).value;
        let sentiment = document.querySelector(
            "#aspect-topic-tree-map-sentiment"
        ).value;
        let urlParams = new URLSearchParams({
            "aspect-label": encodeURIComponent(aspectLabel),
            "max-topics": encodeURIComponent(maxTopics),
            sentiment: sentiment,
        })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL();
        fetch(`/api/topics-per-aspect/${project_id}/?` + urlParams)
            .then((response) => response.json())
            .then((data) => {
                let chartData = [];
                for (let element of data) {
                    chartData.push({
                        x: element.topicLabel,
                        y: element.topicCount,
                    });
                }
                let options = {
                    series: [],
                    legend: {
                        show: false,
                    },
                    chart: {
                        height: 480,
                        type: "treemap",
                        events: {
                            dataPointSelection: function (
                                event,
                                chartContext,
                                config
                            ) {
                                let topicLabel =
                                    config.w.config.series[0].data[
                                        config.dataPointIndex
                                    ].x;
                                document.querySelector(
                                    "#data-table-modal"
                                ).style.display = "block";
                                let wordCloudURL =
                                    `/api/data-per-aspect-topic/${window.project_id}/?format=word-cloud&` +
                                    new URLSearchParams({
                                        "aspect-label":
                                            encodeURIComponent(aspectLabel),
                                        "topic-label":
                                            encodeURIComponent(topicLabel),
                                        sentiment: sentiment,
                                    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL();
                                options.csvURL =
                                    `/api/data-per-aspect-topic/${window.project_id}/?format=csv&` +
                                    new URLSearchParams({
                                        "aspect-label":
                                            encodeURIComponent(aspectLabel),
                                        "topic-label":
                                            encodeURIComponent(topicLabel),
                                       
                                    })+ "&" + normalFiltersURL() + "&" + metadataFiltersURL();
                                options.dataURL =
                                    `/api/data-per-aspect-topic/${window.project_id}/?` +
                                    new URLSearchParams({
                                        "aspect-label":
                                            encodeURIComponent(aspectLabel),
                                        "topic-label":
                                            encodeURIComponent(topicLabel),
                                        sentiment: sentiment,
                                    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL();
                                wordCloud(wordCloudURL);
                                createTable(1, options);
                            },
                        },
                    },
                };
                options.series.push({ data: chartData });
                if (Object.keys(data).length !== 0) {
                    chart = new ApexCharts(
                        document.querySelector(
                            "#aspect-topic-tree-map-container"
                        ),
                        options
                    );
                    chart.render();
                }
                update.finishUpdate();
            });
    }
}

document
    .querySelector("#aspect-topic-tree-map-aspects")
    .addEventListener("change", (e) => {
        createGraph();
    });

document
    .querySelector("#aspect-topic-tree-map-max-topics")
    .addEventListener("change", (e) => {
        createGraph();
    });

document
    .querySelector("#aspect-topic-tree-map-sentiment")
    .addEventListener("change", (e) => {
        createGraph();
    });
