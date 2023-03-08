""" Serializers for recipe APIs """

from rest_framework import serializers as srzs
from core.models import Post, Tag, Gallery
from rest_framework.exceptions import PermissionDenied


class GallerySRZ(srzs.ModelSerializer):
    """ Serializer for the Gallery"""
    post = srzs.PrimaryKeyRelatedField(queryset=Post.objects.all())

    class Meta:
        model = Gallery
        fields = ['id', 'post', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}

    def create(self, validated_data):
        post = validated_data['post']
        request = self.context.get('request')
        if request.user == post.author:
            if post:
                gall = Gallery.objects.create(
                    post=post, image=validated_data['image'])
                gall.save()
                return gall
        else:
            raise PermissionDenied(
                'You are not authorized to create a gallery for this post')


class TagSRZ(srzs.ModelSerializer):
    """ Serializer for tags. """

    class Meta:
        model = Tag
        fields = ['id', 'value']
        read_only_fields = ['id']


class PostSRZ(srzs.ModelSerializer):
    """ Serializer for posts """
    tags = TagSRZ(many=True, required=False)

    class Meta:
        model = Post
        fields = ['id', 'author', 'title', 'views',
                  'published_at', 'slug', 'tags']
        read_only_fields = ['id', 'author', 'views', 'slug']

    def _get_or_create_tags(self, tags, post):
        """ Handle getting or creating tags as needed. """
        for tag in tags:
            tag_obj, created = Tag.objects.get_or_create(**tag)
            post.tags.add(tag_obj)

    def create(self, validated_data):
        """ Create a post """
        tags = validated_data.pop('tags', [])
        post = Post.objects.create(**validated_data)
        self._get_or_create_tags(tags, post)
        return post

    def update(self, instance, validated_data):
        """ Update recipe. """
        tags = validated_data.pop('tags', None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PostDetailSRZ(PostSRZ):
    """ Serializer for post detail view. """

    class Meta(PostSRZ.Meta):
        fields = PostSRZ.Meta.fields + ['content']
