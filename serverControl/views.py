# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from control.views import msgSave

# Create your views here.
from django.urls import reverse


def login_user(request):
    redirect_to = request.GET.get('next', '')
    if request.method == 'POST':
        username = request.POST.get("username")
        passwd = request.POST.get("passwd")
        check = request.POST.get("check")
        next = request.GET.get("next")
        user = authenticate(username=username, password=passwd)
        if user:
            if user.is_active:
                if user.is_staff:
                    login(request, user)
                    if check:
                        request.session.set_expiry(None)
                    else:
                        request.session.set_expiry(0)
                    if next:
                        msgSave(username, "登入成功")
                        return HttpResponseRedirect(next)
                    else:
                        msgSave(username, "登入成功")
                        return redirect(reverse('index'))
                else:
                    if username != "admin":
                        msgSave(username, "没有登入权限")
                        return render(request, 'login.html', {'error': u'用户没有登入权限!'})
            else:
                msgSave(username, "用户未激活")
                return render(request, 'login.html', {'error': u'用户没有激活!'})
        else:
            msgSave(username, "登入失败")
            return render(request, 'login.html', {'error': u'用户名或密码错误!'})
    return render(request, 'login.html', {'redirect_to': redirect_to})


def logout_user(req):
    logout(req)
    return redirect(reverse('login'))


def changepw(request):
    if request.method == "GET":
        return render(request, 'changepasswd.html')
    elif request.method == "POST":
        username = request.user.username
        oldpasswd = request.POST.get('oldpasswd', None)
        password = request.POST.get('password', None)
        rpassword = request.POST.get('rpassword', None)
        if oldpasswd == password:
            return render(request, 'changepasswd.html', {"error": u"新密码不能和旧密码一致"})
        if rpassword != password:
            return render(request, 'changepasswd.html', {"error": u"两次密码输入不一样"})
        user = authenticate(username=username, password=oldpasswd)
        if user:
            if user.is_active:
                user.set_password(password)
                user.save()
                return redirect(reverse('login'))
            else:
                return render(request, 'changepasswd.html', {"error": u"用户权限不够"})
        else:
            return render(request, 'changepasswd.html', {"error": u"密码错误"})
