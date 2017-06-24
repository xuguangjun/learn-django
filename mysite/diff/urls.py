from django.conf.urls import include, url
from django.contrib import admin

from . import views


urlpatterns = [
    url(r'^compare_file/', views.comparefile, name="compare_file"),
]