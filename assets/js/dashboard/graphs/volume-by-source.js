import config from "../config";
import {getFilters} from "../helpers/filters"
import {update, createHTMLForGraphsContainer as createHTML} from '../helpers/helpers'
import {createTable as dataTableModalVolumeBySource} from '../tables/data_table_modal_volume_by_source'
let chart
let html = `
<div class="col-12 project-card">
<div class="project-card-inner">
  <div class="chart-title  align-items-center d-flex flex-wrap">
    <h4>Volume By Source <a href="#" data-toggle="tooltip" data-placement="top" title="Need help?">
        <i class="fe fe-help-circle"></i>
      </a> </h4>
  </div>
  <div class="chart-wrap">
    <div id="volume-by-source" >
    </div>
  </div>
</div>
</div
`
export function createGraph(){
    update.startUpdate()
    createHTML(html)
    let div = document.querySelector("#volume-by-source")
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
                    options.source = source
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
        "sources": filtersValues.sources
    })
    fetch(`/api/volume-by-source/${project_id}/?` + urlParams)
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
            div.innerHTML = ""
            chart = new ApexCharts(
                div,
                chartOptions
            );
            chart.render();
            update.finishUpdate()
        });    
}
