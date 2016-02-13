var _ = require("lodash");
var webpack = require("webpack");
var webpackDefaultConfig = require("./webpack.config.js");

module.exports = function(grunt) {

    grunt.initConfig({
        webpack: {
            development: webpackDefaultConfig,
            //production: require("./webpack.config-prod.js"),
            watch: _.defaults({
                watch: true,
                keepalive: true
            }, webpackDefaultConfig)
        },
        jasmine_webpack: {
            main: {
                options: {
                    specRunnerDest: '.grunt/grunt-jasmine-webpack/index.html',  // Put index file in same dir as other jasmine outputs
                    webpack: require("./webpack.config-test.js"),
                    keepRunner: true,
                    vendor: [
                        //'public/libs/jquery/jquery-1.11.3.js',
                        //'public/libs/lodash/3.10.0/lodash.js',
                        //'public/libs/backbone/backbone-1.1.2.js',
                        //'public/libs/bootstrap/dist/js/bootstrap.js'
                    ],
                    helpers: [
                        //'public/libs/jasmine-jquery/2.1.0/jasmine-jquery.js',
                        //'public/libs/jasmine-ajax/mock-ajax.js',
                        //'./test/js/helpers/pageContextHelper.js'
                    ]
                },
                src: './test/js/**/*Spec.js'
            }
        },
        less: {
            development: {
                options: {
                    paths: [
                        "assets/less"
                    ],
                    compile: true,
                    //compress: true,
                    //yuicompress: true,
                    optimization: 2
                },
                files: {
                    // target.css file: source.less file
                    "bin/css/site.css": "assets/less/site.less"
                }
            }
        },
        watch: {
            css: {
                files: '**/*.less',
                tasks: ['less']
            }
        },
        concurrent: {
            "dev-watcher": {
                tasks: ['watch:css', 'webpack:watch'],
                options: {
                    logConcurrentOutput: true
                }
            }
        }
    });

    grunt.loadNpmTasks('grunt-concurrent');
    grunt.loadNpmTasks('grunt-contrib-less');
    grunt.loadNpmTasks('grunt-contrib-watch');
    grunt.loadNpmTasks('grunt-jasmine-webpack');
    grunt.loadNpmTasks('grunt-webpack');

    grunt.registerTask('default', ['less', 'concurrent:dev-watcher']);
    grunt.registerTask('dev', ['less', 'webpack:development']);

    // Production build
    grunt.registerTask('prod', ['less', 'webpack:production']);

    grunt.registerTask('test', ['jasmine_webpack:main']);
};
