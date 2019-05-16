# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import random

import datetime
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from control.models import *
from web.models import *
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseBadRequest
import json


# Create your views here.


@login_required
def userLog(req):
    usermsg = UserExecMsg.objects.all()
    total_num = usermsg.count()
    return render(req, "userLog.html", {"usermsg": usermsg, "total_num": total_num})


def status(req):
    if req.method == "POST":
        info = json.loads(req.body)
        sn = info['sn']
        ip = info['ip']
        try:
            stat = Stat.objects.get(ip=ip)
        except:
            stat = Stat()
        stat.status = info['status']
        stat.ip = info['ip']
        stat.sn = info['sn']
        stat.cpu = info['cpu']
        stat.mem = info['mem']
        stat.hostname = info['hostname']
        stat.save()
        return HttpResponse('ok')
    else:
        return HttpResponse('yes')


def realTimeStatus(req):
    return render(req, "realTimeStatus.html")


def dataSource(req):
    return render(req, "dataSource.html")


def envirmentData(req):
    return render(req, "envirmentData.html")


def dataSourceRequest(req):
    time = datetime.datetime.now().strftime("%H:%M")
    host = Stat.objects.values("cpu", "mem", "sn")
    if host:
        result = 1
    else:
        result = 0
    cpu, memory_presure, machine_name, net_usage = [], [], [], []
    for info in host:
        cpu.append(info["cpu"])
        memory_presure.append(info["mem"].replace("%", ""))
        machine_name.append(eval(info["sn"])[0])
    if cpu:
        for i in xrange(len(cpu)):
            net_usage.append(random.randint(1, 99))
    cpu_pressure = 0
    for info1 in cpu:
        cpu_pressure += float(info1.replace("%", ""))
    cpu_pressure = cpu_pressure / len(cpu)
    realTimeStatus = {"result": result,
                      "data": {"cpu_pressure": "{:.2f}".format(cpu_pressure),
                               "machine_detail": {"memory_presure": memory_presure,
                                                  "machine_name": machine_name, "net_usage": net_usage}}, "time": time}
    return HttpResponse(json.dumps(realTimeStatus))


def realTimeStatusRequest(req):
    time = datetime.datetime.now().strftime("%H:%M")
    is_testing = Stat.objects.filter(status="run").count()
    wait_test = Stat.objects.filter(status="wait").count()
    if is_testing or wait_test:
        result = 1
    else:
        result = 0
    dataSourceRequest = {"result": result,
                         "data": {"machine_detail": {"is_testing": is_testing, "wait_test": wait_test}}, "time": time}
    return HttpResponse(json.dumps(dataSourceRequest))


def envirmentDataRequest(req):
    date_time = datetime.datetime.now()
    time = date_time.strftime("%H:%M")
    data_list = []
    for num in xrange(12):
        d1 = date_time - datetime.timedelta(hours=num)
        time = d1.hour
        tmp = random.randint(1, 100)
        tem = random.randint(1, 100)
        data_list.append([tmp, tem, time])
    envirmentDataRequest = {"result": 1, "data": {"machine_detail": {"data_list": data_list}}, "time": time}
    return HttpResponse(json.dumps(envirmentDataRequest))
