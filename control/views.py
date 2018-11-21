# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import datetime
import json
import time

from django.contrib.auth.decorators import login_required
from django.core.files import File

from saltstack import SaltApi
from django.db.models import Q
from django.forms import model_to_dict
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
from django.shortcuts import render
from web.models import *
from .models import *


# Create your views here.




@login_required
def index(req):
    if req.method == "POST":
        info = json.loads(req.body)
        ip = info['ip']
        try:
            stat = Stat.objects.get(ip=ip)
        except Exception:
            stat = Stat()
        stat.status = info['status']
        stat.ip = info['ip']
        stat.sn = info['sn']
        stat.cpu = info['cpu']
        stat.mem = info['mem']
        stat.hostname = info['hostname']
        stat.save()
        return HttpResponse()
    else:
        totalNum = Host.objects.exclude(stress_test__contains="OS off").count()
        runNum = Host.objects.filter(stress_test="running").count()
        stopNum = Host.objects.filter(Q(stress_test="reload")).count()
        offNum = Host.objects.filter(status__contains="erro").count()
        form = Stat.objects.all()
        count = form.count()
        form = form.order_by('-status', 'hostname')
        a = 1
        for i in form:
            b = i
            b.num = a
            a += 1
            b.save()
        num = []
        for i in form:
            if 'OS off' in i.status:
                num.append(i.status[:-6])
            else:
                num.append(i.status)
        dic = {}
        data = set(num)
        for i in data:
            dic[i] = num.count(i)
        strs = ""
        for k, v in dic.items():
            strs += '"%s"(%s)___' % (k, v)
        return render(req, 'index.html', {'totalNum': totalNum, 'runNum': runNum, 'offNum': offNum, "stopNum": stopNum,
                                          'form': form, 'count': count, 'dic': strs})


@login_required
def serverDetail(req):
    global name, status
    name = req.GET.get("name")
    status = req.GET.get("status")
    return render(req, 'serverdetail.html')


@login_required
def bios(req):
    Bios = {1: "D51B",
            2: "T41S-2U",
            3: "ASR1100",
            4: "RS100-E9-PI2",
            5: "RS300-E9-PS4",
            6: "RS720Q-E8",
            7: "ESC8000G3",
            8: "P10S-M-DC",
            9: "Z10PA-D8",
            10: "K880G3",
            11: "N880G2",
            12: "SR205-2"
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
        data.append(
            model_to_dict(each, fields=['id', 'sn', 'sn_1', 'name', 'name1', 'family', 'change_stat', 'cmd_stat',
                                        'status', 'bios', 'bmc', 'ip', 'stress_test']))
    return HttpResponse(json.dumps({"rows": data, "total": lenth}))


def msgSave(username, msg):
    userexec = UserExecMsg()
    now_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    userexec.username = username
    userexec.addTime = now_time
    userexec.msg = msg
    userexec.save()


def checkStat(Salt, each, cmd, info, username, name, name1):
    msg = "对设备号(SN:{0},SN_1:{1})进行刷{2}操作，{2}的选择为(机器名称:{3} 产品名称:{4})".format(each['sn'], each['sn_1'], info, name, name1)
    msgSave(username, msg)
    try:
        host = Host.objects.get(sn=each['sn'], sn_1=each['sn_1'])
    except Exception:
        return HttpResponseBadRequest()
    host.change_stat = "{}指令下发中……".format(info)
    host.save()
    Salt.cmd('{}'.format(each['ip']), 'cmd.run', [cmd])
    time.sleep(5)
    cmd1 = 'ps aux | grep {}_lnx64 | grep -v grep'.format(info)
    data = Salt.cmd('{}'.format(each['ip']), 'cmd.run', [cmd1])
    msg = data['ip']
    if msg:
        host.change_stat = "{}指令执行中……".format(info)
        host.save()
    else:
        host.change_stat = "{}指令执行失败".format(info)
        msg = "机器名称为:{},产品名称为:{}的设备刷新{}版本失败".format(name, name1, info)
        msgSave(username, msg)
        host.save()
        exit()
    while 1:
        data = Salt.cmd('{}'.format(each['ip']), 'cmd.run', [cmd])
        msg = data[each['ip']]
        if msg:
            host.change_stat = "{}客制化完成".format(info)
            host.save()
            msg = "机器名称为:{},产品名称为:{}的设备刷新{}版本成功".format(name, name1, info)
            msgSave(username, msg)
            break
        else:
            time.sleep(10)
            continue

@login_required
def control(req):
    username = req.user.username
    salt_api = "https://127.0.0.1:8000/"
    Salt = SaltApi(salt_api)
    state = req.POST.get('state')
    name = req.POST.get('name')
    name1 = req.POST.get('name1')
    file = req.FILES.get('fru_sn')
    if state == "bios":
        cmd = '/control/{}/BIOS_lnx64.sh {}'.format(name, name1)
        msg = req.POST.get('msg')
        if msg:
            msg = json.loads(msg)
            for each in msg:
                checkStat(Salt, each, cmd, 'BIOS', username, name, name1)
    elif state == "bmc":
        cmd = '/control/{}/BMC_lnx64.sh {}'.format(name, name1)
        msg = req.POST.get('msg')
        if msg:
            msg = json.loads(msg)
            for each in msg:
                checkStat(Salt, each, cmd, 'BMC', username, name, name1)
    elif file:
        sn = file.readlines()
        msg = req.POST.get('msg')
        fru_name = req.POST.get('fru_name')
        fru_p_name = req.POST.get('fru_p_name')
        num = 0
        if msg:
            msg = json.loads(msg)
            if len(msg) != len(sn):
                return HttpResponseBadRequest()
            for each in msg:
                print each['ip'], sn[num].strip()
                cmd = 'echo "{}" | /control/{}/FRU_lnx64.sh {}'.format(sn[num].strip(), fru_p_name, fru_name)
                num += 1
                try:
                    checkStat(Salt, each, cmd, 'FRU', username, name, name1)
                except Exception:
                    pass
        return HttpResponseRedirect('/control/bios')
    elif state == "run":
        print req.user.username
        msg = req.POST.get('msg')
        info = req.POST.get('info')
        if info and msg:
            info = json.loads(info)
            msg = json.loads(msg)
            for each in msg:
                for i in info:
                    try:
                        host = Host.objects.get(sn=each['sn'], sn_1=each['sn_1'])
                    except Exception:
                        return HttpResponseBadRequest()
                    host.cmd_stat = "指令下发中……"
                    host.save()
                    Salt.cmd('{}'.format(each['ip']), 'service.start', ['trusme-{}'.format(i.lower())])
                    host.cmd_stat = "指令执行中……"
                    host.save()
                    time.sleep(1)
                    msg = "设备名称为sn:{},sn_1:{}执行{}操作".format(each['sn'], each['sn_1'], i)
                    msgSave(username, msg)
                    while 1:
                        data = Salt.cmd('{}'.format(each['ip']), 'service.status', ['trusme-{}'.format(i.lower())])
                        msg = data[each['ip']]
                        if msg:
                            host.cmd_stat = "运行成功"
                            host.save()
                            msg = "设备名称为sn:{},sn_1:{}执行{}操作成功".format(each['sn'], each['sn_1'], i)
                            msgSave(username, msg)
                            break
                        else:
                            time.sleep(10)
                            continue
    return HttpResponse()


@login_required
def infoPaser(req):
    val = str(req.POST.get('val'))
    if val:
        if val.isdigit():
            val = int(val)
    name_list = {
        "D51B": ["SunMnet-M3", "UDS1022-G"],
        "T41S-2U": ["UDS2000-C", "UDS2000-E", "zhongdianfufu"],
        "ASR1100": ['RG-eLog', 'RCP', 'meidian'],
        "RS100-E9-PI2": ['RG-RCP1.0'],
        "RS300-E9-PS4": ['RG-RCM1000-Office', 'RG-RCM1000-Smart', 'RG-RCM1000-Edu'],
        "RS720Q-E8": ['RG-ONC-AIO-CTL'],
        "ESC8000G3": ['RG-RCD16000Pro-3D'],
        "P10S-M-DC": ['P10S-M-DC'],
        "Z10PA-D8": ['tianrongxin'],
        "K880G3": ['RG-RCD6000-Main', 'RG-RCD6000-Office', 'RG-iData-Server', 'RG-RACC5000', 'RG-RCD3000-Office', 'RG-RCD6000EV3', 'haiyunjiexun'],
        "N880G2": ['Meidian'],
        "SR205-2": ['DT-G2-U211', 'CZ-2U-K888G4'],
    }
    return HttpResponse(json.dumps(name_list[val]))


def controlDeatil(req, ID):
    form = Host.objects.get(id=ID)
    message = form.message
    dic = {}
    import re
    ALL_LIST = []
    for i in message.split('\n'):
        re_info = re.findall(r'(^[A-Z]{1,8}[\s_]*[A-Z1-9]*):', i, re.M)
        if re_info:
            ALL_LIST.append(re_info[0])
    for i in xrange(len(ALL_LIST)):
        try:
            info = message.split(ALL_LIST[i+1])[0].strip()
            split_info = ALL_LIST[i] +  ':'
            try:
                data = info.split(split_info)[1].strip()
            except:
                data = ''
            dic[ALL_LIST[i].replace(' ', '_')] = data.strip()
        except:
            info = message.split(ALL_LIST[i])[0]
            dic[ALL_LIST[i].replace(' ', '_')] = info.split(':')[1]
    return render(req, 'detail.html', {'form': dic, 'all': form})


@login_required()
def msgParsePost(req):
    if req.method == "POST":
        info = json.loads(req.body)
        sn = info['sn']
        sn_1 = info['sn_1']
        try:
            host = Host.objects.get(sn=sn, sn_1=sn_1)
        except Exception:
            host = Host()
        host.sn = info['sn']
        host.sn_1 = info['sn_1']
        host.status = info['status']
        host.time = info['time']
        host.boot_time = info['boot_time']
        host.name = info['name']
        host.name1 = info['name1']
        host.family = info['family']
        host.cpu = info['cpu']
        host.memory = info['memory']
        host.disk = info['disk']
        host.disk_num = info['disk_num']
        host.hostname = info['hostname']
        host.stress_test = info['stress_test']
        host.network = info['network']
        host.mac = info['mac']
        host.mac_addr = info['mac_addr']
        host.raid = info['raid']
        host.bios = info['bios']
        host.bmc = info['bmc']
        host.message = info['message']
        host.sel = info['sel']
        host.fru = info['fru']
        if len(info['ip'].strip().split('.')) == 4:
            host.ip = info['ip']
        if info['smart_info']:
            host.smart_info = info['smart_info']
        try:
            host.enclosure = File(info['enclosure'])
        except Exception:
            pass
        host.save()
    return HttpResponse('ok')

