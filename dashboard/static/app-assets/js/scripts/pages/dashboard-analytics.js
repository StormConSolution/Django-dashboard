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
  var $white = "#fff";
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
		var len = arr.length, max = -Infinity;
		while (len--) {
			if (arr[len] > max) {
				max = arr[len];
			}
		}
		return max;
	}

	function min_label(arr) {
		var len = arr.length, min = Infinity;
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
      type: "bar",
      toolbar: {
        show: false,
      },
    },
    plotOptions: {
      bar: {
        horizontal: false,
        columnWidth: "20%",
        endingShape: "rounded",
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
          colors: $white,
        },
      },
    },
    yaxis: {
      min: min,
      max: max,
      tickAmount: 10,
	  range:10,
      forceNiceScale:true,
      labels: {
        style: {
          color: $white,
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

  // Success Line Chart
  // -----------------------------
  var successLineChartOption = {
    chart: {
      height: 100,
      type: "line",
      toolbar: {
        show: false,
      },
    },
    grid: {
      show: false,
      padding: {
        bottom: -20,
      },
    },
    colors: [$success],
    dataLabels: {
      enabled: false,
    },
    stroke: {
      width: 3,
      curve: "smooth",
    },
    series: [
      {
        data: [50, 0, 50, 40, 90, 0, 40, 25, 80, 40, 45],
      },
    ],
    xaxis: {
      show: false,
      labels: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
    yaxis: {
      show: false,
    },
  };

  var successLineChart = new ApexCharts(
    document.querySelector("#success-line-chart"),
    successLineChartOption
  );
  // successLineChart.render();

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
    for (i = 0; i < project_data.country_labels.length; i++) {
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

  // Primary Line Chart
  // -----------------------------
  var primaryLineChartOption = {
    chart: {
      height: 40,
      // width: 180,
      type: "line",
      toolbar: {
        show: false,
      },
      sparkline: {
        enabled: true,
      },
    },
    grid: {
      show: false,
      padding: {
        bottom: 5,
        top: 5,
        left: 10,
        right: 0,
      },
    },
    colors: [$primary],
    dataLabels: {
      enabled: false,
    },
    stroke: {
      width: 3,
      curve: "smooth",
    },
    series: [
      {
        data: [50, 100, 0, 60, 20, 30],
      },
    ],
    fill: {
      type: "gradient",
      gradient: {
        shade: "dark",
        type: "horizontal",
        gradientToColors: [$primary],
        opacityFrom: 0,
        opacityTo: 0.9,
        stops: [0, 30, 70, 100],
      },
    },
    xaxis: {
      show: false,
      labels: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
    yaxis: {
      show: false,
    },
  };

  var primaryLineChart = new ApexCharts(
    document.querySelector("#primary-line-chart"),
    primaryLineChartOption
  );
  // primaryLineChart.render();

  // Warning Line Chart
  // -----------------------------
  var warningLineChartOption = {
    chart: {
      height: 40,
      // width: 90,
      type: "line",
      toolbar: {
        show: false,
      },
      sparkline: {
        enabled: true,
      },
    },
    grid: {
      show: false,
      padding: {
        bottom: 5,
        top: 5,
        left: 10,
        right: 0,
      },
    },
    colors: [$warning],
    dataLabels: {
      enabled: false,
    },
    stroke: {
      width: 3,
      curve: "smooth",
    },
    series: [
      {
        data: [30, 60, 30, 80, 20, 70],
      },
    ],
    fill: {
      type: "gradient",
      gradient: {
        shade: "dark",
        type: "horizontal",
        gradientToColors: [$warning],
        opacityFrom: 0,
        opacityTo: 0.9,
        stops: [0, 30, 70, 100],
      },
    },
    xaxis: {
      show: false,
      labels: {
        show: false,
      },
      axisBorder: {
        show: false,
      },
    },
    yaxis: {
      show: false,
    },
  };

  var warningLineChart = new ApexCharts(
    document.querySelector("#warning-line-chart"),
    warningLineChartOption
  );
  // warningLineChart.render();

  // Profit Primary Chart
  // --------------------------------
  var profitPrimaryOptions = {
    chart: {
      height: 40,
      width: 40,
      type: "radialBar",
      sparkline: {
        show: true,
      },
    },
    grid: {
      show: false,
      padding: {
        left: -30,
        right: -30,
        top: 0,
        bottom: -70,
      },
    },
    series: [50],
    colors: [$primary],
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
    stroke: {
      lineCap: "round",
    },
  };
  var profitPrimaryChart = new ApexCharts(
    document.querySelector("#profit-primary-chart"),
    profitPrimaryOptions
  );

  // profitPrimaryChart.render();
});
