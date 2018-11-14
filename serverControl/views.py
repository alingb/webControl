# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect


# Create your views here.
from django.urls import reverse


def login_user(request):
    redirect_to = request.GET.get('next', '')
    if request.method == 'POST':
        username = request.POST.get("username")
        passwd = request.POST.get("passwd")
        check = request.POST.get("check")
        next = request.GET.get("next")
        print next
        user = authenticate(username=username, password=passwd)
        if user:
            login(request, user)
            if check:
                request.session.set_expiry(None)
            else:
                request.session.set_expiry(0)
            if next:
                return HttpResponseRedirect(next)
            else:
                return redirect(reverse('index'))
        else:
            return render(request, 'login.html', {'error': u'用户名或密码错误!'})
    return render(request, 'login.html', {'redirect_to': redirect_to})


def logout_user(req):
    logout(req)
    return redirect(reverse('login'))


def signup(request):
    if request.method == "GET":
        return render(request, 'signup.html')
    elif request.method == "POST":
        username = request.POST.get('username', None)
        password = request.POST.get('password', None)
        rpassword = request.POST.get('checkpassword', None)
        try:
            User.objects.get(username=username)
            return render(request, 'signup.html', {"error": u'用户已注册!'})
        except:
            pass
        if rpassword != password:
            return render(request, 'signup.html', {"error": u"两次密码输入不一样"})
        if not check_password(password):
            return render(request, 'signup.html', {"error": u"password  is invalid"})
        passwd = make_password(password)
        User.objects.create(username=username,
                            password=passwd,
                            is_active=True,
                            is_staff=True)
        return redirect(reverse('login'))