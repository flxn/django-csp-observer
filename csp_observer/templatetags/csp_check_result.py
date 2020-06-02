from django import template

register = template.Library()

@register.inclusion_tag('result_tag.html', takes_context=True)
def csp_check_result(context):
    request = context['request']
    return {
        'request': request
    }