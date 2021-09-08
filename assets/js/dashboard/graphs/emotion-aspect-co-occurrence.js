import {update} from '../helpers/helpers'
import {normalFiltersURL, metadataFiltersURL} from '../helpers/filters'
import {setShowEmotionAspectCoOccurrence as show} from "../../project-details"
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
                shadeIntensity: 0.3,
                radius: 0,
                colorScale: {
                    ranges: [
                        {
                            from: -10,
                            to: 20,
                            name: "0-20 %",
                            color: "#E2E0FB",
                        },
                        {
                            from: 20,
                            to: 40,
                            name: "20-40 %",
                            color: "#D4D0FA",
                        },
                        {
                            from: 40,
                            to: 60,
                            name: "40-60 %",
                            color: "#C6C1F8",
                        },
                        {
                            from: 60,
                            to: 80,
                            name: "60-80 %",
                            color: "#968DF3",
                        },
                        {
                            from: 80,
                            to: 100,
                            name: "80-100 %",
                            color: "#8075F1",
                        }
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
        tooltip: {
            y: {
                formatter: function (val) {
                    return val+'%';
                },
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
    let urlParams =  "&" +  metadataFiltersURL()+ "&" + normalFiltersURL()
    fetch(`/api/entity-aspect-for-emotion/${project_id}/?` + urlParams)
        .then((response) => response.json())
        .then((data) => {
            if(Object.keys(data).length==0){
                document
                .querySelector("#emotion-aspect-co-occurrence-container")
                .style.display = "none"
                show(false)
            }
            let series = []
            let seriesData = []
            let allAspects = []
            if(Object.keys(data).length !== 0){
                for(let element of data){
                    if(!allAspects.includes(element.aspectLabel)){
                        allAspects.push(element.aspectLabel)
                    }
                }
            }
            let insertedAspects = []
            if(Object.keys(data).length !== 0){
                for(let element of data){
                    if(currentEntity != "" && currentEntity != element.entityLabel){
                        let notInsertedAspects = allAspects.filter(x => !insertedAspects.includes(x))
                        for(let notInsertedAspect of notInsertedAspects){
                            seriesData.push({x:notInsertedAspect, y:0.00})

                        }
                        series.push({name: currentEntity, data: seriesData})
                        seriesData = []
                        insertedAspects = []
                        countEmotions++
                        if(countEmotions==maxEmotions){
                            break
                        }
                    }
                    seriesData.push({x: element.aspectLabel, y:(element.aspectCount/element.entityCount * 100).toFixed(2)})
                    insertedAspects.push(element.aspectLabel)
                    currentEntity = element.entityLabel
                }
                chartOptions.series = series
                chart = new ApexCharts(
                    div,
                    chartOptions
                );
                div.innerHTML = ""
                chart.render();
            } else {

                div.innerHTML = ""
            }
            update.finishUpdate()
        });     
}
document.querySelector("#emotion-aspect-co-occurrence-max-emotions").addEventListener("change", ()=>{
    createGraph()
})
