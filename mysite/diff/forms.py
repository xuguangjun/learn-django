# -*- coding: utf-8 -*-
from django import forms


class CompareForm(forms.Form):
    file_one = forms.FileField()
    file_two = forms.FileField()
