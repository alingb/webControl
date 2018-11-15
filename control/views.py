# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import time

from django.contrib.auth.decorators import login_required

from saltstack import SaltApi
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from web.models import *


# Create your views here.




@login_required
def index(req):
    totalNum = Host.objects.count()
    runNum = Host.objects.filter(stress_test="running").count()
    stopNum = Host.objects.filter(Q(stress_test="reload")).count()
    offNum = Host.objects.filter(status__contains="erro").count()
    return render(req, 'index.html', {'totalNum': totalNum, 'runNum': runNum, 'offNum': offNum, "stopNum": stopNum})


@login_required
def serverDetail(req):
    global name, status
    name = req.GET.get("name")
    status = req.GET.get("status")
    return render(req, 'serverdetail.html')


@login_required
def bios(req):
    Bios = {1: "D51B-2U",
            2: "T41S-2U",
            3: "ASR1100",
            4: "RS300-E9-PS4",
            5: "RS720Q-E8",
            6: "ESC8000G3",
            7: "Z10PA-D8",
            8: "K880G3",
            9: "N880G2",
            10: "SR205-2"
            }
    return render(req, 'bios.html', {"bios": Bios})


@login_required
def execute(req):
    return render(req, 'execute.html')


@login_required
def serverInfo(request):
    global name, status
    limit = request.GET.get("limit")
    offset = request.GET.get("offset")
    search = request.GET.get("search")
    state = request.GET.get("state")
    sort = request.GET.get("sort")
    sortOrder = request.GET.get("sortOrder")
    host = ''
    try:
        if name and status:
            if name == "run":
                host = Host.objects.filter(stress_test=status)
            elif name == "error":
                host = Host.objects.filter(status__contains=status)
            name, status = '', ''
    except Exception:
        pass
    if not host:
        host = Host.objects.all()
    if state:
        host = host.filter(stress_test=state)
    if search:
        host = host.filter(Q(sn__contains=search) |
                           Q(sn_1__contains=search) |
                           Q(name1__contains=search) |
                           Q(name__contains=search) |
                           Q(family__contains=search) |
                           Q(status__contains=search) |
                           Q(ip__contains=search))
    lenth = host.count()
    if sort and sortOrder:
        if sortOrder == "asc":
            host = host.order_by("{}".format(sort))
        elif sortOrder == "desc":
            host = host.order_by("-{}".format(sort))
    if offset and limit:
        offset = int(offset)
        limit = int(limit)
        host = host[offset:offset + limit]
    data = []
    for each in host:
        data.append(model_to_dict(each, fields=['id', 'sn', 'sn_1', 'name', 'name1', 'family',
                                                'status', 'bios', 'bmc', 'ip', 'stress_test']))
    return HttpResponse(json.dumps({"rows": data, "total": lenth}))


@login_required
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
        msg = req.POST.get('msg')
        fru_name = req.POST.get('fru_name')
        num = 0
        if msg:
            msg = json.loads(msg)
            if len(msg) != len(sn):
                return HttpResponseBadRequest()
            for each in msg:
                print each['ip'], sn[num].strip()
                cmd = 'echo "{}" | /fru/{}/FRU_lnx64.sh'.format(sn[num].strip(), fru_name)
                num += 1
                print cmd
                try:
                    Salt.cmd('{}'.format(each['ip']), 'cmd.run', ['{}'.format(cmd)])
                except Exception:
                    pass
        return HttpResponseRedirect('/control/bios')
    elif state == "run":
        msg = req.POST.get('msg')
        info = req.POST.get('info')
        if info and msg:
            info = json.loads(info)
            msg = json.loads(msg)
            for each in msg:
                for i in info:
                    Salt.cmd('{}'.format(each['ip']), 'service.start', ['{}'.format(i.lower())])
                    print each['ip'], i
    return HttpResponse()


@login_required
def infoPaser(req):
    val = str(req.POST.get('val'))
    if val:
        if val.isdigit():
            val = int(val)
    name_list = {
        1: ["SunMnet-M3", "UDS1022"],
        2: ["UDS2000-C", "UDS2000-E", "zhongdianfufu"],
        3: ['ELOG', 'RCP', 'RCP1.0', 'meidian'],
        4: ['RG-RCM1000-Office', 'RG-RCM1000-Smart', 'RG-RCM1000-Edu'],
        5: ['RG-ONC-AIO-CTL'],
        6: ['RG-RCD16000Pro-3D'],
        7: ['tianrongxin'],
        8: ['RG-RCD6000-Main', 'RG-RCD6000-Office', 'RG-iData-Server', 'RG-RACC 5000', 'RG-RCD3000-Office', 'RG-RCD6000E V3', 'haiyunjiexun'],
        9: ['Meidian'],
        10: ['DT-G2-U211', 'CZ-2U-K888G4'],
    }
    return HttpResponse(json.dumps(name_list[val]))
