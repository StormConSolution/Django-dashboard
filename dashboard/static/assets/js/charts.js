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

var colours = [
  'rgba(255, 99, 132, 0.2)',
  'rgba(54, 162, 235, 0.2)',
  'rgba(255, 206, 86, 0.2)',
  'rgba(75, 192, 192, 0.2)',
  'rgba(153, 102, 255, 0.2)',
  'rgba(255, 159, 64, 0.2)'
];

var sentimentSourceChart = new Chart(document.getElementById('sentiment_source').getContext('2d'), {
  type: 'bar',
  data: {
    labels: project.source_labels,
    datasets: project.source_datasets
  },
  options: {
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
});

var barChart = new Chart(document.getElementById('aspect_f'), {
  type: 'bar',
  data: {
    labels: ['Aspects'],
    datasets: project.aspect_f_data
  },
  options: {
    responsive: true,
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
});

var pieChart = new Chart(document.getElementById('sentiment_f'), {
  type: 'pie',
  data: {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [{
      data: project.sentiment_f_data,
      backgroundColor: colours.slice(3)
    }]
  },
  options: {
    responsive: true
  }
});

var aspect_s = new Chart(document.getElementById('aspect_s'), {
  type: 'bar',
  data: {
    labels: project.aspect_s_labels, // labes could be ether [p,n,n] or individual aspects , for now individual aspects , but later we could implement a switch
    datasets: project.aspect_s_data
  },
  options: {
    responsive: true,
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
});

var sentiment_t = new Chart(document.getElementById('sentiment_t'), {
  type: 'line',
  data: {
    labels: project.sentiment_t_labels,
    datasets: project.sentiment_t_data,
    
  },
  options: {
    responsive: true,
    scales: {
      yAxes: [{
        ticks: {
          beginAtZero: true
        }
      }]
    }
  }
});


aspect_t_data = []
for (const aspect in project.aspects) {
  data = []
  for (k in project.aspects[aspect]) {
    data.push({ x: new Date(project.aspects[aspect][k]['data__date_created']), y: project.aspects[aspect][k]["label__count"] })
  }
  aspect_t_data.push({
    label: aspect,
    data: data,
    fill:false,
  })
}

var aspect_t = new Chart(document.getElementById('aspect_t'), {
  type: 'line',
  data: {
    datasets: aspect_t_data
  },
  options: {
    responsive: true,
    scales: {
      xAxes: [{
        type: 'time',
        time: {
          unit: 'month'
        }
      }]
    }
  }
});

Highcharts.chart('emotion-map', {

  chart: {
    type: 'heatmap',
    marginTop: 40,
    marginBottom: 140,
    plotBorderWidth: 1
  },

  title: {
    text: 'Emotion expressed by entity'
  },

  xAxis: {
    categories: project.entities_for_emotions
  },

  yAxis: {
    categories: project.emotions,
    title: null,
    reversed: true
  },

  colorAxis: {
    min: 0,
    minColor: '#FFFFFF',
    maxColor: Highcharts.getOptions().colors[0]
  },

  legend: {
    align: 'right',
    layout: 'vertical',
    margin: 0,
    verticalAlign: 'top',
    y: 25,
    symbolHeight: 280
  },

  tooltip: {
    formatter: function () {
      return '<b>' + this.point.value + '</b>';
    }
  },

  series: [{
    name: 'Mentions',
    data: [[0, 0, 10], [0, 1, 19], [0, 2, 8], [0, 3, 24], [0, 4, 67], [1, 0, 92], [1, 1, 58], [1, 2, 78], [1, 3, 117], [1, 4, 48], [2, 0, 35], [2, 1, 15], [2, 2, 123], [2, 3, 64], [2, 4, 52], [3, 0, 72], [3, 1, 132], [3, 2, 114], [3, 3, 19], [3, 4, 16], [4, 0, 38], [4, 1, 5], [4, 2, 8], [4, 3, 117], [4, 4, 115], [5, 0, 88], [5, 1, 32], [5, 2, 12], [5, 3, 6], [5, 4, 120], [6, 0, 13], [6, 1, 44], [6, 2, 88], [6, 3, 98], [6, 4, 96], [7, 0, 31], [7, 1, 1], [7, 2, 82], [7, 3, 32], [7, 4, 30], [8, 0, 85], [8, 1, 97], [8, 2, 123], [8, 3, 64], [8, 4, 84], [9, 0, 47], [9, 1, 114], [9, 2, 31], [9, 3, 48], [9, 4, 91]],
    dataLabels: {
      enabled: false,
      style: {
        fontWeight: 'bold',
        textOutline: ''
      }
    }
  }],
}
)