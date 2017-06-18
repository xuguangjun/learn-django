# -*- coding: utf-8 -*-
from django import forms

from .models import NaviVersion


class ConfigForm(forms.Form):
    config = forms.FileField()


class UserForm(forms.Form):
    name = forms.CharField(max_length=50)
    passwd = forms.CharField(max_length=50, widget=forms.PasswordInput)
