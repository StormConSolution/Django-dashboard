import config from "../config";
import {getFilters} from "../helpers/filters"
import {update} from '../helpers/helpers'
import {createTable as dataTableModalVolumeBySource} from '../tables/data_table_modal_volume_by_source'
import wordCloud from "./word-cloud-modal";
let chart
let div = document.querySelector("#volume-by-source")
let mapSourceAndID = {}

export function createGraph(){
    update.startUpdate()
    if(chart){
        chart.destroy()
    }
    div.innerHTML = "Loading..."
    var chartOptions = {
        series: [],
        colors: [config.neutral],
        chart: {
            type: "bar",
            height: 320,
            events: {
                dataPointSelection: function(event, chartContext, config) {
                    let source = config.w.config.xaxis.categories[config.dataPointIndex]
                    let options = {}
                    options.sourceID = mapSourceAndID[source]
                    let wordCloudURL = `/api/new-data/project/${window.project_id}/?format=word-cloud&` + new URLSearchParams({
                        "sentiment": encodeURIComponent(options.sentiment),
                        "languages": encodeURIComponent(filtersValues.languages),
                        "sources": filtersValues.sources,
                        "sourcesID": options.sourceID,
                        "date-from": filtersValues.dateFrom,
                        "date-to": filtersValues.dateTo
                    })
                    wordCloud(wordCloudURL) 
                    document.querySelector("#data-table-modal").style.display = "block"
                    dataTableModalVolumeBySource(1, options)
                }            
            }
        },
        plotOptions: {
            bar: {
                borderRadius: 6,
                horizontal: true,
                barHeight: "24",
            },
        },
        dataLabels: {
            enabled: false,
        },
        xaxis: {
            categories: []
        }
    };
    let project_id = window.project_id;
    let filtersValues = getFilters()
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": filtersValues.languages,
        "sourcesID": filtersValues.sourcesID
    })
    fetch(`/api/volume-by-source/${project_id}/?` + urlParams)
        .then((response) => response.json())
        .then((data) => {
            let series = []
            let categories = []
            for(let element of data){
                series.push(element.sourceCount)
                categories.push(element.sourceName)
                mapSourceAndID[element.sourceName] = element.sourceID
            }
            chartOptions.series.push({
                data: series
            })
            chartOptions.xaxis.categories = categories
            div.innerHTML = ""
            chart = new ApexCharts(
                div,
                chartOptions
            );
            chart.render();
            update.finishUpdate()
        });    
}
