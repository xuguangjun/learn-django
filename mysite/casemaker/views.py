# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import os
import logging
import datetime
import zipfile
import shutil


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .forms import ConfigForm, UserForm
from .models import Config, NaviVersion, Case, User
from .util import read_file_data, VersionHelperClass

# Create your views here.
logger = logging.getLogger(__name__)


def index(request):
    # if has login in, jump to allconfig page
    # if not, jump to login page
    if "login_name" in request.COOKIES:
        # check if valid, if valid, jump to all config page
        login_name = request.COOKIES.get("login_name")
        user = User.objects.filter(username__exact=login_name)
        if user:
            return HttpResponseRedirect("/casemaker/config/")
    user_form = UserForm()
    return render(request, "login.html", {"user_form": user_form})


def login(request):
    # check user name and password, if succ, set cookie in response
    if request.method == "POST":
        user_form = UserForm(request.POST)
        if user_form.is_valid():
            username = user_form.cleaned_data["name"]
            password = user_form.cleaned_data["passwd"]
            logger.info("user login in, user name: " + username + ", password: " + password)
            user = User.objects.filter(username__exact=username, passwd__exact=password)
            if user:
                logger.info("user: " + username + "login in success")
                response = HttpResponseRedirect("/casemaker/index/")
                response.set_cookie('login_name', username, 1)
                return response
            else:
                logger.info("user: " + username + " login in failed")
    user_form = UserForm()
    return render(request, "login.html", {"user_form": user_form})



def allconfig(request):
    # fetch all configuration info from databases
    # TODO fetch by page
    config = Config.objects.all()
    version = NaviVersion.objects.all()
    return render(request, 'config.html', {'config': config, 'version': version})


def config_detail(request, id):
    config = get_object_or_404(Config, pk=id)
    return render(request, 'config_detail.html', {"data": config.config})


def uploadconfig(request):
    if request.method == 'POST':
        config_form = ConfigForm(request.POST, request.FILES)
        if config_form.is_valid():
            logger.info("config valid")
            config_data = read_file_data(request.FILES['config'])
            logger.info("post data: " + str(request.POST))
            config = Config()
            config.config = config_data
            if "user" in request.POST:
                config.user = request.POST["user"]
            else:
                config.user = "wangli"
            if "version_id" in request.POST:
                config.navi_version_id = request.POST["version_id"]
            else:
                config.navi_version_id = 1
            config.upload_time = datetime.datetime.now()
            config.modify_time = config.upload_time
            config.state = 1
            config.save()
            return HttpResponseRedirect('/casemaker/config/')
        else:
            logger.error("config invalid")
    else:
        logger.error("method get")
        config_form = ConfigForm()
    return render(request, 'config_upload.html', {'config_form': config_form, "versions": NaviVersion.objects.all()})


def allcase(request):
    case = Case.objects.all()
    return render(request, "case.html", {'case': case})


def case_detail(request, id):
    case = get_object_or_404(Case, pk=id)
    return render(request, "case_detail.html", {'case': case})


def generate_case(request):
    if request.method == "POST":
        if "config_id" not in request.POST:
            return HttpResponse("required param missing: config_id")
        config_id = request.POST["config_id"]
        config = Config.objects.get(pk=config_id)
        if not config:
            return HttpResponse("config_id is not valid: " + config_id)
        config_data = config.config
        logger.info("config_id: " + config_id + ", config data: " + config_data)
        # todo generate the cases, temporary we just create a random file
        # after generate the case, change the state in Config database
        base_dir = os.path.join("case", config.user)
        dir = os.path.join(base_dir, config_id)
        if os.path.exists(dir):
            # os.rmdir(dir) 只能删除空文件夹
            shutil.rmtree(dir)
        os.makedirs(dir)
        name = "test.txt"
        filename = os.path.join(dir, name)
        with open(filename, "w") as f:
            f.write("hahaah")
        case = Case()
        case.config_id = config_id
        case.generate_time = datetime.datetime.now()
        case.dir = dir
        case.name = name
        case.case_num = 1
        case.download_times = 0
        case.save()
        config.state = 2
        config.save()
        return HttpResponseRedirect("/casemaker/config/".format(config_id))
    else:
        return HttpResponse("request method must be POST")


def download_all_case(request):
    zip_filename = "zip_file.zip"  # todo change according to request info
    if not os.path.isfile(zip_filename):
        logger.info("generate new zip file: " + zip_filename)
        archive = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
        for dir_path, dir_names, filenames in os.walk("./casemaker"):
            for filename in filenames:
                archive.write(os.path.join(dir_path, filename))
        archive.close()
    with open(zip_filename, 'rb') as f:
        content = f.read()
    response = HttpResponse(content)
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="all_case.zip"'
    return response


def download_case(request, config_id):
    case = get_object_or_404(Case, config_id=config_id)
    if not case:
        logger.error("case not exists, maybe has not generated, config id: " + config_id)
        return HttpResponseRedirect("/casemaker/case/")
    zip_filename = os.path.join(case.dir, case.name)
    if not os.path.isfile(zip_filename):
        logger.info("generate new zip file: " + zip_filename)
        archive = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
        for dir_path, dir_names, filenames in os.walk(case.dir):
            for filename in filenames:
                archive.write(os.path.join(dir_path, filename))
        archive.close()
    with open(zip_filename, 'rb') as f:
        content = f.read()
    response = HttpResponse(content)
    response["Content-Type"] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment;filename={}".format(case.name)
    return response

