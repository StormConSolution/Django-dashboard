import config from "../config";
import { metadataFiltersURL , normalFiltersURL} from "../helpers/filters";
import { update } from "../helpers/helpers";
import {createTable as dataTableModalVolumeBySource} from '../tables/data_table_modal'
import wordCloud from "./word-cloud-modal";

let chart;
let container = document.querySelector("#source-by-sentiment-graph")
let maxSources = document.querySelector("#source-by-sentiment-max-sources")
let mapSourceAndID = {}

export function createGraph() {
    update.startUpdate();
    if (chart) {
        chart.destroy();
    }
    container.innerHTML = "Loading...";
    let options = {
        series: [],
        chart: {
            type: "bar",
            height: 440,
            stacked: true,
            stackType: "100%",
            events: {
                dataPointSelection: function(event, chartContext, config) {
                    let source = config.w.config.xaxis.categories[config.dataPointIndex]
                    let sentiment = config.w.config.series[config.seriesIndex].name
                    let options = {}
                    options.sourceID = mapSourceAndID[source]
                    options.sentiment = sentiment.toLowerCase()
                    document.querySelector("#data-table-modal").style.display = "block"
                    let wordCloudURL = `/api/new-data/project/${window.project_id}/?format=word-cloud&` + new URLSearchParams({
                        "sentiment": encodeURIComponent(options.sentiment),
                    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
                    options.csvURL =`/api/new-data/project/${window.project_id}/?format=csv&` + new URLSearchParams({
                        "sentiment": options.sentiment
                    })+ "&" +  metadataFiltersURL() + "&" + normalFiltersURL()
                    options.dataURL =`/api/new-data/project/${window.project_id}/?` + new URLSearchParams({
                        "sentiment": options.sentiment
                    })+ "&" +  metadataFiltersURL() + "&" + normalFiltersURL()
                    wordCloud(wordCloudURL)
                    dataTableModalVolumeBySource(1, options)
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
    let urlParams = new URLSearchParams({
        'limit':maxSources.value
    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
    fetch(`/api/source-by-sentiment/${window.project_id}/?` + urlParams)
    .then((response) => response.json())
    .then((data) => {
        let series = []
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
            categories.push(element.sourceLabel)
            mapSourceAndID[element.sourceLabel] = element.sourceID
        }
        options.series.push(positiveCount, neutralCount, negativeCount)
        options.xaxis.categories = categories
        container.innerHTML = ""
        chart = new ApexCharts(container, options);
        chart.render();
        update.finishUpdate()
    });
}


maxSources.addEventListener("change", (e)=>{
    createGraph()
})
