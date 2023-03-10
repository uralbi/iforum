from django.contrib.contenttypes.models import ContentType
from django.db.models import Q

from rest_framework import viewsets, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated, )
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from core.models import Post, Comment, Tag, Gallery
from comment import srzs


from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

"""
<class 'core.models.Post'> 8
<class 'core.models.Comment'> 9
<class 'core.models.Tag'> 7
<class 'core.models.Gallery'> 13
"""

if ContentType.objects.all().exists():
    my_models = {}
    for ctype in ContentType.objects.all():
        if ctype.app_label == 'core':
            my_models[ctype.model] = ctype.id
else:
    my_models = {'1': 1}

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'content_type',
                OpenApiTypes.INT, enum=[i for i in my_models.values()],
                # OpenApiTypes.INT,
                description='Content type id',
            ),
            OpenApiParameter(
                'object_id',
                OpenApiTypes.INT,
                description='Object id of the content type',
            ),
        ]
    )
)
class CommentViewSet(viewsets.ModelViewSet):
    """ View for manage comment APIs """
    serializer_class = srzs.CommentSRZ
    queryset = Comment.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        serializer = srzs.CommentSRZ(obj)
        return Response(serializer.data)

    def get_queryset(self):
        """ Retrieve comments for authenticated and ananymous users. """
        queryset = self.queryset
        c_type = self.request.query_params.get('content_type', 0)
        obj_id = self.request.query_params.get('object_id', 0)
        if self.request.method in ('PATCH', 'PUT', 'DELETE'):
            return queryset.all().filter(creator=self.request.user)
        return queryset.filter(content_type=c_type, object_id=obj_id).order_by('-created_at')

    def perform_create(self, serializer):
        """ Create a new comment """
        serializer.save(creator=self.request.user)
