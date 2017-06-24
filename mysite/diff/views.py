# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .forms import CompareForm

# Create your views here.


def comparefile(request):
    # post only
    if request.method == "POST":
        pass
    else:
        compare_form = CompareForm()
    return render(request, "compare_file.html", {"compare_form": compare_form})