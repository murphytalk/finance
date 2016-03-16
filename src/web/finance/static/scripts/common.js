function getTablePageLenItemName(selector){
    const storagePageLen = "pageLen";
    return selector.substring(1)+"_"+storagePageLen;
}

function getDataTablePageLength(selector){
    if (typeof(Storage) !== "undefined") {
        // Retrieve
        return localStorage.getItem(getTablePageLenItemName(selector));
    } else {
        console.log("Browser does not support HTML5.")
        return null;
    }
}

function setDataTablePageLength(selector,len){
    if (typeof(Storage) !== "undefined") {
        // Store
        localStorage.setItem(getTablePageLenItemName(selector), len);
    } else {
        console.log("Browser does not support HTML5.")
    }
}


function clear_table(table_selector) {
    if ($.fn.dataTable.isDataTable(table_selector)) {
        table = $(table_selector).DataTable();
        table.destroy();
        $(table_selector+' tbody').remove();
    }
}

function build_header(table_selector,headers) {
    var head = $("<thead>").append();
    var tr = $("<tr>");
    clear_table();
    $.each(headers, function (idx, h) {
        tr.append($("<th>").append(h));
    });
    head.append(tr);
    $(table_selector+" thead").replaceWith(head);
};

 function populate_data(table_selector,url,col_order,row_per_page,lengthMenu,colDefs) {
    var lenMenu;
    if(lengthMenu==null){
        lenMenu = [10, 25, 50, 100];
    }
    else lenMenu = lengthMenu;

    var pageLen =  getDataTablePageLength(table_selector);
    console.log("pageLen retrieved : "+pageLen);
    if(pageLen == null){
         pageLen = row_per_page;
    }

    var parameter = {
        'ajax': url,
        "order": col_order,
        'pageLength': pageLen,
        'lengthMenu': lenMenu
    };

    if(colDefs != null){
        parameter['columnDefs'] = colDefs;
    }


    $(table_selector).DataTable(parameter);
    $(table_selector).on( 'length.dt', function ( e, settings, len ) {
        console.log( 'New page length: '+len );
        setDataTablePageLength(table_selector,len);
    });
};

function selectDataTableRow(table_selector, rowSelector){
    var table = $(table_selector).DataTable();
    table.row(rowSelector).addClass('selected');
}

function table_row_selection(table_selector, editTableCallback){
    var table = $(table_selector).DataTable();
    $(table_selector+' tbody').on( 'click', 'tr', function () {
        if ( $(this).hasClass('selected') ) {
            $(this).removeClass('selected');
        }
        else {
            table.$('tr.selected').removeClass('selected');
            $(this).addClass('selected');
        }
        editTableCallback(table_selector);
    });
}
