from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from django.urls import reverse

import random
import string
import tempfile
import os
from PIL import Image

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Post, Tag, Gallery, Comment
from post.srzs import PostSRZ, PostDetailSRZ


COMM_URL = reverse('comment:comment-list')


def detail_url(comm_id):
    """ Create and return a comment detail URL """
    return reverse('comment:comment-detail', args=[comm_id])


def create_user():
    """ Create and return a new user """
    email_string = ''.join(random.choices(
        string.ascii_letters + string.digits, k=5))
    password = ''.join(random.choices(
        string.ascii_letters + string.digits, k=10))
    email = f'{email_string}@example.com'
    return get_user_model().objects.create_user(
        email=email, password=password)


def create_post(user, **params):
    """ Create and return a sample Post. """

    defaults = {
        'title': 'Sample post one',
        'content': 'Content of the sample post one',
    }
    defaults.update(params)
    post = Post.objects.create(author=user, **defaults)
    return post


class PublicCommetAPITests(TestCase):
    """ Test public api requests. """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth is required """
        res = self.client.post(COMM_URL, {"id": 1})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_view_for_post(self):
        """ Test for listing all comments for the post. """
        user1 = create_user()
        user = create_user()
        post = create_post(user=user)
        ctype = ContentType.objects.get_for_model(post)
        comm = Comment.objects.create(creator=user1,
                                      content='Best Comment Ever',
                                      content_type=ctype,
                                      object_id=post.id)
        res = self.client.get(COMM_URL, {'content_type': 8, 'object_id': post.id})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(comm.content, res.data[0]['content'])


class PrivateCommentApiTests(TestCase):
    """ Test authentiated API requests. """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.user1 = create_user()
        self.post = create_post(user=self.user1)

    def test_create_comment(self):
        """ Test creating a comment """


        payload = {
            "content": 'new comment from me',
            "content_type": 8,
            "object_id": self.post.id,
        }
        res = self.client.post(COMM_URL, payload)
        comm = Comment.objects.all().first()
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(res.data['content'], comm.content)

    def test_delete_comment(self):
        """ Test deleting existing comment success"""
        user2 = create_user()
        post = create_post(user=user2)
        ctype = ContentType.objects.get_for_model(post)
        comm = Comment.objects.create(creator=self.user,
                                      content='Best Comment Ever',
                                      content_type=ctype,
                                      object_id=post.id)
        res = self.client.delete(detail_url(comm.id))
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

    def test_update_comment(self):
        """ Test updating existing comment success """
        user2 = create_user()
        post = create_post(user=user2)
        ctype = ContentType.objects.get_for_model(post)
        comm = Comment.objects.create(creator=self.user,
                                      content='Best Comment Ever',
                                      content_type=ctype,
                                      object_id=post.id)
        res = self.client.patch(detail_url(comm.id), {"content": "Updating this comment"})
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data['content'], 'Updating this comment')
