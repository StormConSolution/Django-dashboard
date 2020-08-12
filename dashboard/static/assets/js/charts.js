/* eslint-disable object-curly-newline */

/* global Chart */

/**
 * --------------------------------------------------------------------------
 * CoreUI Boostrap Admin Template (v3.2.0): main.js
 * Licensed under MIT (https://coreui.io/license)
 * --------------------------------------------------------------------------
 */

/* eslint-disable no-magic-numbers */
// random Numbers
var random = function random() {
  return Math.round(Math.random() * 100);
}; // eslint-disable-next-line no-unused-vars

// Aliasing the variable that is declared in the template.
var project = project_data;

aspects = {}

for (datapoint in project.data) {
  for (const [key, value] of Object.entries(project.data[datapoint]['aspects'])) {
    aspects[key] = (typeof aspects[key] === 'undefined') ? value.length : aspects[key] + value.length;
  }
}
//Status:ok is in every aspect and should be removed
delete aspects['status']

var max = 0
var datasets = []
for (const [key, value] of Object.entries(aspects)) {
  if (value > max) {
    max = value
  }
  datasets.push({
    label: key,
    backgroundColor: 'rgba(151, 187, 205, 0.5)',
    borderColor: 'rgba(151, 187, 205, 0.8)',
    highlightFill: 'rgba(151, 187, 205, 0.75)',
    highlightStroke: 'rgba(151, 187, 205, 1)',
    data: [value]
  })
}


var barChart = new Chart(document.getElementById('aspect_f'), {
  type: 'bar',
  data: {
    labels: ['Aspects'],
    datasets: datasets
  },
  options: {
    responsive: true,
    scales: {
      yAxes: [{
        display: true,
        ticks: {
          suggestedMin: 0,    // minimum will be 0, unless there is a lower value.
          suggestedMax: Math.floor(max * (120 / 100)) //tallest bar is always about 20% below the top of the chart
        }
      }]
    }
  }
}); // eslint-disable-next-line no-unused-vars

var sentiment = [0, 0, 0]

for (datapoint in project.data) {
  if (project.data[datapoint]['sentiment'] > 0) {
    sentiment[0]++;

  } else if (project.data[datapoint]['sentiment'] < 0) {
    sentiment[1]++;

  } else {
    sentiment[2]++
  }
}

var pieChart = new Chart(document.getElementById('sentiment_f'), {
  type: 'pie',
  data: {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [{
      data: sentiment,
      backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56'],
      hoverBackgroundColor: ['#FF6384', '#36A2EB', '#FFCE56']
    }]
  },
  options: {
    responsive: true
  }
}); // eslint-disable-next-line no-unused-vars

var mainChart = new Chart(document.getElementById('sentiment_t'), {
  type: 'line',
  data: {
    labels: ['M', 'T', 'W', 'T', 'F', 'S', 'S', 'M', 'T', 'W', 'T', 'F', 'S', 'S', 'M', 'T', 'W', 'T', 'F', 'S', 'S', 'M', 'T', 'W', 'T', 'F', 'S', 'S'],
    datasets: [{
      label: 'My First dataset',
      backgroundColor: coreui.Utils.hexToRgba(coreui.Utils.getStyle('--info'), 10),
      borderColor: coreui.Utils.getStyle('--info'),
      pointHoverBackgroundColor: '#fff',
      borderWidth: 2,
      data: [165, 180, 70, 69, 77, 57, 125, 165, 172, 91, 173, 138, 155, 89, 50, 161, 65, 163, 160, 103, 114, 185, 125, 196, 183, 64, 137, 95, 112, 175]
    }, {
      label: 'My Second dataset',
      backgroundColor: 'transparent',
      borderColor: coreui.Utils.getStyle('--success'),
      pointHoverBackgroundColor: '#fff',
      borderWidth: 2,
      data: [92, 97, 80, 100, 86, 97, 83, 98, 87, 98, 93, 83, 87, 98, 96, 84, 91, 97, 88, 86, 94, 86, 95, 91, 98, 91, 92, 80, 83, 82]
    }, {
      label: 'My Third dataset',
      backgroundColor: 'transparent',
      borderColor: coreui.Utils.getStyle('--danger'),
      pointHoverBackgroundColor: '#fff',
      borderWidth: 1,
      borderDash: [8, 5],
      data: [65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65, 65]
    }]
  },
  options: {
    maintainAspectRatio: false,
    legend: {
      display: false
    },
    scales: {
      xAxes: [{
        gridLines: {
          drawOnChartArea: false
        }
      }],
      yAxes: [{
        ticks: {
          beginAtZero: true,
          maxTicksLimit: 5,
          stepSize: Math.ceil(250 / 5),
          max: 250
        }
      }]
    },
    elements: {
      point: {
        radius: 0,
        hitRadius: 10,
        hoverRadius: 4,
        hoverBorderWidth: 3
      }
    }
  }
});

var sentimentSourceChart = new Chart(document.getElementById('sentiment_source'), {
    type: 'bar',
    data: {
	labels: project_data.source_labels,
	datasets: project_data.source_datasets
    }
});

//# sourceMappingURL=charts.js.map
