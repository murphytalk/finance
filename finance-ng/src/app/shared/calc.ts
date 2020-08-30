import * as Highcharts from 'highcharts/highstock';

// https://stackoverflow.com/questions/57446821/accumulating-a-map-from-an-array-in-typescript
export function fromEntries<V>(iterable: Iterable<[string, V]>) {
    return [...iterable].reduce((obj, [key, val]) => {
        obj[key] = val;
        return obj;
    }, {} as { [k: string]: V });
}

export function formatNumber(num) {
    return num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    /*
    return Math.floor(num)
      .toString()
      .replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
    */
}

export function currencySign(ccy: string) {
    switch (ccy.toUpperCase()) {
        case 'USD':
            return '$';
        case 'JPY':
            return '\u00a5';
        case 'CNY':
            return 'C\u00a5';
        case 'HKD':
            return 'HK$';
        default:
            return '';
    }
}

export function pieChartOptions(
    title: string,
    name: string,
    data,
    tooltipShowPercent: boolean
) {
    let fmt;
    if (tooltipShowPercent) {
        fmt = '{point.percentage:.1f}%';
    } else {
        fmt = '{point.y:,.1f}';
    }

    let chartTitle;
    if (name != null && title != null) {
        chartTitle = name + '<br>' + title;
    } else {
        chartTitle = '';
    }

    return {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie',
        },
        tooltip: {
            pointFormat: '{series.name}: <b>' + fmt + '</b>',
        },
        title: {
            text: chartTitle,
        },
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '<b>{point.name}</b>: {point.percentage:.1f} %',
                    /*
                    style: {
                        color:
                            (Highcharts.theme &&
                                Highcharts.theme.contrastTextColor) ||
                            'black',
                    },
                    */
                },
            },
        },
        series: [
            {
                name,
                colorByPoint: true,
                data,
            },
        ],
    };
}
