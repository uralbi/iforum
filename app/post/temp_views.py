from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.contrib.contenttypes.models import ContentType
from comment.forms import CommentForm
from core.models import Post, Tag, Gallery
import logging

logger = logging.getLogger(__name__)


def post_detail(request, pk):
    post = Post.objects.select_related(
        "author").prefetch_related(
        'images', 'tags').get(pk=pk)
    logger.debug('God %d post', post.id)
    if request.user.is_active:
        if request.method == "POST":
            comment_form = CommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.content_object = post
                comment.creator = request.user
                comment.save()
                logger.info('Created comment on Post %d for user %s', post.id,
                            request.user)
                return redirect(request.path_info)
        else:
            comment_form = CommentForm()
    else:
        comment_form = None
    return render(request, "post/post-detail.html",
                  {"post": post, "comment_form": comment_form})


def index(request):
    # filter(published_at__lte=timezone.now()
    posts = Post.objects.filter(published_at__isnull = False).order_by(
        '-published_at').prefetch_related(
        'images').prefetch_related(
        'tags').select_related(
        "author").defer(
        "created_at")
    return render(request, "post/index.html", {'posts': posts})
