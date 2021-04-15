import config from "../config";
import * as filters from "../helpers/filters"
import {update, createHTMLForGraphsContainer as createHTML} from '../helpers/helpers'
import {createTable as dataTableModalPerSentiment} from "../tables/data_table_modal_data_per_sentiment"
let chart
let html = `
<div class="col-12 project-card" id="overall-graph">
<div class="row">
  <div class="col-12 pb-3 ">
    <div class="project-card-inner">
      <div class="chart-title pb-0 mb-3 border-0 ">
        <h4>Overall Sentiment <a href="#" data-toggle="tooltip" data-placement="top" title="Need help?">
            <i class="fe fe-help-circle"></i>
          </a> </h4>
      </div>
      <div id="overall-sentiment-chart"></div>
    </div>
  </div>
  <div class="col-6">
    <div class="project-card-inner">
      <div class="simple-data">
        <i class="fe fe-hash"></i>
        <h2 id="aspect-count"></h2>
        <span>Different Aspect </span>
      </div>
    </div>
  </div>
  <div class="col-6">
    <div class="project-card-inner">
      <div class="simple-data">
        <i class="fe fe-command"></i>
        <h2 id="source-count"></h2>
        <span>Different Source </span>
      </div>
    </div>
  </div>
</div>
</div>
`
function overallSentiment(data){
    var chartOptions = {
        colors: [config.positive, config.negative, config.neutral],
        chart: {
            height: 250,
            type: "donut",
            events: {
                dataPointSelection: function(event, chartContext, config) {
                    let sentiment = config.w.config.labels[config.dataPointIndex].toLowerCase()
                    let options = {}
                    options.sentiment = sentiment
                    document.querySelector("#data-table-modal").style.display = "block"
                    dataTableModalPerSentiment(1, options)
                }            
            }
        },
        dataLabels: {
            enabled: false,
        },
        legend: {
            position: "left",
        },
        plotOptions: {
            pie: {
                donut: {
                    labels: {
                        show: true,
                        total: {
                            showAlways: true,
                            show: true,
                        },
                    },
                },
            },
            radialBar: {
                hollow: {
                    size: "60%",
                },
            },
        },
        labels: ["Positive", "Negative", "Neutral"],
    };
    chartOptions.series = [data.positivesCount, data.negativesCount, data.neutralsCount]
    let div = document.querySelector("#overall-sentiment-chart")
    chart = new ApexCharts(div, chartOptions);
    chart.render();
}

function aspectAndSourceCount(data){
    let aspectCount = document.getElementById("aspect-count")
    let sourceCount = document.getElementById("source-count")
    aspectCount.innerHTML = data.aspectCount
    sourceCount.innerHTML = data.sourceCount
}

let project_id = window.project_id
export function createGraph(){
    createHTML(html)
    let div = document.querySelector("#overall-sentiment-chart")
    update.startUpdate()
    let filtersValues = filters.getFilters()
    let urlParams = new URLSearchParams({
        "date-from": filtersValues.dateFrom,
        "date-to": filtersValues.dateTo,
        "languages": encodeURIComponent(filtersValues.languages),
        "sources": encodeURIComponent(filtersValues.sources)
    })
    if(chart){
        chart.destroy()
    }
    //div.innerHTML = "Loading..."

    fetch(`/api/project-overview/${project_id}/?` + urlParams).then(response => response.json()).then(data => {
        //div.innerHTML = ""
        overallSentiment(data)
        aspectAndSourceCount(data)
        update.finishUpdate()
    })
}


