# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import time

from saltstack import SaltApi
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, Http404
from django.shortcuts import render
from web.models import *


# Create your views here.


def index(req):
    host = Host.objects.all()
    totalNum = len(host)
    runNum = len(host.filter(stress_test="running"))
    # stopNum = len(Host.objects.filter(Q(stress_test="running") |
    #                                   Q(stress_test__contains="OS off")))
    offNum = len(host.filter(status__contains="erro"))
    return render(req, 'index.html', {'totalNum': totalNum, 'runNum': runNum,
                                             'offNum': offNum})


def serverDetail(req):
    global name, status
    name = req.GET.get("name")
    status = req.GET.get("status")
    return render(req, 'serverdetail.html')


def bios(req):
    return render(req, 'bios.html')


def execute(req):
    return render(req, 'execute.html')


def serverInfo(request):
    limit = request.GET.get("limit")
    offset = request.GET.get("offset")
    search = request.GET.get("search")
    state = request.GET.get("state")
    sort = request.GET.get("sort")
    sortOrder = request.GET.get("sortOrder")
    try:
        if name and status:
            if name == "run":
                host = Host.objects.filter(stress_test=status)
            elif name == "error":
                host = Host.objects.filter(status__contains=status)
            global name, status
            name, status = '', ''
        else:
            host = Host.objects.all()
    except Exception:
        host = Host.objects.all()
    if state:
        host = host.filter(stress_test=state)
    if sort and sortOrder:
        if sortOrder == "asc":
            host = host.order_by("{}".format(sort))
        elif sortOrder == "desc":
            host = host.order_by("-{}".format(sort))
    if search:
        host = host.filter(Q(sn__contains=search) |
                           Q(sn_1__contains=search) |
                           Q(name1__contains=search) |
                           Q(name__contains=search) |
                           Q(family__contains=search) |
                           Q(status__contains=search) |
                           Q(ip__contains=search))
    lenth = len(host)
    if offset and limit:
        offset = int(offset)
        limit = int(limit)
        host = host[offset:offset + limit]
    data = []
    for each in host:
        data.append(model_to_dict(each, fields=['id', 'sn', 'sn_1', 'name', 'name1', 'family',
                                                'status', 'bios', 'bmc', 'ip', 'stress_test']))
    return HttpResponse(json.dumps({"rows": data, "total": lenth}))


def control(req):
    salt_api = "https://127.0.0.1:8000/"
    Salt = SaltApi(salt_api)
    state = req.POST.get('state')
    name = req.POST.get('name')
    file = req.FILES.get('fru_sn')
    if state == "bios":
        cmd = '/bios/{}/BIOS_lnx64.sh'.format(name)
        msg = req.POST.get('msg')
        if msg:
            msg = json.loads(msg)
            for each in msg:
                Salt.cmd('{}'.format(each['ip']), 'cmd.run', ['{}'.format(cmd)])
                time.sleep(10)
    elif state == "bmc":
        cmd = '/bmc/{}/BMC_lnx64.sh'.format(name)
        msg = req.POST.get('msg')
        if msg:
            msg = json.loads(msg)
            for each in msg:
                Salt.cmd('{}'.format(each['ip']), 'cmd.run', ['{}'.format(cmd)])
    elif file:
        sn = file.readlines()
        for i in sn:
            print i.strip()
        cmd = ''
        msg = req.POST.get('msg')
        fru_name = req.POST.get('fru_name')
        print fru_name
        if msg:
            msg = json.loads(msg)
            if len(msg) != len(sn):
                return
            for each in msg:
                print each['ip']
                try:
                    Salt.cmd('{}'.format(each['ip']), 'cmd.run', ['{}'.format(cmd)])
                except Exception:
                    pass
        return HttpResponseRedirect('/control/bios')
    elif state == "run":
        cmd = ''
        msg = req.POST.get('msg')
        info = req.POST.get('info')
        if info and msg:
            info = json.loads(info)
            msg = json.loads(msg)
            for each in msg:
                for i in info:
                    Salt.cmd('{}'.format(each['ip']), 'cmd.run', ['{}'.format(cmd)])
                    print each['ip'], i
    return HttpResponse()