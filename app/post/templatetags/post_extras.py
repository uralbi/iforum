from django import template
from django.contrib.auth import get_user_model
from django.utils.html import format_html as fhtml
from core.models import Post

register = template.Library()
user_model = get_user_model()


@register.inclusion_tag("post/post-list.html")
def recent_posts(post):
    posts = Post.objects.exclude(pk=post.pk)[:5]
    return {"title": "Recent Posts", "posts": posts}


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


@register.simple_tag
def row(extra_classes=''):
    return fhtml('<div class="row {}">', extra_classes)


@register.simple_tag
def endrow():
    return fhtml("</div>")


@register.simple_tag
def col(extra_classes=""):
    return fhtml('<div class="col {}">',
            extra_classes)

@register.simple_tag
def endcol():
    return fhtml("</div>")

@register.simple_tag(takes_context=True)
def author_details_tag(context):
    request = context["request"]
    current_user = request.user
    post = context["post"]
    author = post.author
    if author == current_user:
        return fhtml("<strong>ME</strong>")
    if author.first_name and author.last_name:
        name = f"{author.first_name} {author.last_name}"
    else:
        name = f"{author.username}"
    if author.email:
        prefix = fhtml('<a href="mailto:{}">', author.email)
        suffix = fhtml("</a>")
    else:
        prefix = ""
        suffix = ""
    return fhtml("{}{}{}", prefix, name, suffix)