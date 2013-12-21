var initDjangoHStoreWidget = function(hstore_field_name) {

    $ = django.jQuery;
    
    // reusable function that compiles the UI
    var compileUI = function(params){
        var hstore_field_id = 'id_'+hstore_field_name,
            original_textarea = $('#'+hstore_field_id),
            original_container = original_textarea.parents('.form-row, .grp-row'),
            json_data = JSON.parse(original_textarea.val()),
            hstore_field_data = {
                'id': hstore_field_id,
                'label': original_container.find('label').text(),
                'name': hstore_field_name,
                'value': original_textarea.val(),
                'help': original_container.find('.grp-help, .help').text(),
                'data': json_data
            },
            // compile template
            ui_html = $('#hstore-ui-template').html(),
            compiled_ui_html = _.template(ui_html, hstore_field_data);
        
        // this is just to DRY up a bit
        if(params && params.replace_original === true){
            // remove original textarea to avoid having two textareas with same ID
            original_textarea.remove();
            // inject compiled template and hide original
            original_container.after(compiled_ui_html).hide();
        }
        
        return compiled_ui_html;
    };
    
    // generate UI
    compileUI({ replace_original: true });
    
    // cache other objects that we'll reuse
    var row_html = $('#hstore-row-template').html(),
        empty_row = _.template(row_html, { 'key': '', 'value': '' }),
        $hstore = $('.hstore');
    
    // reusable function that updates the textarea value
    var updateTextarea = function(container) {
        // init empty json object
        var new_value = {},
            raw_textarea = container.find('textarea'),
            rows = container.find('.form-row, .grp-row');
    
        // loop over each object and populate json
        rows.each(function() {
            var inputs = $(this).find('input'),
                key = inputs.eq(0).val(),
                value = inputs.eq(1).val();
            new_value[key] = value;
        });
    
        // update textarea value
        $(raw_textarea).val(JSON.stringify(new_value, null, 4));
    };
    
    // remove row link
    $hstore.delegate('a.remove-row', 'click', function(e) {
        e.preventDefault();
        // cache container jquery object before $(this) gets removed
        var container = $(this).parents('.hstore');
        $(this).parents('.form-row, .grp-row').remove();
        updateTextarea(container);
    });
    
    // add row link
    $hstore.delegate('.add-row', 'click', function(e) {
        e.preventDefault();
        $(this).parents('.hstore').find('.hstore-rows').append(empty_row);
    });
    
    // toggle textarea link
    $hstore.delegate('.hstore-toggle-txtarea', 'click', function(e) {
        e.preventDefault();
        
        var container = $(this).parents('.hstore'),
            raw_textarea = container.find('.hstore-textarea'),
            hstore_rows = container.find('.hstore-rows'),
            add_row = container.find('.add-row');
        
        if(raw_textarea.is(':visible')) {
            try{
                // update rows
                hstore_rows.html(
                    $(compileUI()).find('.hstore-rows').html()
                );
            }
            catch(e){
                alert('invalid JSON:\n'+e);
                return;
            }
            raw_textarea.hide();
            hstore_rows.show();
            add_row.show();
        }
        else{
            raw_textarea.show();
            hstore_rows.hide();
            add_row.hide();
        }
    });
    
    window.compileUI = compileUI;
    
    // update textarea whenever a field changes
    $hstore.delegate('input[type=text]', 'keyup', function() {
        updateTextarea($(this).parents('.hstore'));
    });
};