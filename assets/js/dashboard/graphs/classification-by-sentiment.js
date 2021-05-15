import config from "../config";
import { getFilters } from "../helpers/filters";
import { update } from "../helpers/helpers";
import { createTable as dataTableModalEntityBySentiment} from "../tables/data_table_modal";
import wordCloud from "./word-cloud-modal";
let chart;
let graphContainer = document.querySelector("#classification-by-sentiment")
let limit = document.querySelector("#classification-by-sentiment-limit")
let mapClassificationAndID = {}
export function createGraph() {
    update.startUpdate();
    if (chart) {
        chart.destroy();
    }
    graphContainer.innerHTML = "Loading...";
    let options = {
        series: [],
        chart: {
            type: "bar",
            height: 440,
            stacked: true,
            stackType: "100%",
            events: {
                dataPointSelection: function(event, chartContext, config) {
                    let classification = config.w.config.xaxis.categories[config.dataPointIndex]
                    let sentiment = config.w.config.series[config.seriesIndex].name
                    let options = {}
                    options.classificationID = mapClassificationAndID[classification]
                    options.sentiment = sentiment.toLowerCase()
                    let filtersValues = getFilters()
                    document.querySelector("#data-table-modal").style.display = "block"
                    let wordCloudURL = `/api/data-per-classification/${window.project_id}/?format=word-cloud&` + new URLSearchParams({
                        "sentiment": encodeURIComponent(options.sentiment),
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": filtersValues.sources,
                        "sourcesID": filtersValues.sourcesID,
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo,
                        "classificationID": mapClassificationAndID[classification]
                    })
                    options.csvURL = `/api/data-per-classification/${window.project_id}/?format=csv&` + new URLSearchParams({
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo,
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": encodeURIComponent(filtersValues.sources),
                        "sourcesID": filtersValues.sourcesID,
                        "sentiment": options.sentiment,
                        "classificationID": options.classificationID
                    })
                    options.dataURL = `/api/data-per-classification/${window.project_id}/?` + new URLSearchParams({
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo,
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": encodeURIComponent(filtersValues.sources),
                        "sourcesID": filtersValues.sourcesID,
                        "sentiment": options.sentiment,
                        "classificationID": options.classificationID
                    })
                    wordCloud(wordCloudURL)
                    dataTableModalEntityBySentiment(1, options)
                }            
            },
        },
        plotOptions: {
            bar: {
                horizontal: true,
                borderRadius: 6,
                barHeight: "50",
            },
        },
        stroke: {
            width: 1,
            colors: ["#fff"],
        },
        xaxis: {
            categories: [],
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val;
                },
            },
        },
        fill: {
            opacity: 1,
        },
        legend: { show: false },
        colors: [config.positive, config.neutral, config.negative]
    };
    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": filtersValues.languages,
        "sources": filtersValues.sources,
        "sourcesID": filtersValues.sourcesID,
        "limit": limit.value
    })
    fetch(`/api/classification-by-sentiment/${window.project_id}/?` + urlParams)
    .then((response) => response.json())
    .then((data) => {
        let positiveCount = {
            name: 'Positive',
            data:[]
        }
        let neutralCount = {
            name: 'Neutral',
            data:[]
        }
        let negativeCount = {
            name: 'Negative',
            data:[]
        }
        let categories = []
        for (let element of data) {
            positiveCount.data.push(element.positiveCount)    
            negativeCount.data.push(element.negativeCount)    
            neutralCount.data.push(element.neutralCount)    
            categories.push(element.classificationLabel)
            mapClassificationAndID[element.classificationLabel] = element.classificationID
        }
        options.series.push(positiveCount, neutralCount, negativeCount)
        options.xaxis.categories = categories
        graphContainer.innerHTML = "";
        chart = new ApexCharts(graphContainer, options);
        chart.render();
        update.finishUpdate()
    });
}

limit.addEventListener("change", (e)=>{
    createGraph()
})