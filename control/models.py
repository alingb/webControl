# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class UserExecMsg(models.Model):
    username = models.CharField(max_length=255, default='-')
    addTime = models.CharField(max_length=255, default='-')
    msg = models.CharField(max_length=255, default='-')