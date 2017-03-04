/**
 * Created by murphytalk on 2/26/2017.
 */
const filter_prefix = 'filter-';

function get_active_filter() {
    var name = $('#filters').find('.btn-success').attr('id').slice(7); //remove the leading filter_prefix
    return name;
}

/* Filter extra logic
   Extra logic is defined as an array of object {action, parameter}
   Extra action will be mapped to the following extra filter functions.
   All those functions share the same parameters:
    - position
    - parameters read from extra filter definition

   They either  return a new position : {capital, shares}
*/

//=== extra filter functions ======
function adjust_shares(position, parameters){
    /* parameters format : {instrument, adjustment}
    * */
    const instrument= position['instrument']['name'];
    const shares = position['shares'];
    const capital = position['capital'];
    if(parameters['instrument'] === instrument){
        const cost_per_share = capital / shares;
        const new_share =  shares+parameters['adjustment'];
        return  {shares: new_share, capital: new_share*cost_per_share};
    }
    else return null;
}
//==================================

/* Input is filter(one in the_filters) and position
 * If returned value <0 means this instrument is filtered by the filter
 * */
function apply_filter(filter, position) {
    const instrument_id = position['instrument']['id'];
    var shares = position['shares'];
    var capital = position['capital'];

    //if instruments not specified (null) meaning no instrument is being filtered
    if ((filter['instruments'] != null) && !(instrument_id in filter['instruments'])) {
        return {shares: -1};
    }

    if (filter['extra']) {
        var extras = JSON.parse(filter['extra']);
        $.each(extras,function(idx,extra) {
            var func = window[extra['action']];
            var new_position = func(position, extra['parameters']);
            if(new_position){
                shares = new_position['shares'];
                capital = new_position['capital'];
            }
        });
    }

    return {shares: shares, capital: capital};
}

function on_filter_btn_clicked(btn) {
    var filter_id = $(btn).attr('id');
    console.log(filter_id + ' clicked');
    $("#filters").children().removeClass('btn-success');
    $("#filters").children().addClass('btn-primary');
    $(btn).removeClass('btn-primary');
    $(btn).addClass('btn-success');
}

function populate_filters(filter_url, after_filters_loaded) {
    //All-filter is from filter template, now get the other filters
    $.getJSON(filter_url, function (filters) {
        //console.log(JSON.stringify(filters,null,4));
        var the_filters = {All: {instruments: null, extra: null}};
        //Populate filter buttons
        $.each(filters, function (i, v) {
            var filter_id = filter_prefix+ v['name'];
            $("#filters").append("<button type=\"button\" class=\"btn btn-primary\" id=\"" + filter_id + "\">" + v['name'] + "</button>");
            $('#' + filter_id).click(filter_btn_clicked);
            var instruments = null;
            if(v['instruments']) {
                instruments = {};
                $.each(v['instruments'], function (i2, v2) {
                    instruments[v2['id']] = v2['name'];
                });
            }
           the_filters[v['name']] = {instruments:instruments, extra: v['extra']};
        });
        after_filters_loaded(the_filters);
        //console.log());
    });
}

