import config from "../config";

import {update, createHTMLForGraphsContainer as createHTML} from '../helpers/helpers'
let html = 
`
<div class="col-12 project-card">
<div class="project-card-inner">
  <div class="chart-title  align-items-center d-flex flex-wrap">
    <h4>Aspect Co-Occurrence (last 30 days of data) <a href="#" data-toggle="tooltip" data-placement="top" title="Need help?">
        <i class="fe fe-help-circle"></i>
      </a> </h4>
  </div>
  <div class="chart-wrap">
    <div id="co-occurrence-graph" >
    </div>
  </div>
</div>
</div>
`
export function createGraph(){
    createHTML(html)
    update.startUpdate()
    let div = document.querySelector("#co-occurrence-graph")
    div.innerHTML = "Loading..."
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
            div.innerHTML = ""
            let chart = new ApexCharts(
                div,
                chartOptions
            );
            chart.render();
            update.finishUpdate()
        });     
}
