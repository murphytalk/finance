const portfolio_prefix = 'portfolio-';

function get_active_portfolio() {
    var name = $('#portfolios').find('.btn-success').attr('id').slice(10); //remove the leading portfolio_prefix
    return name;
}

function get_active_portfolio_name() {
    return  $('#portfolios').find('.btn-success').text();
}
/* Input is portfolio and position
 * If returned value <0 means this instrument is portfolioed by the portfolio
 * */
function apply_portfolio(portfolio, position) {
    const instrument = position['instrument']['name'];
    var shares = position['shares'];
    var capital = position['capital'];

    //if there is a portfolio and the instrument is not in it ther filter it out
    if ( (portfolio != null) && !(instrument in portfolio)){
        return {shares: -1};
    }

    return {shares: shares, capital: capital};
}

function on_portfolio_btn_clicked(btn) {
    const portfolio_id = $(btn).attr('id');
    //console.log(portfolio_id + ' clicked');
    $("#portfolios").children().removeClass('btn-success');
    $("#portfolios").children().addClass('btn-primary');
    $(btn).removeClass('btn-primary');
    $(btn).addClass('btn-success');
}

function populate_portfolios(portfolio_url, after_portfolios_loaded) {
    //All-portfolio is from portfolio template, now get the other portfolios
    $.getJSON(portfolio_url, function (portfolios) {
        //console.log(JSON.stringify(portfolios,null,4));
        var the_portfolios = {All: null};
        //Populate portfolio buttons
        $.each(portfolios, function (i, v) {
            const normalized_portfolio_name = v['name'].replace(' ','_');
            const portfolio_id = portfolio_prefix + normalized_portfolio_name;
            $("#portfolios").append("<button type=\"button\" class=\"btn btn-primary\" id=\"" + portfolio_id + "\">" + v['name'] + "</button>");
            $('#' + portfolio_id).click(portfolio_btn_clicked);
            const portfolio_name = normalized_portfolio_name;
            the_portfolios[portfolio_name] = {};
            $.each(v['allocations'], function (i2, alloc){
                const instrument = alloc['instrument'];
                the_portfolios[portfolio_name][instrument] = alloc;
            });
        });
        after_portfolios_loaded(the_portfolios );
        //console.log(the_portfolios);
    });
}

function rebalance(){
    $(document).ready(function () {
        function populate_plan_data(table_id, plan_data){
            clear_table(table_id);
            const cols = ['instrument', 'delta_shares', 'current_allocation', 'target_allocation', 'deviation'];
            const num_cols = [1, 2, 3, 4];
            populate_data(
                table_id,
                function (d, callback, s){
                    callback({'data': obj_to_array(plan_data, cols)});
                },
                null,
                100,
                null,
                [
                    {
                        "render": function (data, type, row) {
                            //format_num(data);
                            return data.toFixed(2);
                        },
                        "targets": num_cols
                    },
                    {"className": "text-right", "targets": num_cols},
                ],
                null,
                {
                    bLengthChange: false,
                    paging: false,
                    searching: false,
                    info: false
                } 
            );
        }
        const portfolio_name = get_active_portfolio_name();
        const new_fund = 1000;
        var url = '/finance/api/report/rebalance_portfolio/'.concat(portfolio_name , '/', new_fund )
        $.getJSON(url,
            function (data) {
                const plans = data['plans'];
                const plan_ids = ['#plan1', '#plan2'];

                if(plans!=null){
                    $.each(plans, function (i,v){
                        if(v!=null){
                            populate_plan_data(plan_ids[i].concat('_tbl'), v);
                        }
                    });
                }
                else{
                    $.each(plans, function (i,v){ $(plan_ids[i]).hide();});
                }

                const merged = data['merged'];
                if(merged!=null){
                    populate_plan_data('#merged_plan_tbl', merged);
                    $('#merged_plan').show();
                }
                else{
                    $('#merged_plan').hide();
                }
                $("#rebalancing_popup").modal();
        });
    });
}
