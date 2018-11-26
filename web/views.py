# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from control.models import *
# Create your views here.



@login_required
def userLog(req):
    usermsg = UserExecMsg.objects.all()
    total_num = usermsg.count()
    return render(req, "userLog.html", {"usermsg": usermsg, "total_num": total_num})