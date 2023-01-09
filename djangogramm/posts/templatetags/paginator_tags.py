from django import template

register = template.Library()


@register.simple_tag
def get_page_range(paginator, current_page, on_each_side=1, on_ends=1):
    return paginator.get_elided_page_range(number=current_page, on_each_side=on_each_side, on_ends=on_ends)
