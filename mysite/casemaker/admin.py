# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from .models import Config, NaviVersion, User

# Register your models here.
admin.site.register(Config)
admin.site.register(NaviVersion)
admin.site.register(User)
