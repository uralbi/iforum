from django.urls import path, include
from post import views


app_name = 'post'

urlpatterns = [
    path('', views.index, name='home page'),
    path('post/<int:pk>/', views.post_detail, name="post-detail"),
    ]
