from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from core.models import Comment


class CommentSRZ(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'creator', 'content', 'content_type', 'object_id', 'created_at', 'modified_at']
        read_only_fields = ['id', 'creator', 'created_at', 'modified_at']
