const path = require('path');

module.exports = {
    mode: 'development',
    entry: {
        'project-details':'./assets/js/project-details.js',
        'dashboard':'./assets/js/dashboard.js',
        'dashboard-guest':'./assets/js/dashboard-guest.js',
        'sentiment':'./assets/js/sentiment.js',
        'aspect':'./assets/js/aspect.js',
        'aspect-guest':'./assets/js/aspect-guest.js',
        'entity':'./assets/js/entity.js',
        'entity-guest':'./assets/js/entity-guest.js',
        'sentiment-guest':'./assets/js/sentiment-guest.js',
        'alerts':'./assets/js/alerts.js',
        'alerts-guest':'./assets/js/alerts-guest.js',
    },
    output: {
        filename: '[name].js',
        path: path.resolve(__dirname, 'dashboard/static/assets/js'),
        publicPath: '/dist'
    },
    devServer:{
        contentBase: path.join(__dirname),
    }
};