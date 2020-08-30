// https://stackoverflow.com/questions/57446821/accumulating-a-map-from-an-array-in-typescript
export function fromEntries<V>(iterable: Iterable<[string, V]>) {
    return [...iterable].reduce((obj, [key, val]) => {
      obj[key] = val;
      return obj;
    }, {} as {[k: string]: V});
}

// for ag-grid
export function currencyFormatter(params) {
    return  formatNumber(params.value);
}

export function formatNumber(num) {
    return num == null ? '' : num.toFixed(2).replace(/\B(?=(\d{3})+(?!\d))/g, ',');
    /*
    return Math.floor(num)
      .toString()
      .replace(/(\d)(?=(\d{3})+(?!\d))/g, '$1,');
    */
}
