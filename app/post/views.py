from django.shortcuts import render

from django.db.models import Q
from rest_framework import viewsets, generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated, )
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import status
from core.models import Post, Tag, Gallery
from post import srzs
import datetime
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)

def index(request):
    posts = Post.objects.filter(published_at__isnull = False).order_by('-published_at')
    return render(request, "post/index.html", {'posts': posts})

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter',
            ),
        ]
    )
)
class PostViewSet(viewsets.ModelViewSet):
    """ View for manage post APIs """
    serializer_class = srzs.PostDetailSRZ
    queryset = Post.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def _params_to_ints(self, qs):
        """ Convert a list of strings to integers. """
        return [int(str_id) for str_id in qs.split(',')]

    def retrieve(self, request, pk=None):
        obj = self.get_object()
        obj.views += 1
        obj.save()
        serializer = srzs.PostDetailSRZ(obj)
        return Response(serializer.data)

    def get_queryset(self):
        """ Retrieve recipes for authenticated and ananymous users. """
        tags = self.request.query_params.get('tags')
        queryset = self.queryset
        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids).distinct()
        if self.request.method in ('PATCH', 'PUT', 'DELETE'):
            return queryset.all().filter(author=self.request.user)
        if self.request.user.is_authenticated:
            return queryset.all().exclude(
                ~Q(author=self.request.user) & Q(published_at=None))
        return queryset.all().exclude(
            published_at=None).order_by('-published_at')

    def get_serializer_class(self):
        if self.action == 'list':
            return srzs.PostSRZ
        return self.serializer_class

    def perform_create(self, serializer):
        """ Create a new recipe """
        serializer.save(author=self.request.user)


class PostPublishView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = srzs.PostDetailSRZ

    def post(self, request, pk):
        post = Post.objects.get(pk=pk)
        if post.author != request.user:
            return Response(status.HTTP_401_UNAUTHORIZED)
        post.published_at = datetime.datetime.now()
        srz = srzs.PostDetailSRZ(post, data=request.data, partial=True)
        if srz.is_valid():
            srz.save()
            return Response(srz.data, status.HTTP_200_OK)
        else:
            return Response(srz.errors, status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                OpenApiTypes.INT, enum=[0, 1],
                description='Filter by items assigned to posts.',
            ),
        ]
    )
)
class TagView(generics.ListCreateAPIView):
    serializer_class = srzs.TagSRZ
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]
    # generics.ListCreateAPIView

    def list(self, request):
        qs = self.get_queryset()
        srz = srzs.TagSRZ(qs, many=True)
        return Response(srz.data)

    def get_queryset(self):
        """ Filter queryset """
        assigned_only = bool(
            int(self.request.query_params.get('assigned_only', 0))
        )
        queryset = Tag.objects.all()
        if assigned_only:
            queryset = queryset.filter(post__isnull=False)
        return queryset


class GalleryView(generics.ListCreateAPIView):
    serializer_class = srzs.GallerySRZ
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [TokenAuthentication]

    def list(self, request):
        qs = self.get_queryset()
        srz = srzs.GallerySRZ(qs, many=True)
        return Response(srz.data)

    def get_queryset(self):
        gueryset = Gallery.objects.all()
        return gueryset
