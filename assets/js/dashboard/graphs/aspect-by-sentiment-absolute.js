import { getFilters, metadataFiltersURL } from "../helpers/filters";
import {update} from '../helpers/helpers'
import {createTable as dataTableModalDataPerAspectAndSentiment} from "../tables/data_table_modal"
import wordCloud from './word-cloud-modal'
let chart 
let graphContainer = document.querySelector("#aspect-by-sentiment-absolute")
let limitDiv = document.querySelector("#aspect-by-sentiment-absolute-limit")
export function createGraph() {

    update.startUpdate()
    if(chart){
        chart.destroy()
    }
    graphContainer.innerHTML = "Loading..."
    var chartOptions = {
        series: [],
        chart: {
            type: "bar",
            height: 440,
            stacked: true,
            events: {
                dataPointSelection: function(event, chartContext, config) {
                    let aspect = config.w.config.xaxis.categories[config.dataPointIndex]
                    let count = config.w.config.series[config.seriesIndex].data[config.dataPointIndex]
                    let options = {}
                    if(count > 0){
                        options.sentiment = "positive"
                    } else {
                        options.sentiment = "negative"
                    }
                    options.aspect = aspect
                    let filtersValues = getFilters()
                    document.querySelector("#data-table-modal").style.display = "block"
                    let wordCloudURL = `/api/data-per-aspect/${window.project_id}/?format=word-cloud&` + new URLSearchParams({
                        "sentiment": encodeURIComponent(options.sentiment),
                        "aspect-label": encodeURIComponent(options.aspect),
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": filtersValues.sources,
                        "sourcesID": filtersValues.sourcesID,
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo
                    }) + "&" +  metadataFiltersURL()
                    options.csvURL = `/api/data-per-aspect/${window.project_id}/?format=csv&` + new URLSearchParams({
                        "sentiment": encodeURIComponent(options.sentiment),
                        "aspect-label": encodeURIComponent(options.aspect),
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": filtersValues.sources,
                        "sourcesID": filtersValues.sourcesID,
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo
                    })+ "&" +  metadataFiltersURL()
                    options.dataURL = `/api/data-per-aspect/${window.project_id}/?` + new URLSearchParams({
                        "sentiment": encodeURIComponent(options.sentiment),
                        "aspect-label": encodeURIComponent(options.aspect), 
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo,
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": filtersValues.sources,
                        "sourcesID": filtersValues.sourcesID
                    })+ "&" +  metadataFiltersURL()
                    wordCloud(wordCloudURL)
                    dataTableModalDataPerAspectAndSentiment(1, options)
                }            
            }
        },
        legend: { show: false },
        colors: ["#28C76F", "#EA5455"],
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

    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": filtersValues.languages,
        "sources": filtersValues.sources,
        "sourcesID": filtersValues.sourcesID,
        "limit": limitDiv.value
    })+ "&" +  metadataFiltersURL()
    fetch(`/api/sentiment-per-aspect/${window.project_id}/?` + urlParams)
        .then((response) => response.json())
        .then((data) => {
            let positiveData = [];
            let negativeData = [];
            let aspects = [];
            let maxPositive = 0;
            let maxNegative = 0;
            for (let element of data) {
                positiveData.push(element.positiveCount);
                negativeData.push(-element.negativeCount);
                aspects.push(element.aspectLabel);
                if (element.positiveCount > maxPositive) {
                    maxPositive = element.positiveCount;
                }
                if (element.negativeCount > maxNegative) {
                    maxNegative = element.negativeCount;
                }
            }
            chartOptions.series.push({
                name: "Positives",
                data: positiveData,
            });
            chartOptions.series.push({
                name: "Negatives",
                data: negativeData,
            });
            chartOptions.yaxis.max =
                maxPositive + Math.round(maxPositive * 0.1);
            chartOptions.yaxis.min =
                -maxNegative - Math.round(maxNegative * 0.1);
            chartOptions.xaxis.categories = aspects;
            graphContainer.innerHTML = ""

            if(Object.keys(data).length !== 0){
            chart = new ApexCharts(
                graphContainer,
                chartOptions
            );
            chart.render();
            }
            update.finishUpdate()
        });
}

limitDiv.addEventListener("change", (e)=>{
    createGraph()
})