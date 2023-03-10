from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.contenttypes.models import ContentType
from post.forms import CommentForm
from core.models import Post, Tag, Gallery


def post_detail(request, pk):
    post = Post.objects.prefetch_related('images', 'tags').get(pk=pk)
    if request.user.is_active:
        if request.method == "POST":
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.content_object = post
                comment.creator = request.user
                comment.save()
                return redirect(request.path_info)
        else:
            comment_form = CommentForm()
    else:
        comment_form = None

    return render(request, "post/post-detail.html",
                  {"post": post, "comment_form": comment_form})


def index(request):
    posts = Post.objects.filter(published_at__isnull = False).order_by(
        '-published_at').prefetch_related(
        'images').prefetch_related('tags').all()

    content_type_id = ContentType.objects.get_for_model(posts.first()).id
    return render(request, "post/index.html", {'posts': posts, 'content_type_id': content_type_id})
