'use strict';

var webpack = require('webpack');
var _ = require('lodash');
var fs = require("fs");
var path = require("path");
var BundleTracker = require('webpack-bundle-tracker');

var paths = {
    SOURCE: __dirname + "/assets/js",
    VENDOR: __dirname + "/assets/libs"
};

// Create an entrypoint for each .js file in /mains dir
var entryPoints = {};
fs.readdirSync(paths.SOURCE + "/mains").forEach(function(filename) {
    var stripped = filename.replace(/\.(js|jsx)$/, "");
    if (stripped !== filename) {
        entryPoints[stripped] = "mains/" + filename;
    }
});

module.exports = {
    context: paths.SOURCE,    // Path for resolving entry point modules
    entry: entryPoints,
    output: {
        path: path.resolve('bin/js/'),
        filename: 'main.[name].js'
    },
    devtool: "source-map",
    debug: true,
    module: {
        loaders: [
            // Make sure setupApp gets included in every entrypoint.
            {
                test: [
                    /mains\/.*\.js$/,
                    /Spec\.js$/
                ],
                loader: "imports?appSetupModule=setupApp.js"
            },
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                query: {
                    presets:['es2015', 'react']
                }
            }
        ],
        /*
         * Don't parse and minify already-minified vendor libs. This speeds up build time but could cause problems
         * if the lib itself tries to use a module system for its own dependencies (e.g. Backbone)
         */
        noParse: [new RegExp("^" + escapeRegExp(paths.VENDOR) + ".*\.min\.js$")]
    },
    resolve: {
        root: [paths.SOURCE, paths.VENDOR],
        modulesDirectories: ['node_modules', 'bower_components'],
        extensions: ['', '.js', '.jsx'],
        alias: {
            underscore: "lodash"
        }
    },

    // These values are assumed to be in the global scope on the page, so we don't need to bundle them
    externals: {
        "jquery": "jQuery",
        "bootstrap": "bootstrap"
    },
    plugins: [
        new BundleTracker({
            filename: './webpack-stats.json'
        }),
        new webpack.optimize.CommonsChunkPlugin({   // TODO: more granular commons chunking
            name: "common",
            filename: "common.js",
            minChunks: 3    // If at least 3 chunks require a module, put it in common.
        }),
        new webpack.IgnorePlugin(/^\.\/locale$/, /moment$/),
        new webpack.ProvidePlugin({
            $: "jquery",
            jQuery: "jquery",
            bootstrap: "bootstrap",
            _: "lodash"
        })
    ]
};


function escapeRegExp(str) {
    // from https://developer.mozilla.org/en-US/docs/Web/JavaScript/Guide/Regular_Expressions
    return str.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
}
