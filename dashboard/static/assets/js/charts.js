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
    datasets: project.sentiment_t_data
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

/* var aspect_t = new Chart(document.getElementById('aspect_t'), {
  type: 'bar',
  data: {
    labels: project.aspect_t_labels,
    datasets: project.aspect_t_data
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
 */




