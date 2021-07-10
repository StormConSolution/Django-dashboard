import config from "../config";
import {normalFiltersURL, metadataFiltersURL} from "../helpers/filters"
import {update} from '../helpers/helpers'
import {createTable as dataTableModalVolumeBySource} from '../tables/data_table_modal'
import wordCloud from "./word-cloud-modal";
import {storeGraph} from '../pdf/pdf'

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
                    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
                    options.csvURL =`/api/new-data/project/${window.project_id}/?format=csv&` + new URLSearchParams({
                        "sentiment": options.sentiment
                    })+ "&" +  metadataFiltersURL() + "&" + normalFiltersURL()
                    options.dataURL =`/api/new-data/project/${window.project_id}/?` + new URLSearchParams({
                        "sentiment": options.sentiment
                    })+ "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
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
    let urlParams = metadataFiltersURL()+ "&" + normalFiltersURL()
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
            chart.render().then(()=>{
                setTimeout(function() {
                    chart.dataURI().then(({imgURI,blob})=>{
                        storeGraph('volume-by-source', imgURI)
                    })
                }, 1000) 
            }
            );
            update.finishUpdate()
        });    
}
