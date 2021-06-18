from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
@stringfilter
def tooltip(msg):
    return mark_safe("""
    <a href="#" data-toggle="tooltip" data-placement="top" title="" data-original-title="{}">
      <i class="fe fe-help-circle"></i></a>
    """.format(msg))

