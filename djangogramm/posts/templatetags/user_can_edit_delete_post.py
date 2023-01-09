from django import template

register = template.Library()


@register.simple_tag
def user_can_edit_delete_post(post, user):
    return post.user_can_edit_post(user)
