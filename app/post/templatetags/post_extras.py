from django import template
from django.contrib.auth import get_user_model
from django.utils.html import format_html as fhtml

register = template.Library()
user_model = get_user_model()


@register.filter
def author_details(author, current_user):
    if not isinstance(author, user_model):
        return ""
    if author == current_user:
        return fhtml('<strong>ME</strong>')
    if author.first_name and author.last_name:
        name = f"{author.first_name} {author.last_name}"
    else:
        name = f"{author.username}"
    if author.email:
        email = author.email
        prefix = fhtml('<a href="mailto:{}">', author.email)
        suffix = fhtml("</a>")
    else:
        prefix = ""
        suffix = ""
    return fhtml('{}{}{}', prefix, name, suffix)

