# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.


class Host(models.Model):
    id = models.AutoField(primary_key=True)
    sn = models.CharField(max_length=250)
    sn_1 = models.CharField(max_length=250)
    name = models.CharField(max_length=250)
    name1 = models.CharField(max_length=250)
    family = models.CharField(max_length=250)
    status = models.CharField(max_length=550)
    time = models.DateTimeField()
    boot_time = models.CharField(max_length=250)
    cpu = models.CharField(max_length=250)
    memory = models.CharField(max_length=250)
    disk = models.CharField(max_length=550)
    raid = models.CharField(max_length=550)
    network = models.CharField(max_length=550)
    mac = models.CharField(max_length=550)
    mac_addr = models.CharField(max_length=550)
    ip = models.CharField(max_length=550, blank=True)
    bios = models.CharField(max_length=250)
    bmc = models.CharField(max_length=250)
    sel = models.TextField()
    stress_test = models.CharField(max_length=250)
    hostname = models.CharField(max_length=250)
    disk_num = models.IntegerField()
    message = models.TextField()
    fru = models.TextField()
    smart_info = models.TextField(blank=True)
    enclosure = models.FileField('breakin', blank=True)
    change_stat = models.CharField(max_length=255, blank=True, default="-", null=True)
    cmd_stat = models.CharField(max_length=255, blank=True, default="-", null=True)

    class Meta:
        verbose_name_plural = u'老化测试系统'
        verbose_name = u'服务器信息'

    def __unicode__(self):
        return self.sn


KIND_CHOICES = (
    ('run', 'run'),
    ('stop', 'stop'),
    ('poweroff', 'poweroff'),
    ('bmcLogClear', 'bmcLogClear'),
)


class Stat(models.Model):
    ip = models.GenericIPAddressField()
    sn = models.CharField(max_length=150, default='no date')
    status = models.CharField(max_length=50, choices=KIND_CHOICES, default='wait')
    cpu = models.CharField(max_length=150)
    mem = models.CharField(max_length=150)
    num = models.CharField(max_length=150)
    hostname = models.CharField(max_length=150)

    def __unicode__(self):
        return "%s(%s)" % (self.status, self.hostname)
