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

// https://echarts.apache.org/en/option.html#legend.data
export interface ChartLegend {
    name: string;
    icon?: string;
    textStyle?: any;
}
export interface ChartData {
    name: string;
    value: number;
}

export function pieChartOption(
                    title: any, // https://echarts.apache.org/en/option.html#title
                    legend: ChartLegend,
                    data: ChartData[]){
    const sum = data.map ( x => x.value).reduce( (acc, cur) => acc + cur, 0);
    function tooltipFormatter(params: any, ticket: string, callback: (ticket: string, html: string) => string){
        // console.log('chart param', params);
        return `Market Value : \u00a5${formatNumber(params.data.value)} (${(params.data.value * 100 / sum).toFixed(2)}%)`;
    }
    return {
        title,
        tooltip: {
            trigger: 'item',
            // https://echarts.apache.org/en/option.html#tooltip.formatter
            formatter: tooltipFormatter,
        },
        legend: {
            type: 'scroll',
            orient: 'vertical',
            right: 10,
            top: 20,
            bottom: 20,
            data: legend
            //selected: data.selected
        },
        series: [
            {
                // name: '姓名',
                type: 'pie',
                radius: '55%',
                center: ['40%', '50%'],
                data,
                emphasis: {
                    itemStyle: {
                        shadowBlur: 10,
                        shadowOffsetX: 0,
                        shadowColor: 'rgba(0, 0, 0, 0.5)'
                    }
                }
            }
        ]
    };
}
