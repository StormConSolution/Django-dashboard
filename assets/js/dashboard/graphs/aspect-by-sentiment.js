import config from "../config";
import { getFilters } from "../helpers/filters";
import {update} from '../helpers/helpers'
import {createTable as dataTableModalDataPerAspectAndSentiment} from "../tables/data_table_modal_aspect_by_sentiment"
let chart 
export function createGraph() {
    update.startUpdate()
    if(chart){
        chart.destroy()
    }
    document.querySelector("#aspect-by-sentiment").innerHTML = "Loading..."
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
                    console.log(aspect)
                    console.log(count)
                    document.querySelector("#data-table-modal").style.display = "block"
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
        "sourcesID": filtersValues.sourcesID
    })
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
            document.querySelector("#aspect-by-sentiment").innerHTML = ""
                chart = new ApexCharts(
                document.querySelector("#aspect-by-sentiment"),
                chartOptions
            );
            chart.render();
            update.finishUpdate()
        });
}
