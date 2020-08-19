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
  'rgba(60, 180, 75, 0.5)',
  'rgba(230, 25, 75,0.5)',
  'rgba(67, 99, 216,0.5)',
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

var aspect_f = new Chart(document.getElementById('aspect_f'), {
  type: 'horizontalBar',
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

var sentiment_f = new Chart(document.getElementById('sentiment_f'), {
  type: 'pie',
  data: {
    labels: ['Positive', 'Negative', 'Neutral'],
    datasets: [{
      data: project.sentiment_f_data,
      backgroundColor: colours
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
var indexOfObject = 0 //iterating over objects is not determenistic, we need a separate index
for (const aspect in project.aspects) {
  data = []
  for (k in project.aspects[aspect]) {
    data.push({ x: new Date(project.aspects[aspect][k]['data__date_created']), y: project.aspects[aspect][k]["label__count"] })
  }
  
  aspect_t_data.push({
    label: aspect,
    data: data,
    backgroundColor:project.colors[indexOfObject%project.colors.length],
    borderColor:project.colors[indexOfObject%project.colors.length],
    fill: false,
  })
  indexOfObject+=1
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
          unit: 'day'
        }
      }],
      yAxes: [{
        ticks: {
          beginAtZero: true
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
    data: project.emotional_entity_data, 
    dataLabels: {
      enabled: false,
      style: {
        fontWeight: 'bold',
        textOutline: ''
      }
    }
  }],
})
