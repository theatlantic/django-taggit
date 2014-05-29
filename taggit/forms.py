import os
from django import forms
from django.forms.util import flatatt
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.core.urlresolvers import reverse

from taggit.utils import parse_tags, edit_string_for_tags, clean_tag_string, transform_tags

class TagWidget(forms.TextInput):
    
    def render_values(self, tags, attrs):
        builder = []
        builder.append(u'<ul%s>' % flatatt(attrs))
        for tag_name in tags:
            tag_attr = {'tagValue': tag_name, 'value': tag_name}
            builder.append(u'<li%s>%s</li>' % (flatatt(tag_attr), tag_name))
        builder.append(u'</ul>')
        return ''.join(builder)
    
    def default_render(self, name, value, attrs):
        # Get the initial rendered box
        raw_value = value
        if value is not None and not isinstance(value, basestring):
            value = edit_string_for_tags(value)
        return super(TagWidget, self).render(name, value, attrs)

    def render(self, name, value, attrs=None):
        if attrs is None:
            attrs = {}

        # Get the original input field, which we will hide on render
        attrs.update({
            'class': 'taggit-tags',
            'data-ajax-url': reverse('taggit-ajax'),
            })
        rendered = self.default_render(name, value, attrs)


        # We need to get rid of the id if it's in attrs
        if 'id' in attrs:
            attrs['data-field-id'] = attrs.pop('id')

        tag_list = self.render_values(value or [], attrs)

        return mark_safe(rendered + tag_list)

    def _has_changed(self, initial, data):
        """
        Whether the input value has changed. Used for recording in
        django_admin_log.
        
        Because initial is passed as a queryset, and data is a string,
        we need to turn the former into a string and run the latter
        through a function which cleans it up and sorts the tags in it.
        """
        if initial is None:
            initial = ""
        elif hasattr(initial, 'select_related'):
            initial_vals = [o.tag for o in initial.select_related("tag")]
            initial = edit_string_for_tags(initial_vals)
        else:
            try:
                if not initial:
                    initial = ""
                else:
                    initial = edit_string_for_tags(initial)
            except TypeError, ValueError:
                initial = ""
        data = clean_tag_string(data)
        return super(TagWidget, self)._has_changed(initial, data)

    class Media:
        css = {'all': ('taggit/css/tagit-dark-grey.css',)}
        js = (
            'taggit/js/tagit.js',
            'taggit/js/taggit.js?v=1',
            )



class TagField(forms.CharField):
    widget = TagWidget

    def __init__(self, *args, **kwargs):
        self.transform_on_save  = kwargs.pop('transform_on_save', True)
        super(TagField, self).__init__(*args, **kwargs)

    def clean(self, value):
        # import debug
        value = super(TagField, self).clean(value)
        try:
            tags = parse_tags(value)
            if self.transform_on_save:
                tags = transform_tags(tags, delete_tags=False)
            return tags
        except ValueError:
            raise forms.ValidationError(_("Please provide a comma-separated list of tags."))

    def prepare_value(self, value):
        value = value or []
        if isinstance(value,  basestring):
            try:
                value = parse_tags(value)
            except ValueError:
                raise forms.ValidationError(_("Please provide a comma-separated list of tags."))
        else:
            value = [unicode(item.tag) for item in value]

        return super(TagField, self).prepare_value(value)
