var initDjangoHStoreWidget = function(hstore_field_name, inline_prefix) {
    // ignore inline templates
    // if hstore_field_name contains "__prefix__"
    if(hstore_field_name.indexOf('__prefix__') > -1){
        return;
    }

    var $ = django.jQuery;

    // processing inlines
    if(hstore_field_name.indexOf('inline') > -1){
        var inlineClass = $('#id_'+hstore_field_name).parents('.inline-related, .grp-group').attr('class');
        // if using TabularInlines stop here
        // TabularInlines not supported
        if (inlineClass.indexOf('tabular') > -1) {
            return;
        }
    }

    // reusable function that retrieves a template even if ID is not correct
    // (written to support inlines)
    var retrieveTemplate = function(template_name, field_name){
        var specific_template = $('#'+template_name+'-'+field_name);
        // if found specific template return that
        if(specific_template.length){
            return specific_template.html();
        }
        else{
            // get fallback template
            var html = $('.'+template_name+'-inline').html();
            // replace all occurrences of __prefix__ with field_name
            // and return
            html = html.replace(/__prefix__/g, inline_prefix);
            return html;
        }
    }

    // reusable function that compiles the UI
    var compileUI = function(params){
        var hstore_field_id = 'id_'+hstore_field_name,
            original_textarea = $('#'+hstore_field_id),
            original_value = original_textarea.val(),
            original_container = original_textarea.parents('.form-row, .grp-row').eq(0),
            errorHtml = original_container.find('.errorlist').html(),
            json_data = {};

        if(original_value !== ''){
            // manage case in which textarea is blank
            try{
                json_data = JSON.parse(original_value);
            }
            catch(e){
                alert('invalid JSON:\n'+e);
                return false;
            }
        }

        var hstore_field_data = {
                "id": hstore_field_id,
                "label": original_container.find('label').text(),
                "name": hstore_field_name,
                "value": original_textarea.val(),
                "help": original_container.find('.grp-help, .help').text(),
                "errors": errorHtml,
                "data": json_data
            },
            // compile template
            ui_html = retrieveTemplate('hstore-ui-template', hstore_field_name),
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
    var row_html = retrieveTemplate('hstore-row-template', hstore_field_name),
        empty_row = _.template(row_html, { 'key': '', 'value': '' }),
        $hstore = $('#id_'+hstore_field_name).parents('.hstore');

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
        $(this).parents('.form-row, .grp-row').eq(0).remove();
        updateTextarea($hstore);
    });

    // add row link
    $hstore.delegate('a.hs-add-row, .hs-add-row a', 'click', function(e) {
        e.preventDefault();
        $hstore.find('.hstore-rows').append(empty_row);
    });

    // toggle textarea link
    $hstore.delegate('.hstore-toggle-txtarea', 'click', function(e) {
        e.preventDefault();

        var raw_textarea = $hstore.find('.hstore-textarea'),
            hstore_rows = $hstore.find('.hstore-rows'),
            add_row = $hstore.find('.hs-add-row');

        if(raw_textarea.is(':visible')) {

            var compiled_ui = compileUI();

            // in case of JSON error
            if(compiled_ui === false){
                return;
            }

            // jquery < 1.8
            try{
                var $ui = $(compiled_ui);
            }
            // jquery >= 1.8
            catch(e){
                var $ui = $($.parseHTML(compiled_ui));
            }

            // update rows with only relevant content
            hstore_rows.html($ui.find('.hstore-rows').html());

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

    // update textarea whenever a field changes
    $hstore.delegate('input[type=text]', 'keyup', function() {
        updateTextarea($hstore);
    });
};

django.jQuery(window).load(function() {
    // support inlines
    // bind only once
    if(django.hstoreWidgetBoundInlines === undefined){
        var $ = django.jQuery;
        $('.grp-group .grp-add-handler, .inline-group .hs-add-row a, .inline-group .add-row').click(function(e){
            var hstore_original_textareas = $(this).parents('.grp-group, .inline-group').eq(0).find('.hstore-original-textarea');
            // if module contains .hstore-original-textarea
            if(hstore_original_textareas.length > 0){
                // loop over each inline
                $(this).parents('.grp-group, .inline-group').find('.grp-items div.grp-dynamic-form, .inline-related').each(function(e, i){
                    var prefix = i;
                    // loop each textarea
                    $(this).find('.hstore-original-textarea').each(function(e, i){
                        // cache field name
                        var field_name = $(this).attr('name');
                        // ignore templates
                        // if name attribute contains __prefix__
                        if(field_name.indexOf('prefix') > -1){
                            // skip to next
                            return;
                        }
                        initDjangoHStoreWidget(field_name, prefix);
                    });
                });
            }
        });
        django.hstoreWidgetBoundInlines = true;
    }
});
