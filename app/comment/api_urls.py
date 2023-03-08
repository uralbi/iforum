from django.urls import path, include
from rest_framework.routers import DefaultRouter
from comment import views

router = DefaultRouter()
router.register('comments', views.CommentViewSet)

app_name = 'comment'

urlpatterns = [
    path('', include(router.urls)),
    ]
