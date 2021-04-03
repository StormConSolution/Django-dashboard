import config from "../config";

export function createGraph(){
    var chartOptions = {
        series: [],
        chart: {
            height: 480,
            type: "heatmap",
        },
        plotOptions: {
            heatmap: {
                shadeIntensity: 0.5,
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
    fetch(`/api/co-occurence/${project_id}/`)
        .then((response) => response.json())
        .then((data) => {
            chartOptions.series = data
            let chart = new ApexCharts(
                document.querySelector("#co-occurrence-graph"),
                chartOptions
            );
            chart.render();
        });     
}
