from django.urls import path, include
from rest_framework.routers import DefaultRouter
from post import views

router = DefaultRouter()
router.register('posts', views.PostViewSet)

app_name = 'post'

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<int:pk>/publish/',
         views.PostPublishView.as_view(), name='post_publish_field'),
    path('tags/', views.TagView.as_view(), name='tags'),
    path('gallery/', views.GalleryView.as_view(), name='gallery'),
    ]
