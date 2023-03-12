from django.urls import path, include
from user import temp_views as views

app_name = 'tuser'

urlpatterns = [
    path("accounts/", include("django.contrib.auth.urls")),
    path("profile/", views.profile, name="profile"),
    ]