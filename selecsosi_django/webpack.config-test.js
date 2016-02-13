"use strict";

var _ = require("lodash");
var webpack = require("webpack");

var defaultConfig = require("./webpack.config.js");

var testConfig = {
    context: __dirname
};

_.defaultsDeep(testConfig, defaultConfig);

delete testConfig['output'];
delete testConfig['entry'];

testConfig.plugins = _.filter(testConfig.plugins, function(plugin) {
    return !(plugin instanceof webpack.optimize.CommonsChunkPlugin);
});

module.exports = testConfig;
