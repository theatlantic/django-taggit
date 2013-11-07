(function($) {
    
    var taggitPrefix;
    
    var availableTags = [];
    function setup_autocomplete() {
        
        // We'll provide this as a data-attr using reverse
        taggitPrefix = $('input.taggit-tags').attr('data-ajax-url') || '/';

        console.log("setup setup_autocomplete")
        $.getJSON(taggitPrefix, {}, function(data) {
            availableTags.push.apply(availableTags, data.map(function(i) {
                return i.fields.name;
            }));
            $('.taggit-tags').tagit('updateAutoCompleteTags', availableTags);
        });
    }

    function get_contents_by_name(context, field_name) {
        var $form = $(context).parents('form').slice(0,1);
        var $field = $form.find('[name='+field_name +']');

        // Explicit check to CKEDITOR
        if($field[0].tagName === 'TEXTAREA' && 
               window.CKEDITOR !== undefined && 
               CKEDITOR.instances[$field.attr('id')] !== undefined) {
            return CKEDITOR.instances[$field.attr('id')].getData();
        }
        return $field.val();
    }

    function update_input(a, b) {
        // tagsChanged api is crappy; it doesn't return a consistent
        // element
        var tags = this.tags().map(function(t) {
            return '"' + t.value + '"';
        });
        var id = this.element.attr('data-field-id');
        // Update the input field
        $('#'+id).val(tags.join(','));
    }

    function setup_tagit_widgets() {
        $('ul.taggit-tags').tagit({
            tagSource: availableTags,
            triggerKeys: ['enter', 'comma', 'tab'],
            editable: true,
            tagsChanged: update_input
        });
        $('input.taggit-tags').hide();
    }

    function setup_generate_tags()  {
        var selector = 'button.taggit-tag-suggest';
        $(selector).live('click', function() {
            // Get content field to use and url to query
            var $ul = $(this).prev(),
                $input = $ul.prev(),
                query_url = taggitPrefix + 'generate-tags',
                content_field = $ul.attr('data-tag-content-field'),
                self = this,
                raw_tags = $input.val();
            
            // Merge form contents into a string of HTML.
            var raw_contents = content_field.split(',').map(function(cf) {
                return get_contents_by_name(self, cf); 
            }).join('.\n');
            // Wrap the whole thing in a div to ensure no free-floating text.
            raw_contents = ['<div>', raw_contents, '</div>'].join('');
            
            $.ajax({
                url: query_url,
                type: 'POST',
                dataType: 'jsonp',
                data: {'contents': raw_contents},
                success: function(new_tags) {
                    // Make sure to dedup the provided tags against the
                    // already given tags, normalizing as best we can.
                    for(var i = 0; i < new_tags.length; i++) {
                        var t = new_tags[i];
                        $ul.tagit('add', {label: t, value: t});
                    }
                },
                failure: function() {
                    $input.removeAttr('disabled'); 
                }
                
            });

        });
    }

    $(document).ready(function() {
        setup_autocomplete();
        setup_tagit_widgets();
        // setup_generate_tags();
    });

})((typeof window.django != 'undefined') ? django.jQuery : jQuery);
