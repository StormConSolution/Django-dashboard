import {update} from '../helpers/helpers'
import {getFilters} from '../helpers/filters'
let div = document.querySelector("#emotion-aspect-co-occurrence")
let chart
export function createGraph(){
    update.startUpdate()
    if(chart){
        chart.destroy()
    }
    div.innerHTML = "Loading..."
    var chartOptions = {
        series: [],
        chart: {
            height: 480,
            type: "heatmap",
        },
        plotOptions: {
            heatmap: {
                shadeIntensity: 0,
                radius: 0,
                colorScale: {
                    ranges: [
                        {
                            from: 0,
                            to: 20,
                            name: "0-20",
                            color: "#E2E0FB",
                        },
                        {
                            from: 21,
                            to: 40,
                            name: "21-40",
                            color: "#D4D0FA",
                        },
                        {
                            from: 41,
                            to: 60,
                            name: "41-60 ",
                            color: "#C6C1F8",
                        },
                        {
                            from: 61,
                            to: 80,
                            name: "61-80",
                            color: "#968DF3",
                        },
                        {
                            from: 81,
                            to: 99,
                            name: "81-99",
                            color: "#8075F1",
                        },
                        {
                            from: 100,
                            to: 100,
                            name: "100",
                            color: "#7367F0",
                        },
                    ],
                },
            },
        },
        dataLabels: {
            enabled: false,
            style: {
                fontSize: "14px",
                fontFamily: "Helvetica, Arial, sans-serif",
                fontWeight: "bold",
            },
        },
        legend: {
            position: "bottom",
    
            markers: {
                width: 30,
            },
        },
    
        stroke: {
            width: 1,
        },
        xaxis: {
            type: "category",
            categories: [],
        },
    };
    let project_id = window.project_id;
    let currentEntity = ""
    let maxEmotions = document.querySelector("#emotion-aspect-co-occurrence-max-emotions").value
    let countEmotions = 0
    let filtersValues = getFilters()
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": filtersValues.languages,
        "sourcesID": filtersValues.sourcesID
    })
    fetch(`/api/entity-aspect-for-emotion/${project_id}/?` + urlParams)
        .then((response) => response.json())
        .then((data) => {
            let series = []
            let seriesData = []
            for(let element of data){
                    if(currentEntity != "" && currentEntity != element.entityLabel){
                        series.push({name: currentEntity, data: seriesData})
                        seriesData = []
                        countEmotions++
                        if(countEmotions==maxEmotions){
                            break
                        }
                    }
                    seriesData.push({x: element.aspectLabel, y:(element.aspectCount/element.entityCount * 100).toFixed(2)})
                    currentEntity = element.entityLabel
            }
            chartOptions.series = series
            div.innerHTML = ""
            chart = new ApexCharts(
                div,
                chartOptions
            );
            chart.render();
            update.finishUpdate()
        });     
}
document.querySelector("#emotion-aspect-co-occurrence-max-emotions").addEventListener("change", ()=>{
    createGraph()
})