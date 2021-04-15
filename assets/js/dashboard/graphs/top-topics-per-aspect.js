import config from "../config";
import {update, createHTMLForGraphsContainer as createHTML} from '../helpers/helpers'

let chart
function topicsPerAspect(maxTopicsPerAspect) {
    let data = topicsPerAspectData;
    for (aspect in data.aspects) {
        let series = [];
        let labels = [];
        let i = 0;
        if (data.aspects[aspect].topics.length == 0) {
            continue
        }
        for (let topic of data.aspects[aspect].topics) {
            i++;
            if (i > maxTopicsPerAspect) {
                break
            }
            labels.push(topic.topic)
            series.push(topic.count)
        }
        var options = {
            responsive: [
                {
                    breakpoint: 700,
                    options: {
                        chart: {
                            width: "100%"
                        }
                    }
                }
            ],
            legend: {
                position: 'top'
            },
            pie: {
                donut: {
                    labels: {
                        show: true,
                        name: {}
                    }
                }
            },
            series: series,
            labels: labels,
            chart: {
                type: 'donut',
                width: '500'
            },
            plotOptions: {
                pie: {
                    donut: {
                        size: '70%',
                        labels: {
                            show: true,

                            name: {

                                show: true,
                                formatter: (e) => {
                                    if (e) {
                                        return 'Topic: ' + e
                                    }
                                }
                            }

                        }
                    }
                }
            }
        };
        let h2 = document.createElement("h2");
        h2.innerHTML = 'ASPECT: ' + aspect;
        h2.style.marginTop = "1rem";
        h2.style.marginLeft = "auto";
        h2.style.marginRight = "auto";
        h2.style.textAlign = "center"
        let div = document.createElement('div');
        div.className = 'donut-container';
        // div.style.marginLeft = 'auto';
        document.querySelector("#top-topics-per-aspect").append(h2);
        document.querySelector("#top-topics-per-aspect").append(div);
        document.querySelector("#top-topics-per-aspect").innerHTML = ""
        chart = new ApexCharts(div, options);
        chart.render();
    }

}
let topicsPerAspectData;
document.querySelector("#top-topics-per-aspect").innerHTML = "Loading...";
fetch('/topics-per-aspect/' + window.project_id + '/').then(response => response.json()).then(data => {
    topicsPerAspectData = data;
    topicsPerAspect(6);
})
document.getElementById('select-max-topics-per-aspect').addEventListener('change', (e) => {
    let maxTopicsPerAspect = e.target.value
    topicsPerAspect(maxTopicsPerAspect)
})
