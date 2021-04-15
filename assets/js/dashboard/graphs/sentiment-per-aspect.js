import config from "../config";
import {update, createHTMLForGraphsContainer as createHTML} from '../helpers/helpers'

let div = document.querySelector("#sentiment-for-each-aspect")
export function createGraph(){
    update.startUpdate()
    div.innerHTML = "Loading..."
    var aspect_data = window.project_data.aspect_data;
    let positives = [];
    let negatives = [];
    let neutrals = [];
    let categories = [];
    for (let data of aspect_data) {
        categories.push(data.label);
        positives.push(data.pos);
        negatives.push(data.neg);
        neutrals.push(data.count - data.pos - data.neg);
    }
    var options = {
        series: [
            {
                name: 'Positive',
                data: positives
            }, {
                name: 'Neutral',
                data: neutrals
            }, {
                name: 'Negative',
                data: negatives
            }
        ],
        chart: {
            type: 'bar',
            height: 350,
            stacked: true,
            stackType: '100%'
        },
        plotOptions: {
            bar: {
                horizontal: true
            }
        },
        stroke: {
            width: 1
        },
        xaxis: {
            categories: categories,
            labels: {
                style: {
                    colors: config.label_trend
                }
            }
        },
        tooltip: {
            y: {
                formatter: function (val) {
                    return val;
                }
            },
            theme: 'dark'
    
        },
        fill: {
            opacity: 1
    
        },
        legend: {
            position: 'top',
            horizontalAlign: 'left',
            offsetX: 40,
            labels: {
                colors: ['white']
            }
        },
    };
    let graphHeight = 0;
    if (options.xaxis.categories.length < 5) {
        graphHeight = 300;
    } else {
        graphHeight = options.xaxis.categories.length * 40;
    } options.chart.height = graphHeight;
    options.yaxis = {
        labels: {
            style: {
                colors: 'white'
            }
        }
    }
    div.innerHTML = ""
    var chart = new ApexCharts(div, options);
    chart.render();
    update.finishUpdate()
}

