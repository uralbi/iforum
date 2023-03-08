""" Test for tags API. """

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Tag, Post
from post.srzs import TagSRZ

import random
import string

TAGS_URL = reverse('post:tags')
POST_URL = reverse('post:post-list')


def tag_url(tag_id):
    return reverse('post:tags', args=[tag_id])


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


class PublicTagsApiTests(TestCase):
    """ Test unauthenticated API requests. """

    def setUp(self):
        self.client = APIClient()

    def test_try_to_create_tag_error(self):
        """ Test creatign a tag by anauthorised user. """
        res = self.client.post(TAGS_URL, {"value": "Tag One"})
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    # def test_filter_tags_assigned_to_posts(self):
    #     """ Test listing tags by those assigned to posts. """
    #     t1 = Tag.objects.create(value='SUV truck')
    #     t2 = Tag.objects.create(value='private room')
    #     user = create_user()
    #     post = create_post(user=user)
    #     post.tags.add(t1)
    #     res = self.client.get(TAGS_URL, {'assigned_only': 1})
    #     s1 = TagSRZ(t1)
    #     s2 = TagSRZ(t2)
    #     self.assertIn(s1.data, res.data)
    #     self.assertNotIn(s2.data, res.data)

    # def test_filtered_tags_unique(self):
    #     tag = Tag.objects.create(value='used car')
    #     Tag.objects.create(value='nice books')
    #     user = create_user()
    #     post1 = create_post(user=user)
    #     post2 = create_post(user=user)
    #     post1.tags.add(tag)
    #     post2.tags.add(tag)
    #     res = self.client.get(TAGS_URL, {'assigned_only': 1})
    #     self.assertEqual(len(res.data), 1)


class PrivateTagsApiTests(TestCase):
    """ Test authenticated API requests. """

    def setUp(self):
        self.user = create_user()
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """ Test retrieving a list of tags for all users. """
        Tag.objects.create(value='furniture')
        Tag.objects.create(value='car parts')
        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('-value')
        srz = TagSRZ(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, srz.data)
