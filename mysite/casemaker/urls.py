from django.conf.urls import include, url
from django.contrib import admin

from . import views


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^index/', views.index, name="index"),
    url(r'^login/', views.login, name="login"),
    url(r'^config/$', views.allconfig, name="allconfig"),
    url(r'^config/upload/$', views.uploadconfig, name="uploadconfig"),
    url(r'^config/detail/(?P<id>[0-9]+)/$', views.config_detail, name="config_detail"),
    url(r'^case/$', views.allcase, name="allcase"),
    url(r'^case/detail/(?P<id>[0-9]+)/$', views.case_detail, name="case_detail"),
    url(r'^case/generate/$', views.generate_case, name="generate_case"),
    #url(r'case/download/$', views.download_all_case, name="download_all_case"),
    url(r'case/download/(?P<config_id>[0-9]+)/$', views.download_case, name="download_case"),
]
