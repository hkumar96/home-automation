$(function() {
    var plot = [];
  $.getJSON("home_data.php",function(data){
    var power = data.power;
    // alert(power);
    for (var i = 0; i < power.length; i++) {
      var obj = {t:i+":00",value:power[i]};
      plot.push(obj);
    }
      Morris.Area({
          element: 'morris-area-chart',
          data: plot,
          xkey: 't',
          ykeys: ['value'],
          labels: ['Power'],
          pointSize: 2,
          hideHover: 'auto',
          resize: true
      });

  });

});
