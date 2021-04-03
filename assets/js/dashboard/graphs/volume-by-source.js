import config from "../config";

let chart
export function createGraph(){
    if(chart){
        chart.destroy()
    }
    var chartOptions = {
        series: [],
        colors: [config.neutral],
        chart: {
            type: "bar",
            height: 320,
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
    fetch(`/api/volume-by-source/${project_id}/`)
        .then((response) => response.json())
        .then((data) => {
            let series = []
            let categories = []
            for(let element of data){
                series.push(element.sourceCount)
                categories.push(element.sourceName)
            }
            chartOptions.series.push({
                data: series
            })
            chartOptions.xaxis.categories = categories
            chart = new ApexCharts(
                document.querySelector("#volume-by-source"),
                chartOptions
            );
            chart.render();
        });    
}
