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

  // Radial-Success-chart
  // --------------------------------
  var radialSuccessoptions = {
    chart: {
      height: 40,
      width: 40,
      type: "radialBar",
    },
    grid: {
      show: false,
      padding: {
        left: -30,
        right: -30,
        top: 0,
      },
    },
    series: [30],
    colors: [$success],
    plotOptions: {
      radialBar: {
        hollow: {
          size: "30%",
        },
        dataLabels: {
          showOn: "always",
          name: {
            show: false,
          },
          value: {
            show: false,
          },
        },
      },
    },
    fill: {
      type: "gradient",
      gradient: {
        shade: "light",
        type: "horizontal",
        gradientToColors: [$success],
        opacityFrom: 1,
        opacityTo: 0.8,
        stops: [0, 70, 100],
      },
    },
    stroke: {
      lineCap: "round",
    },
  };
  var radialSuccessChart = new ApexCharts(
    document.querySelector("#radial-success-chart"),
    radialSuccessoptions
  );

  // radialSuccessChart.render();

  // Radial-Warning-chart
  // --------------------------------
  var radialWarningoptions = {
    chart: {
      height: 40,
      width: 40,
      type: "radialBar",
    },
    grid: {
      show: false,
      padding: {
        left: -30,
        right: -30,
        top: 0,
      },
    },
    series: [80],
    colors: [$warning],
    plotOptions: {
      radialBar: {
        hollow: {
          size: "30%",
        },
        dataLabels: {
          showOn: "always",
          name: {
            show: false,
          },
          value: {
            show: false,
          },
        },
      },
    },
    fill: {
      type: "gradient",
      gradient: {
        shade: "light",
        type: "horizontal",
        gradientToColors: [$warning],
        opacityFrom: 1,
        opacityTo: 0.8,
        stops: [0, 70, 100],
      },
    },
    stroke: {
      lineCap: "round",
    },
  };
  var radialWarningChart = new ApexCharts(
    document.querySelector("#radial-warning-chart"),
    radialWarningoptions
  );

  // radialWarningChart.render();

  // Radial-Danger-chart
  // --------------------------------
  var radialDangeroptions = {
    chart: {
      height: 40,
      width: 40,
      type: "radialBar",
    },
    grid: {
      show: false,
      padding: {
        left: -30,
        right: -30,
        top: 0,
      },
    },
    series: [50],
    colors: [$danger],
    plotOptions: {
      radialBar: {
        hollow: {
          size: "30%",
        },
        dataLabels: {
          showOn: "always",
          name: {
            show: false,
          },
          value: {
            show: false,
          },
        },
      },
    },
    fill: {
      type: "gradient",
      gradient: {
        shade: "light",
        type: "horizontal",
        gradientToColors: [$danger],
        opacityFrom: 1,
        opacityTo: 0.8,
        stops: [0, 70, 100],
      },
    },
    stroke: {
      lineCap: "round",
    },
  };
  var radialDangerChart = new ApexCharts(
    document.querySelector("#radial-danger-chart"),
    radialDangeroptions
  );

  // radialDangerChart.render();

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

  //treemap chart for source data
  //------------------------
  var entry_data = [];
  function entry() {
    var i, j;
    var y = 0;
    for (i = 0; i < project_data.source_labels.length; i++) {
      for (j = 0; j < 2; j++) {
        entry_data.push({
          x: project_data.source_labels[i],
          y:
            project_data.source_datasets[j]["label"] == "negative"
              ? 0 - parseInt(project_data.source_datasets[j]["data"][i])
              : project_data.source_datasets[j]["data"][i],
        });
      }
    }
  }
  entry();
  var treemapoptions = {
    series: [
      {
        data: entry_data,
      },
    ],
    legend: {
      show: false,
    },
    chart: {
      height: 350,
      type: "treemap",
    },

    dataLabels: {
      enabled: true,
      style: {
        fontSize: "26px",
      },
      formatter: function (text, op) {
        return [text, op.value];
      },
      offsetY: -4,
    },
    plotOptions: {
      treemap: {
        enableShades: false,
        shadeIntensity: 0.5,
        reverseNegativeShade: true,
        colorScale: {
          ranges: [
            {
              from: -1000000,
              to: 0,
              color: $negative,
            },
            {
              from: 0,
              to: 1000000,
              color: $positive,
            },
          ],
        },
      },
    },
  };

  var Treechart = new ApexCharts(
    document.querySelector("#treemap-chart"),
    treemapoptions
  );
  Treechart.render();

  //-----------

  //treemap chart for country based data
  //-------------------------
  var country_data = [];
  function country() {
    var i, j;
    var y = 0;
    for (i = 0; i < project_data?.country_labels?.length; i++) {
      for (j = 0; j < 2; j++) {
        country_data.push({
          x: project_data.country_labels[i],
          y:
            project_data.country_datasets[j]["label"] == "negative"
              ? 0 - parseInt(project_data.country_datasets[j]["data"][i])
              : project_data.country_datasets[j]["data"][i],
        });
      }
    }
  }
  country();
  var treemapGeooptions = {
    series: [
      {
        data: country_data,
      },
    ],
    legend: {
      show: false,
    },
    chart: {
      height: 350,
      type: "treemap",
    },

    dataLabels: {
      enabled: true,
      style: {
        fontSize: "26px",
      },
      formatter: function (text, op) {
        return [text, op.value];
      },
      offsetY: -4,
    },
    plotOptions: {
      treemap: {
        enableShades: false,
        shadeIntensity: 0.5,
        reverseNegativeShade: true,
        colorScale: {
          ranges: [
            {
              from: -1000000,
              to: 0,
              color: $negative,
            },
            {
              from: 0,
              to: 1000000,
              color: $positive,
            },
          ],
        },
      },
    },
  };

  var GeoTreechart = new ApexCharts(
    document.querySelector("#treemapGeo-chart"),
    treemapGeooptions
  );
  GeoTreechart.render();

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

  // Stacked Bar Negative Chart
  // ----------------------------------

  project_data.aspect_s_data[0]["data"].map(function (positive_data, i) {
    let $net_color;
    if (positive_data - project_data.aspect_s_data[1]["data"][i] < 0) {
      $net_color = $negative;
    } else {
      $net_color = $positive;
    }
    var donutChartOption = {
      chart: {
        width: 200,
        type: "donut",
      },
      dataLabels: {
        enabled: false,
      },
      series: [positive_data, project_data.aspect_s_data[1]["data"][i]],
      labels: ["Positive", "Negative"],
      stroke: {
        width: 0,
        lineCap: "round",
      },
      colors: [$positive, $negative],
      plotOptions: {
        pie: {
          donut: {
            size: "90%",
            labels: {
              show: true,
              name: {
                show: false,
                fontSize: "15px",
                color: $net_color,
                offsetY: 20,
                fontFamily: "IBM Plex Sans",
              },
              value: {
                show: true,
                fontSize: "48px",
                fontFamily: "Rubik",
                color: $net_color,

                offsetY: 9,
                formatter: function (val) {
                  return val;
                },
              },

              total: {
                show: true,
                label: "Net score",
                color: $net_color,
                formatter: function (w) {
                  return w.globals.seriesTotals.reduce(function () {
                    return (
                      positive_data - project_data.aspect_s_data[1]["data"][i]
                    );
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
    var donut_chart = new ApexCharts(
      document.querySelector(
        `#${project_data.aspect_s_labels[i]}-bar-negative-chart`
      ),
      donutChartOption
    );

    donut_chart.render();
  });
	
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
            horizontal: false,
            columnWidth: '55%'
          },
        },
        dataLabels: {
          enabled: true
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
			show: false
		  },
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

});
