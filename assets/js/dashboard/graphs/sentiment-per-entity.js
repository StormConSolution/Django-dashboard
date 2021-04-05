import config from "../config";
let chart;
function createSentimentPerEntityGraph(max_entities) {

    update.startUpdate()
    fetch('/sentiment-per-entity/' + window.project_id + '/?max-entities=' + max_entities).then(response => response.json()).then(data => {
        var options = {
            chart: {
                type: 'bar',
                height: 350,
                stacked: true,
                stackType: '100%',
                events: {
                    click: function (event, chartContext, config) {
                        let seriesIndex = config.seriesIndex;
                        let dataPointIndex = config.dataPointIndex
                        let modal_data;
                        let sentiment = '';
                        if (seriesIndex == 0) {
                            sentiment = "Positive"
                            modal_data = data[dataPointIndex].data.filter(element => element.sentiment > 0)
                        } else if (seriesIndex == 1) {
                            sentiment = "Neutral"
                            modal_data = data[dataPointIndex].data.filter(element => element.sentiment == 0)
                        } else if (seriesIndex == 2) {
                            sentiment = "Negative"
                            modal_data = data[dataPointIndex].data.filter(element => element.sentiment < 0)
                        }
                        let modalElement = document.getElementById("aspectModal")
                        modalElement.style.display = "block"
                        modalElement.classList.add("show")
                        modalElement.setAttribute("aria-modal", "true")
                        modalElement.setAttribute("aria-hidden", "false")
                        $('#aspectModal').modal();
                        $("#modal-title").html(sentiment + " data for entity: " + data[dataPointIndex].entity_label)
                        $("#modal-table").html("")
                        $("#modal-table").append("<thead><tr><th>Text</th><th>Sentiment</th></tr></thead>")
                        $("#modal-table").append("<tbody></tbody>")
                        for (let element of modal_data) {
                            $("#modal-table > tbody").append(`<tr><td>${
                                element.text
                            }</td><td>${
                                element.sentiment
                            }</td></tr>`)
                        }
                    }
                }
            },
            plotOptions: {
                bar: {
                    horizontal: true
                }
            },
            stroke: {
                width: 1
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
            colors: [config.$positive, config.$info, config.$negative]
        };
        let positives = [];
        let negatives = [];
        let neutrals = [];
        let categories = [];
        for (let element of data) {
            categories.push(element.entity_label);
            positives.push(element.positive_count);
            negatives.push(element.negative_count);
            neutrals.push(element.neutral_count);
        }
        options.series = [
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
        ];
        options.xaxis = {
            categories: categories,
            labels: {
                style: {
                    colors: config.label_trend
                }
            }
        };
        options.yaxis = {
            labels: {
                style: {
                    colors: 'white'
                }
            }
        }
        let graphHeight = 0;
        if (options.xaxis.categories.length < 5) {
            graphHeight = 300;
        } else {
            graphHeight = options.xaxis.categories.length * 40;
        } options.chart.height = graphHeight;
        if (chart) {
            chart.destroy()
        }
        chart = new ApexCharts(document.querySelector("#sentiment-for-each-entity"), options);
        chart.render();
        update.finishUpdate()
    })
}
createSentimentPerEntityGraph(8);
function updateGraph(){
    let maxEntities = e.target.value;
    document.getElementById("sentiment-for-each-entity").innerHTML = "";
    if(chart){
        chart.destroy();
    }
    createSentimentPerEntityGraph(maxEntities);
}
document.getElementById("select-max-top-sentiment-per-entity").addEventListener("change", (e) => {
    updateGraph()
})
