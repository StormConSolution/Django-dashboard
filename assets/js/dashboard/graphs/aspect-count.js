import config from "../config";
let colors = ["#28C76F", "#EA5455", "#00CFE8", "#7367F0", "#FF9F43"];
let colorsIndex = 0;

let aspectCountGraphs = document.querySelector("#aspect-count-graphs");

let project_id = window.project_id;
fetch(`/api/aspect-count/${project_id}/`)
    .then((response) => response.json())
    .then((data) => {
        let totalCount = 0
        for(let element of data){
            totalCount += element.aspectCount
        }
        for (let element of data) {
            let percentage = (element.aspectCount/totalCount * 100).toFixed(2)
            let id = `aspect-count-${element.aspectLabel}`
            let li = document.createElement("li")

            let domElement = `
            <a href="#" class="d-flex color-1">
            <small>${element.aspectLabel}</small>
            <b style="color:${colors[colorsIndex]};">${element.aspectCount}</b>
            <span>${percentage}%</span>
            <div class="round-chart">
              <div id="${id}"></div>
            </div>
            </a>
            `;
            li.innerHTML = domElement;
            aspectCountGraphs.append(li)
            let color = colors[colorsIndex];
            if(colorsIndex == colors.length - 1){
                colorsIndex = 0
            } else {
                colorsIndex++
            }

            let chartOptions = {
                series: [percentage],
                chart: {
                    type: "radialBar",
                    width: 30,
                    height: 30,
                    sparkline: {
                        enabled: true,
                    },
                },

                colors: [color],
                dataLabels: {
                    enabled: false,
                },
                plotOptions: {
                    radialBar: {
                        hollow: {
                            margin: 0,
                            size: "40%",
                        },
                        track: {
                            margin: 0,
                        },
                        dataLabels: {
                            show: false,
                        },
                    },
                },
            };
            let chart = new ApexCharts(
                document.querySelector(`#${id}`),
                chartOptions
            );
            chart.render();
        }
    });
