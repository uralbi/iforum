from django.urls import path, include
from post import temp_views as views
from django.conf import settings
import logging
logger = logging.getLogger(__name__)

app_name = 'tpost'

urlpatterns = [
    path('', views.index, name='home page'),
    path('post/<int:pk>/', views.post_detail, name="post-detail"),
    ]
