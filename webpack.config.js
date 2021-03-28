const path = require('path');

module.exports = {
    mode: 'development',
    entry: './assets/js/project-details.js',
    output: {
        filename: 'bundle.js',
        path: path.resolve(__dirname, 'dashboard/static/assets/js'),
        publicPath: '/dist'
    },
    devServer:{
        contentBase: path.join(__dirname),
    }
};