import greeter = require('../greeter');
import $ = require('jquery');

$(() => {
  $(document.body).append(greeter("World"));
});