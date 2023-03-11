# import uuid
# import os

from django.conf import settings
from django.contrib.auth.models import AbstractUser, UserManager
from django.utils.translation import gettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import PermissionDenied
from django.db import models
from django.utils.text import slugify


class IforumUserManager(UserManager):
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError("Email must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = models.CharField(max_length=255, blank=True)
    email = models.EmailField(
        _("email address"),
        unique=True,
    )

    objects = IforumUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email


class Tag(models.Model):
    value = models.CharField(max_length=100)

    def create(self, *args, **kwargs):
        if not self.request.user.is_authorized:
            raise PermissionDenied(
                "You do not have permission to create objects.")
        return super().create(*args, **kwargs)

    def __str__(self):
        return self.value


class Gallery(models.Model):
    post = models.ForeignKey(
        'Post', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(
        upload_to='gallery/%Y/%m/%d')  # upload_to=galler_image_path
    created_at = models.DateTimeField(
        auto_now_add=True, db_index=True)


class Comment(models.Model):
    creator = models.ForeignKey(settings.AUTH_USER_MODEL,
                                on_delete=models.CASCADE)
    content = models.TextField()
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, related_name='comments')
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey("content_type", "object_id")
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    modified_at = models.DateTimeField(auto_now=True)


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)
    published_at = models.DateTimeField(blank=True,
                                        null=True,
                                        db_index=True)
    title = models.TextField(max_length=100)
    content = models.TextField()
    slug = models.SlugField()
    views = models.SmallIntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name='posts', blank=True)
    comments = GenericRelation(Comment)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.title + '_' + f'{self.pk}')
        super(Post, self).save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class AuthorProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
        )
    bio = models.TextField()
    #   pic = GenericRelation(Gallery)

    def __str__(self):
        return f"{self.__class__.__name__} object for {self.user}"
