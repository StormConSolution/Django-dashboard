/*=========================================================================================
    File Name: dashboard-analytics.js
    Description: dashboard analytics page content with Apexchart Examples
    ----------------------------------------------------------------------------------------
    Item Name: Frest HTML Admin Template
    Version: 1.0
    Author: PIXINVENT
    Author URL: http://www.themeforest.net/user/pixinvent
==========================================================================================*/

$(window).on("load", function () {
  var $primary = "#5A8DEE";
  var $success = "#39DA8A";
  var $danger = "#FF5B5C";
  var $warning = "#FDAC41";
  var $info = "#00CFDD";
  var $label_color = "#FFFFFF";
  var $primary_light = "#E2ECFF";
  var $danger_light = "#ffeed9";
  var $gray_light = "#828D99";
  var $label_trend = "#f5eff7";
  var $sub_label_color = "#596778";
  var $radial_bg = "#e7edf3";
  var $positive = "#537fd6";
  var $negative = "#dd9942";

  // Bar Chart
  // ---------
  const postive_label = project_data.sentiment_t_data[0].data;
  const list = postive_label.concat(project_data.sentiment_t_data[1].data);

  function max_label(arr) {
    var len = arr.length,
      max = -Infinity;
    while (len--) {
      if (arr[len] > max) {
        max = arr[len];
      }
    }
    return max;
  }
  function min_label(arr) {
    var len = arr.length,
      min = Infinity;
    while (len--) {
      if (arr[len] < min) {
        min = arr[len];
      }
    }
    return min;
  }
  const max = max_label(list);
  const min = min_label(list);

  var analyticsBarChartOptions = {
    chart: {
      height: 260,
      type: "line",
      toolbar: {
        show: false,
      },
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: "20%",
        endingShape: "flat",
      },
    },
    legend: {
      horizontalAlign: "right",
      offsetY: -10,
      markers: {
        radius: 50,
        height: 8,
        width: 8,
      },
    },
    dataLabels: {
      enabled: false,
    },
    colors: [$positive, $negative],
    fill: {
      type: "gradient",
      gradient: {
        shade: "light",
        type: "vertical",
        inverseColors: true,
        opacityFrom: 1,
        opacityTo: 1,
        stops: [0, 70, 100],
      },
    },
    series: project_data.sentiment_t_data,
    xaxis: {
      categories: project_data.sentiment_t_labels,
      axisBorder: {
        show: false,
      },
      axisTicks: {
        show: false,
      },
      labels: {
        style: {
          colors: $label_trend,
        },
      },
    },
    yaxis: {
      min: min,
      max: max,
      forceNiceScale: true,
      range: 10,
      tickAmount: 10,
      labels: {
        style: {
          colors: $label_trend,
        },
      },
    },
    legend: {
      show: false,
    },
    tooltip: {
	  theme:'dark',
      y: {
        formatter: function (val) {
          return val;
        },
      },
    },
  };

  var analyticsBarChart = new ApexCharts(
    document.querySelector("#analytics-bar-chart"),
    analyticsBarChartOptions
  );

  analyticsBarChart.render();

  //-----------

  // Donut Chart
  // ---------------------
  var donutChartOption = {
    chart: {
      width: 320,
      type: "donut",
    },
    dataLabels: {
      enabled: false,
    },
    series: project_data.sentiment_f_data,
    labels: ["Positive", "Negative", "Neutral"],
    stroke: {
      width: 0,
      lineCap: "round",
    },
    colors: [$positive, $negative, $info],
    plotOptions: {
      pie: {
        donut: {
          size: "90%",
          labels: {
            show: true,
            name: {
              show: true,
              fontSize: "15px",
              colors: $sub_label_color,
              offsetY: 20,
              fontFamily: "IBM Plex Sans",
            },
            value: {
              show: true,
              fontSize: "26px",
              fontFamily: "Rubik",
              color: $label_color,
              offsetY: -20,
              formatter: function (val) {
                return val;
              },
            },
            total: {
              show: true,
              label: "Sentiments",
              color: $label_color,
              formatter: function (w) {
                return w.globals.seriesTotals.reduce(function (a, b) {
                  return a + b;
                }, 0);
              },
            },
          },
        },
      },
    },
    legend: {
      show: false,
    },
  };

  var donutChart = new ApexCharts(
    document.querySelector("#donut-chart"),
    donutChartOption
  );

  donutChart.render();

	let positiveAspectSeries = [];
	let negativeAspectSeries = [];
	let aspectLabels = [];

	for (i=0; i<project_data.aspect_data.length; i++) {
		aspect = project_data.aspect_data[i];
		positiveAspectSeries.push(aspect.pos);
		negativeAspectSeries.push(-1*aspect.neg);
		aspectLabels.push(aspect.label);
	}
	
	// Aspect by sentiment graph.
	  var options = {
          series: [{
          name: 'Positive',
          data: positiveAspectSeries
        },
        {
          name: 'Negative',
          data: negativeAspectSeries
        }
        ],
          chart: {
          type: 'bar',
          height: 640,
          stacked: true
        },
        colors: [$positive, $negative],
        plotOptions: {
          bar: {
            horizontal: true,
            barHeight: '80%',
            borderRadius: 7,
            radiusOnLastStackedBar: false
          },
        },
        dataLabels: {
          enabled: false
        },
        grid: {
          xaxis: {
            lines: {
              show: false
            }
          }
        },
        tooltip: {
		  theme: 'dark',
          shared: false,
          x: {
            formatter: function (val) {
              return val
            }
          },
          y: {
            formatter: function (val) {
              return Math.abs(val)
            }
          }
        },
        xaxis: {
          categories: aspectLabels,
          title: {
            text: 'Aspect'
          },
		  labels: {
			  style: {
				  colors: new Array(aspectLabels.length).fill('#ffffff')
			  }
		  }
        },
        yaxis: {
		  labels: {
			  style: {
				  colors: new Array(aspectLabels.length).fill('#ffffff')
			  }
		  }
        }
	};

	var chart = new ApexCharts(document.querySelector("#aspect-by-sentiment"), options);
	chart.render();
	
	  var sourceOptions = {
          series: [{
			  name: 'Data',
			  data: project_data.source_by_count.series
			}
		  ],
          chart: {
          type: 'bar',
          height: 480
        },
        plotOptions: {
          bar: {
            horizontal: true,
            columnWidth: '55%'
          },
        },
        dataLabels: {
          enabled: true,
			formatter: function(val, opts) {
				// Calculate the percent.
				let percent = ((val / project_data.source_by_count.total) * 100).toFixed(2);
				return `${val} (${percent}%)`;
			},
			offsetX:50
        },
        stroke: {
          show: true,
          width: 2,
          colors: ['transparent']
        },
        xaxis: {
          categories: project_data.source_by_count.labels,
		  labels: {
			  style: {
				  colors: new Array(project_data.source_by_count.labels.length).fill('#ffffff')
			  }
		  }
        },
	    colors: ['#6a9dcb'],
        fill: {
          opacity: 1
        },
		yaxis: {
		  floating: true,
		  axisTicks: {
			show: false
		  },
		  axisBorder: {
			show: false
		  },
		  labels: {
			show: true,
			style: {
				colors: new Array(project_data.source_by_count.labels.length).fill('#ffffff')
			}
		  },
		}, 
		grid: {
			show:true
		},
		tooltip: {
			enabled:false
		}
	};

	// Render a chart for source volume.
	var sourceByVolumeChart = new ApexCharts(
		document.querySelector('#source-volume'),
		sourceOptions
	);
	sourceByVolumeChart.render();

	// Render the aspect co-occurence.
	series_data = project_data.aspect_cooccurrence_data;
	if (series_data.length > 0) {
		options = {
			chart: {
				height: 600,
				type: 'heatmap'
			},
			legend: {
			  show: false,
			},
			series: series_data,
			tooltip: {
			  theme:'dark'
			},
			xaxis: {
			  labels: {
				  style: {
					  colors: new Array(aspectLabels.length).fill('#ffffff')
				  },
				  rotateAlways:true,
				  rotate:-45
			  }
			},
			yaxis: {
			  labels: {
				  style: {
					  colors: new Array(aspectLabels.length).fill('#ffffff')
				  }
			  }
			},
			plotOptions: {
				heatmap: {
					shadeIntensity: 0.75,
					enableShaded: true,
					radius: 0,
					useFillColorAsStroke: true,
					min:0,
					max:100,
					colorScale:{
						ranges:[
							{
								from:0,
								to:100,
								color:'#6a9dcb'
							}
						]
					}
				}
			}
		}
		var aspectCoChart= new ApexCharts(document.querySelector('#aspect-co'), options)
		aspectCoChart.render();
	}

});
