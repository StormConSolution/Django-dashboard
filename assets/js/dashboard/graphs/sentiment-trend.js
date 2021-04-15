import config from "../config";
import {update, createHTMLForGraphsContainer as createHTML} from '../helpers/helpers'
import { getFilters } from "../helpers/filters";
let chart;
let def = 1;
let html = `
        <div class="project-card-inner">
        <div class="chart-title  align-items-center d-flex flex-wrap">
            <h4 class="col p-0 sentiment-trend ">Sentiment
            Trend <a href="#" data-toggle="tooltip" data-placement="top" title="Need help?">
                <i class="fe fe-help-circle"></i>
            </a> </h4>
            <div class="col-auto ml-auto p-0">
            <div class="row">
                <div class="col chart-total-data">
                <h2 id="sentiment-trend-total">0</h2>
                <span>Total positives and negatives </span>
                </div>
                <div class="col chart-positive-data">
                <h2 id="sentiment-trend-total-positives">0</h2>
                <span>Total positive</span>
                </div>
                <div class="col chart-negative-data">
                <h2 id="sentiment-trend-total-negatives">0</h2>
                <span>Total negative</span>
                </div>
            </div>
            </div>

        </div>
        <div class="chart-wrap">
            <div id="sentiment-trend-graph" >

            </div>
        </div>
        </div>
        `
export function createGraph(){
    createHTML(html)
    let div = document.querySelector("#sentiment-trend-graph")
    update.startUpdate()
    if(chart){
        chart.destroy()
    }
    div.innerHTML = "Loading..."
    document.getElementById("sentiment-trend-total").innerHTML = 0
    document.getElementById("sentiment-trend-total-positives").innerHTML = 0
    document.getElementById("sentiment-trend-total-negatives").innerHTML = 0
    var projectId = window.project_id;
    let filtersValues = getFilters() 
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": filtersValues.languages,
        "sources": filtersValues.sources,
        "default": def
    })
    fetch(`/api/sentiment-trend/${projectId}/?` + urlParams)
        .then((response) => response.json())
        .then((data) => {
            def = 0
            let chartOptions = {
                series: [],
                colors: ["#28C76F", "#EA5455"],
                chart: {
                    height: 320,
                    type: "line",
                    toolbar: {
                        show: false,
                    },
                },
    
                dataLabels: {
                    enabled: false,
                },
                stroke: {
                    curve: "smooth",
                    width: 3,
                },
                legend: {
                    show: false,
                },
                xaxis: {
                    categories: [],
                },
                tooltip: {
                    x: {
                        format: "MM/yyyy",
                    },
                },
            };
            let positives = [];
            let negatives = [];
            let categories = [];
            let totalPositives = 0
            let totalNegatives = 0
            for (let element of data) {
                totalPositives += element.positivesCount
                totalNegatives += element.negativesCount
                positives.push(totalPositives);
                negatives.push(totalNegatives);
                categories.push(element.date);
            }
            chartOptions.series.push(
                { name: "Positives", data: positives },
                { name: "Negatives", data: negatives }
            );
    
            chartOptions.xaxis.categories = categories;
    
            document.getElementById("sentiment-trend-total").innerHTML = totalPositives + totalNegatives
            document.getElementById("sentiment-trend-total-positives").innerHTML = totalPositives
            document.getElementById("sentiment-trend-total-negatives").innerHTML = totalNegatives
            div.innerHTML = ""
            chart = new ApexCharts(
                div,
                chartOptions
            );
            
            chart.render();
            update.finishUpdate()
        });
    
}

