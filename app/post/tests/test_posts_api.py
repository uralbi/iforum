from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

import random
import string
import tempfile
import os
from PIL import Image

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Post, Tag, Gallery
from post.srzs import PostSRZ, PostDetailSRZ


POST_URL = reverse('post:post-list')


def detail_url(post_id):
    """ Create and return a recipe detail URL """
    return reverse('post:post-detail', args=[post_id])


def publish_url(post_id):
    return reverse('post:post_publish_field', args=[post_id])


def create_post(user, **params):
    """ Create and return a sample Post. """

    defaults = {
        'title': 'Sample post one',
        'content': 'Content of the sample post one',
    }
    defaults.update(params)
    post = Post.objects.create(author=user, **defaults)
    return post


def image_upload_url():
    """ Create and return an image upload URL """
    return reverse('post:gallery')


def create_user():
    """ Create and return a new user """
    email_string = ''.join(random.choices(
        string.ascii_letters + string.digits, k=5))
    password = ''.join(random.choices(
        string.ascii_letters + string.digits, k=10))
    email = f'{email_string}@example.com'
    return get_user_model().objects.create_user(
        email=email, password=password)


class PublicPostAPITests(TestCase):
    """ Test public api requests. """

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """ Test auth is required """
        res = self.client.get(POST_URL)
        self.assertEqual(res.status_code, 200)

    def test_publish_post(self):
        """ Test update post to published by anauthorized user """
        other_user = get_user_model().objects.create_user(
            'other@ex.com',
            'testpass123',
            )
        post = create_post(user=other_user)
        payload = {"published_at": "2023-02-02T03:11:11-08:00"}
        res = self.client.post(publish_url(post.id), payload)
        self.assertIsNotNone(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivatePostApiTests(TestCase):
    """ Test authentiated API requests. """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrive_post(self):
        """ Test regrieving a list of posts """
        create_post(user=self.user, published_at="2023-03-04T18:57:33Z")
        create_post(user=self.user, published_at="2023-03-03T18:57:33Z")
        res = self.client.get(POST_URL)
        posts = Post.objects.all().order_by('-published_at')
        srz = PostSRZ(posts, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, srz.data)

    def test_posts_list_to_user(self):
        """ Test list of posts is limited to authenticated user. """
        other_user = create_user()
        create_post(user=other_user, published_at="2023-03-04T11:57:33Z")
        create_post(user=self.user, published_at="2023-03-03T18:57:33Z")
        res = self.client.get(POST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 2)

    def test_get_post_detail(self):
        """ Test get published post detail. """
        post = create_post(user=self.user, published_at='2023-02-02T11:11:11Z')
        url = detail_url(post.id)
        res = self.client.get(url)
        srz = PostDetailSRZ(post)
        self.assertEqual(res.data['id'], srz.data['id'])
        self.assertEqual(res.data['views'], 1)

    def test_create_post(self):
        """ Test creating a post through API """
        payload = {
            'title': 'Sample post',
            'content': 'Content of the sample post',
        }
        res = self.client.post(POST_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.get(id=res.data['id'])
        for k, v in payload.items():
            with self.subTest(value=f'{k}:{v}'):
                self.assertEqual(getattr(post, k), v)
        self.assertEqual(post.author, self.user)

    def test_publish_post(self):
        """ Test update post published_at with API """
        post = create_post(user=self.user)
        payload = {"published_at": "2023-02-02T03:11:11-08:00"}
        res = self.client.post(publish_url(post.id), payload)
        self.assertEqual(res.data['published_at'], payload['published_at'])

    def test_partial_update(self):
        """ Test partial update of a post """
        post = create_post(user=self.user)
        payload = {'title': 'New Updated title'}
        url = detail_url(post.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        self.assertEqual(post.title, payload['title'])
        self.assertEqual(post.author, self.user)

    def test_full_update(self):
        """ Test full update POST """
        post = create_post(user=self.user)
        payload = {
            'title': 'Full new Post',
            'content': 'new content of the full new post',
        }
        url = detail_url(post.id)
        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        post.refresh_from_db()
        for k, v in payload.items():
            with self.subTest(value=f'{k}:{v}'):
                self.assertEqual(getattr(post, k), v)
        self.assertEqual(post.author, self.user)

    def test_update_user_returns_error(self):
        """ Test changing the post author results in error """
        new_user = create_user()
        post = create_post(user=self.user)
        payload = {'author': new_user.id}
        url = detail_url(post.id)
        self.client.patch(url, payload)
        post.refresh_from_db()
        self.assertEqual(post.author, self.user)

    def test_delete_post(self):
        """ Test deleting a post successful. """
        post = create_post(user=self.user)
        url = detail_url(post.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Post.objects.filter(id=post.id).exists())

    def test_post_delete_other_user(self):
        """ Test trying to delete another users post gives error. """
        new_user = create_user()
        post = create_post(user=new_user, published_at='2023-02-02T11:11:11Z')
        # post = create_post(user=new_user)
        url = detail_url(post.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Post.objects.filter(id=post.id).exists())

    def test_create_post_with_tags(self):
        """ Test creating a post with new tags. """
        payload = {
            'title': 'Selling my new laptop',
            'content': 'Macbook pro 14 in good condition',
            'tags': [{'value': 'macbook pro 14'}, {'value': 'selling laptop'}]
        }
        res = self.client.post(POST_URL, payload, format='json')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        post = Post.objects.filter(author=self.user)
        self.assertEqual(post.count(), 1)
        post = post[0]
        self.assertEqual(post.tags.count(), 2)
        for tag in payload['tags']:
            exists = post.tags.filter(**tag).exists()
            with self.subTest(tag=tag):
                self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """ Test creating tag when updating a post """
        post = create_post(user=self.user)
        payload = {'tags': [{'value': 't shirt'}]}
        url = detail_url(post.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        new_tag = Tag.objects.get(value='t shirt')
        self.assertIn(new_tag, post.tags.all())

    def test_update_post_assign_tag(self):
        """ Test assigning an existing tag when updating a post """
        tag1 = Tag.objects.create(value='prius 2011')
        post = create_post(user=self.user)
        post.tags.add(tag1)
        tag2 = Tag.objects.create(value='bmw x5')
        payload = {'tags': [{'value': 'bmw x5'}]}
        url = detail_url(post.id)

        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(tag2, post.tags.all())
        self.assertNotIn(tag1, post.tags.all())

    def test_clear_post_tags(self):
        """ Test clearing a post tags """
        ag1 = Tag.objects.create(value='prius 2011')
        post = create_post(user=self.user)
        post.tags.add(ag1)
        payload = {'tags': []}
        url = detail_url(post.id)
        res = self.client.patch(url, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(post.tags.count(), 0)

    def test_filter_by_tags(self):
        """ Test filtering post by tags. """
        p1 = create_post(user=self.user, title='first my post')
        p2 = create_post(user=self.user, title='second my post')
        tag1 = Tag.objects.create(value='sport car')
        tag2 = Tag.objects.create(value='adidas shoes')
        p1.tags.add(tag1)
        p2.tags.add(tag2)
        p3 = create_post(user=self.user, title='Raw fish for sale')
        params = {'tags': f'{tag1.id}, {tag2.id}'}
        res = self.client.get(POST_URL, params)
        s1 = PostSRZ(p1)
        s2 = PostSRZ(p2)
        s3 = PostSRZ(p3)
        self.assertIn(s1.data, res.data)
        self.assertIn(s2.data, res.data)
        self.assertNotIn(s3.data, res.data)


class ImageUploadTests(TestCase):
    """ Tests for the image upload API. """

    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)
        self.post = create_post(user=self.user)
        self.gallery = ''

    def tearDown(self):
        if self.gallery:
            self.gallery.delete()

    def test_upload_image(self):
        """ Test uploading an image to a recipe. """
        post = Post.objects.all().first()
        self.assertEqual(self.post.id, post.id)

        url = image_upload_url()
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'post': self.post.id, 'image': image_file}
            res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.gallery = Gallery.objects.all().first()
        self.gallery.refresh_from_db()
        self.assertIn('image', res.data)
        self.assertTrue(os.path.exists(self.gallery.image.path))

    def test_upload_bad_request(self):
        """ Test uploading invalid image. """
        url = image_upload_url()
        payload = {'post': 1, 'image': 'notanimage'}
        res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_upload_by_other_user_forbidden(self):
        """ Test uploading image to a post by other user. """
        self.other_user = create_user()
        self.post2 = create_post(user=self.other_user)
        url = image_upload_url()
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {'post': self.post2.id, 'image': image_file}
            res = self.client.post(url, payload, format='multipart')
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
