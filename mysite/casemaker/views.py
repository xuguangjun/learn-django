# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division  # for division
import os
import logging
import datetime
import time
import zipfile
import shutil
import ConfigParser
import io
from math import ceil


from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from .forms import ConfigForm, UserForm
from .models import Config, NaviVersion, Case, User
from .util import read_file_data, CONFIG_STATE_DOING, CONFIG_STATE_DONE,CONFIG_STATE_INITIAL
from .util import TEST_CASE_GENERATE, ITEM_NUM_PER_PAGE, GET_PAGE_DOWN, GET_PAGE_UP, GET_PAGE_CURRENT

# Create your views here.
logger = logging.getLogger(__name__)


def is_login(request):
    if "login_name" in request.COOKIES:
        login_name = request.COOKIES.get("login_name")
        user = User.objects.filter(username__exact=login_name)
        if user:
            return True
    return False


def index(request):
    # if has login in, jump to allconfig page
    # if not, jump to login page
    if not is_login(request):
        return HttpResponseRedirect(reverse("login"))
    return HttpResponseRedirect(reverse("allconfig"))


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
                logger.info("user: " + username + " login in success")
                response = HttpResponseRedirect(reverse("allconfig"))
                response.set_cookie('login_name', username, 86400)  # cookie valid in 1 day
                return response
            else:
                logger.info("user: " + username + " login in failed")
    user_form = UserForm()
    return render(request, "login.html", {"user_form": user_form})


def allconfig(request):
    # fetch all configuration info from databases
    if not is_login(request):
        return HttpResponseRedirect(reverse("login"))
    total = Config.objects.count()  # total items count in database
    total_page_num = int(ceil(total / ITEM_NUM_PER_PAGE))
    logger.info("all config num: " + str(total) + ", total page num: " + str(total_page_num))
    current_page = 1
    want_page = current_page
    page_type = GET_PAGE_CURRENT
    if "total_page_num" in request.GET:
        total_page_num = int(request.GET["total_page_num"])
    if "current_page" in request.GET:
        current_page = int(request.GET["current_page"])
    if "page_type" in request.GET:
        page_type = int(request.GET["page_type"])
    if page_type == GET_PAGE_DOWN:
        want_page = current_page + 1
        if want_page > total_page_num:
            want_page = total_page_num
    elif page_type == GET_PAGE_UP:
        want_page = current_page - 1
        if want_page < 1:
            want_page = 1
    start_pos = (want_page - 1) * ITEM_NUM_PER_PAGE
    end_pos = start_pos + ITEM_NUM_PER_PAGE
    config = Config.objects.order_by("-id").all()[start_pos:end_pos]  # order by id desc
    version = NaviVersion.objects.all()
    return render(request, 'config.html', {'config': config, 'version': version,
                                           'total_page': total_page_num, "current_page": want_page})


def config_detail(request, id):
    if not is_login(request):
        return HttpResponseRedirect(reverse("login"))
    config = get_object_or_404(Config, pk=id)
    return render(request, 'config_detail.html', {"data": config.config})


def uploadconfig(request):
    if not is_login(request):
        return HttpResponseRedirect(reverse("login"))
    if request.method == 'POST':
        config_form = ConfigForm(request.POST, request.FILES)
        if config_form.is_valid():
            logger.info("config valid")
            config_data = read_file_data(request.FILES['config'])
            if config_data == "":
                logger.error("config format is not valid, config file must utf-8 encoded")
                return HttpResponse("sorry, config file must be utf-8 encoded")
            logger.info("post data: " + str(request.POST))
            config = Config()
            config.config = config_data
            config.user = request.COOKIES["login_name"]
            if "version_id" in request.POST:
                config.navi_version_id = request.POST["version_id"]
            else:
                config.navi_version_id = 1  # fallback
            config.upload_time = datetime.datetime.now()
            config.modify_time = config.upload_time
            config.state = CONFIG_STATE_INITIAL
            config.save()
            return HttpResponseRedirect(reverse("allconfig"))
        else:
            logger.error("config invalid")
    else:
        logger.error("method get")
        config_form = ConfigForm()
    return render(request, 'config_upload.html', {'config_form': config_form, "versions": NaviVersion.objects.all()})


def allcase(request):
    if not is_login(request):
        return HttpResponseRedirect(reverse("login"))
    total = Case.objects.count()  # total items count in database
    total_page_num = int(ceil(total / ITEM_NUM_PER_PAGE))
    logger.info("all case num: " + str(total) + ", total page num: " + str(total_page_num))
    current_page = 1
    want_page = current_page
    page_type = GET_PAGE_CURRENT
    if "total_page_num" in request.GET:
        total_page_num = int(request.GET["total_page_num"])
    if "current_page" in request.GET:
        current_page = int(request.GET["current_page"])
    if "page_type" in request.GET:
        page_type = int(request.GET["page_type"])
    if page_type == GET_PAGE_DOWN:
        want_page = current_page + 1
        if want_page > total_page_num:
            want_page = total_page_num
    elif page_type == GET_PAGE_UP:
        want_page = current_page - 1
        if want_page < 1:
            want_page = 1
    start_pos = (want_page - 1) * ITEM_NUM_PER_PAGE
    end_pos = start_pos + ITEM_NUM_PER_PAGE
    case = Case.objects.order_by("-config_id").all()[start_pos:end_pos]  # order by config_id desc
    return render(request, "case.html", {'case': case, 'current_page': want_page, 'total_page': total_page_num})


def case_detail(request, id):
    if not is_login(request):
        return HttpResponseRedirect(reverse("login"))
    case = get_object_or_404(Case, pk=id)
    return render(request, "case_detail.html", {'case': case})


def generate_case(request):
    if not is_login(request):
        return HttpResponseRedirect(reverse("login"))
    if request.method == "POST":
        if "config_id" not in request.POST:
            return HttpResponse("required param missing: config_id")
        config_id = request.POST["config_id"]
        config = Config.objects.get(pk=config_id)
        if not config:
            return HttpResponse("config_id is not valid: " + config_id)
        config_data = config.config
        # check if case generate is in process, if so, just return to allconfig page and tell user the state
        if config.state == CONFIG_STATE_DOING:
            return HttpResponseRedirect(reverse("allconfig"))  # redirect to all config page
        # mark config generating case state, in case of repeating requests
        # but if generating case failed, remind to fallback state to CONFIG_STATE_INITIAL
        config.state = CONFIG_STATE_DOING
        config.save()
        logger.info("generate case for config_id: " + config_id + ", config data: \n" + config_data)
        try:
            base_dir = os.path.join("case_data", config.user)
            dir = os.path.join(base_dir, config_id)
            if os.path.exists(dir):
                # os.rmdir(dir) 只能删除空文件夹
                shutil.rmtree(dir)
            os.makedirs(dir)
            case_num_index = 0
            if not TEST_CASE_GENERATE:
                from casegenerator.caseGenerator import load_old_pb, generate_new_pb, write_to_file
                from casegenerator.caseGenerator import get_old_pb_from_file, ORIGINAL_PB_SOURCE
                from casegenerator.configReader import parse_case_from_config
                # TODO load pb binary data from databases
                old_pb = load_old_pb(get_old_pb_from_file(ORIGINAL_PB_SOURCE))
                config_object = ConfigParser.SafeConfigParser()
                config_object.readfp(io.BytesIO(config_data.encode("utf-8")))
                cases = parse_case_from_config(config_object)
                for generated_case in cases:
                    new_pb_content = generate_new_pb(old_pb, generated_case)
                    write_to_file(os.path.join(dir, str(case_num_index)), new_pb_content)
                    case_num_index += 1
            else:
                # just for debug test, you need not care about this
                # remember set TEST_CASE_GENERATE to False to prevent run to here
                name = "test.txt"
                filename = os.path.join(dir, name)
                for i in range(1, 10):
                    time.sleep(2)  # for test repeat request dure generating case
                    case_num_index += 1
                with open(filename, "w") as f:
                    f.write("hahaah")
            case = Case()
            case.config_id = config_id
            case.generate_time = datetime.datetime.now()
            case.dir = dir
            # the zip file will generate when first downloaded
            case.name = config.user + "_" + str(time.time()) + ".zip"
            case.case_num = case_num_index
            case.download_times = 0
            case.save()
        except Exception, e:
            logger.error("exception caught when generate case for config, config id: " + str(config_id)
                         + ", exception: " + str(e))
            # fallback config state
            config.state = CONFIG_STATE_INITIAL
            config.save()
            return HttpResponseRedirect(reverse("allconfig"))  # redirect to all config page
        # after generate the case, change the state in Config database
        config.state = CONFIG_STATE_DONE
        config.save()
        return HttpResponseRedirect(reverse("allconfig"))  # redirect to all config page
    else:
        return HttpResponse("request method must be POST")


def download_case(request, config_id):
    if not is_login(request):
        return HttpResponseRedirect(reverse("login"))
    case = get_object_or_404(Case, config_id=config_id)
    if not case:
        logger.error("case not exists, maybe has not generated, config id: " + config_id)
        return HttpResponseRedirect(reverse("allconfig"))
    zip_filename = os.path.join(case.dir, case.name)
    if not os.path.isfile(zip_filename):
        logger.info("generate new zip file: " + zip_filename)
        archive = zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED)
        for dir_path, dir_names, filenames in os.walk(case.dir):
            for filename in filenames:
                full_path_name = os.path.join(dir_path, filename)
                if full_path_name == zip_filename:  # except zip file itself
                    logger.info("file name: " + full_path_name)
                    continue
                archive.write(full_path_name)
        archive.close()
    with open(zip_filename, 'rb') as f:
        content = f.read()
    response = HttpResponse(content)
    response["Content-Type"] = 'application/octet-stream'
    response['Content-Disposition'] = "attachment;filename={}".format(case.name)
    case.download_times += 1
    case.save()
    return response

