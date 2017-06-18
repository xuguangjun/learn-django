# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.utils.encoding import python_2_unicode_compatible

# Create your models here.


@python_2_unicode_compatible
class Config(models.Model):  # used to keep configuration information
    config = models.TextField()
    user = models.CharField(max_length=50)
    navi_version_id = models.IntegerField()  # refer to NaviVersion table
    upload_time = models.DateTimeField()
    modify_time = models.DateTimeField()
    state = models.SmallIntegerField()  # change to unsigned

    def __str__(self):
        return self.user + "upload config, config data: \n" + self.config


class NaviVersion(models.Model):
    version_id = models.IntegerField()
    version_name = models.CharField(max_length=100)


class User(models.Model):
    username = models.CharField(max_length=50)
    passwd = models.CharField(max_length=50)


@python_2_unicode_compatible
class Case(models.Model):
    config_id = models.IntegerField(default=1)
    dir = models.CharField(max_length=100)  # absolute directory
    generate_time = models.DateTimeField()
    case_num = models.SmallIntegerField()
    name = models.CharField(max_length=100)
    download_times = models.SmallIntegerField()

    def __str__(self):
        return "config id: " + str(self.config_id) + ", generate_time: " + self.generate_time
