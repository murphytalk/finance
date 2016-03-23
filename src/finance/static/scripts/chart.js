Highcharts.setOptions({
    lang: {
        thousandsSep : ','
    }
});

function pieChartOptions(title, name, data, tooltip_show_percent){
    var fmt;
    if(tooltip_show_percent){
        fmt = '{point.percentage:.1f}%';
    }
    else{
        fmt = '{point.y:,.1f}';
    }

    var chart_title;
    if(name !=null && title !=null) {
        chart_title =  name + '<br>' + title;
    }
    else{
        chart_title = '';
    }

    return {
       chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie'
       },
       tooltip: {
            pointFormat: '{series.name}: <b>'+fmt+'</b>'
       },
       title: {
            text: chart_title
       },
       plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                    style: {
                        color: (Highcharts.theme && Highcharts.theme.contrastTextColor) || 'black'
                    }
                }
            }
        },
       series: [{
            name: name,
            colorByPoint: true,
            data: data
       }]
    };
}
