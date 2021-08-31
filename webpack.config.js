const path = require('path');
const webpack = require("webpack");

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
    module: {
        rules: [{
            test: /\.(jsx)$/,
            exclude: path.resolve(__dirname, "node_modules"),
            use: ['babel-loader']
        }]
    },
    output: {
        libraryTarget: "umd",
        filename: '[name].js',
        path: path.resolve(__dirname, 'dashboard/static/assets/js'),
    },
    devServer:{
        contentBase: path.join(__dirname),
    },
    resolve: {
        extensions: ['.js', '.jsx'],
    },
    externals: {
        react: {
            root: 'React',
            commonjs2: 'react',
            commonjs: 'react',
            amd: 'React'
        },
        'react-dom': {
            root: 'ReactDOM',
            commonjs2: 'react-dom',
            commonjs: 'react-dom',
            amd: 'ReactDOM'
        },

    },
    externalsPresets: {
        node: true,
    },
};