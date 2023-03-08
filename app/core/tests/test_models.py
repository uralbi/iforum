""" Test for models """
# from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from core import models
import random
import string


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
    post = models.Post.objects.create(author=user, **defaults)
    return post


class ModelTests(TestCase):

    def test_create_user_with_email(self):
        """ Test creating a user with email is successful. """
        email = 'test@example.com'
        password = 'testpass123'
        user = models.User.objects.create_user(email=email, password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalized_emails(self):
        """ Test email is normalized for new users. """
        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.COM', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com']
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, 'sample123')
            with self.subTest(text=expected):
                self.assertEqual(user.email, expected)

    def test_user_without_email_error(self):
        """ Test a user without an email raises a ValuerError """
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user('', 'test123')

    def test_create_superuser(self):
        """ Test creating a superuser """
        user = get_user_model().objects.create_superuser(
            'test@example.com',
            'test123'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_post(self):
        """ Test creating a post is successful. """
        user = create_user()
        post = models.Post.objects.create(
            author=user,
            title='Sample post ONE',
            content='Sample content of the post one'
        )
        self.assertEqual(str(post), post.title)
        self.assertEqual(post.views, 0)

    def test_create_tag(self):
        """ Test creating a Tag """
        tag = models.Tag.objects.create(value='NewTag')
        self.assertEqual(str(tag), tag.value)


    def test_create_comments(self):
        """ Test creating a comment to the Post """
        new_user = create_user()
        sec_user = create_user()
        post = create_post(user=new_user)
        comment = models.Comment.objects.create(
            creator=sec_user,
            content='Nice One Post',
            content_type = ContentType.objects.get_for_model(post),
            object_id = post.id)

        cmm = models.Comment.objects.all().first()
        self.assertEqual(cmm.creator, sec_user)
        self.assertTrue(cmm)


class ImageUploadTests(TestCase):
    """ Tests for the image upload API. """

    def setUp(self):
        self.user = create_user()
        self.post = create_post(user=self.user)
        self.gallery = ''

    def tearDown(self):
        self.gallery.delete()

    def test_upload_image(self):
        """ Test creating gallery for the post. """
        self.gallery = models.Gallery.objects.create(
            post=self.post, image='image.jpg')
        self.gallery = models.Gallery.objects.create(
            post=self.post, image='image2.jpg')
        gal = models.Gallery.objects.all().first()
        self.assertEqual(gal.image.path, '/vol/web/media/image.jpg')
        self.assertEqual(self.post.author, self.user)
        self.assertEqual(self.post.images.count(), 2)
