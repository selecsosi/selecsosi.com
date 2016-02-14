import React from 'react';
import ReactDOM from 'react-dom';
import App from '../app.jsx';
import $ from "jquery"

var hello = $("<div>");
var timer =  $("<div>");
$("#react-app").append(hello).append(timer);
ReactDOM.render(<App.App/>, hello[0]);
ReactDOM.render(<App.Timer/>, timer[0]);
