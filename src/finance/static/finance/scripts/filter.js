/**
 * Created by murphytalk on 2/26/2017.
 */
const filter_prefix = 'filter-';

function get_active_filter() {
    var name = $('#filters').find('.btn-success').attr('id').slice(7); //remove the leading filter_prefix
    return name;
}

/* Input is filter(one in the_filters), instrument id and shares.
 *  If returned value <0 means this instrument is filtered by the filter
 * */
function apply_filter(filter, instrument_id, shares) {
    if ((filter['instruments'] != null) && !(instrument_id in filter['instruments'])) {
        return -1;
    }

    if (filter['extra']) {
        //todo: apply extra
        return shares;
    }
    else return shares;
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
            var instruments = {};
            $.each(v['instruments'], function (i2, v2) {
                instruments[v2['id']] = v2['name'];
            });
            the_filters[v['name']] = {instruments:instruments, extra: v['extra']};
        });
        after_filters_loaded(the_filters);
        //console.log());
    });
}

