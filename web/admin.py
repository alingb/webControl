# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import *
# Register your models here.

from django.utils.html import format_html_join
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from django.http import StreamingHttpResponse
from django.forms import ModelForm
from django import forms

# Register your models here.
import datetime
import time
import sys
import xlwt
import MySQLdb
import re

reload(sys)
sys.setdefaultencoding('utf8')


def save_errors(self, request, queryset):
    def mysqlQuer(id_num, project):
        conn = MySQLdb.connect('127.0.0.1', 'admin', 'admin', 'cmdb', charset='utf8')
        cursor = conn.cursor()
        count = cursor.execute('select %s from web_host where %s' % (project, id_num))
        cursor.scroll(0, mode='absolute')
        global results
        results = cursor.fetchall()

        return results

    id_num = ''
    for q in queryset:
        id_num += 'id="%s" or ' % q.id
    if id_num:
        id_num = id_num[:-3]

    quer_num = len(queryset)

    cpu = list(set(mysqlQuer(id_num, 'cpu')))
    disk_detail = ''
    disk = list(set(mysqlQuer(id_num, 'disk')))[0]
    for disk_pcs in eval(disk[0]).items():
        k, v = disk_pcs
        disk_detail += k + '(%s)' % v + '\n'
    raid = list(set(mysqlQuer(id_num, 'raid')))[0]
    sn = mysqlQuer(id_num, 'sn')
    name = list(set(mysqlQuer(id_num, 'name')))[0]
    network = list(set(mysqlQuer(id_num, 'network')))[0]
    network_detail = ''
    for network_pcs in eval(network[0]).items():
        k, v = network_pcs
        network_detail += k + '(%s)' % v + '\n'
    #  memory = list(set(mysqlQuer(id_num, 'memory')))[0]
    message = str(mysqlQuer(id_num, 'message')[0][0])
    memory = re.search(r'.*MHz.*', message, re.M)
    memory_num = len(re.findall(r'.*MHz.*', message))
    if memory:
        memory = memory.group(0).split('||')[2:]
        if len(memory) == 4:
            memory_detail = u'内存容量：%s \n内存数量：%s\n内存频率：%s \n设置频率：%s \n内存品牌：%s' % (
                memory[0],
                memory_num,
                memory[1],
                memory[2],
                memory[3])
        else:
            memory_detail = ''
    else:
        memory_detail = ''

    if len(cpu) == 1:
        cpu = cpu[0]
        import xlrd
        import xlwt
        from xlutils.copy import copy
        def set_style(name, height, bold=False):
            style = xlwt.XFStyle()  # 初始化样式

            font = xlwt.Font()  # 为样式创建字体
            font.name = name  # 'Times New Roman'
            font.bold = bold
            font.color_index = 4
            font.height = height

            borders = xlwt.Borders()
            borders.left = 1
            borders.right = 1
            borders.top = 1
            borders.bottom = 1

            alignment = xlwt.Alignment()
            alignment.horz = xlwt.Alignment.HORZ_JUSTIFIED
            # alignment.vert = xlwt.Alignment.VERT_JUSTIFIED

            style.alignment = alignment

            style.font = font
            style.borders = borders

            # style.borders = borders
            return style

        oldWb = xlrd.open_workbook(r'/data/oqc.xls', formatting_info=True)
        newWb = copy(oldWb)

        sheet = newWb.get_sheet(0)
        sheet.write(4, 1, quer_num, set_style(u'宋体', 240))
        sheet.write(6, 1, quer_num, set_style(u'宋体', 240))
        sheet.write(3, 6, name, set_style(u'宋体', 240))
        sheet.write(22, 3, cpu, set_style(u'宋体', 240))
        sheet.write(23, 3, memory_detail, set_style(u'宋体', 240))
        sheet.write(24, 3, disk_detail.strip(), set_style(u'宋体', 240))
        sheet.write(25, 3, raid, set_style(u'宋体', 240))
        sheet.write(26, 3, network_detail.strip(), set_style(u'宋体', 240))
        j = 1
        k = 7
        if 41 > len(sn) > 0:
            for i in xrange(0, len(sn)):
                sheet.write(k, j, sn[i], set_style(u'宋体', 240))
                j += 2
                if j > 8:
                    k += 1
                    j = 1

        newWb.save('/data/media/new.xls')
    else:
        import os
        if os.path.exists('/data/media/new.xls'):
            with open('/data/media/new.xls', 'w') as fd:
                fd.write(u'选择的服务器配置不一致')

    def file_iterator(file_name, chunk_size=512):
        with open(file_name) as f:
            while True:
                c = f.read(chunk_size)
                if c:
                    yield c
                else:
                    break

    the_file_name = "/data/media/new.xls"
    response = StreamingHttpResponse(file_iterator(the_file_name))
    response['Content-Type'] = 'application/octet-stream'
    response['Content-Disposition'] = 'attachment;filename="{0}"'.format('RG_reporot.xls')
    self.message_user(request, "%s haved download" % quer_num)
    return response


save_errors.short_description = u"报告下载"


def update(self, request, queryset):
    num = len(queryset)
    erro_num = 0
    msg = []
    for q in queryset:
        if q.stress_test != 'running':
            msg.append('erro')
            erro_num += 1
    if len(msg) > 0:
        self.message_user(request, u"共选择了%s台设备，其中%s台不在运行状态" % (num, erro_num))
    else:
        import os
        from django.shortcuts import render
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return render(request, os.path.join(PROJECT_ROOT, 'web/templates', 'sn.html'), {'form': queryset})


update.short_description = u'关机时间设定'


class HostAdmin(admin.ModelAdmin):
    actions = [save_errors, update]
    list_display = [
        'get_log',
        'get_account_state',
        'get_stat',
        'sn',
        'hostname',
        'sn_1',
        'get_dmp',
        'get_img',
        'family',
        'bios',
        'bmc',
        'get_power_status',
    ]

    list_filter = ('status', 'time', 'name', 'family', 'stress_test',)
    search_fields = ('status', 'hostname', 'time', 'sn', 'sn_1', 'name', 'family', 'stress_test')
    date_hierarchy = 'time'
    list_per_page = 50
    list_display_links = ('sn',)
    actions_on_top = True
    fields = ('message', 'sel', 'smart_info',)

    #    list_select_related = True
    #    def changelist_view(self, request, extra_context=None):
    #        user = request.user
    #        if user.is_superuser:
    #            list_display_links = ('status',)
    #            self.fieldsets = (['Main',{
    #            'fields':('status',
    #                      'sn',
    #                      'sn_1',
    #                      'ip',
    #                      'time',
    #                      'name',
    #                      'family',
    #                      'cpu',
    #                      'memory',
    #                      'disk_num',
    #                      'bios',
    #                      'bmc',
    #                      'raid',
    #                      'disk',
    #                      'mac',
    #                      'network',
    #                      'fru',
    #                      'name1',
    #                      'mac_addr',
    #                      'boot_time',
    #                      'sel',
    #                      'message',
    #                      'smart_info',
    #                      'stress_test',
    #                      'enclosure'),
    #                         }],
    #                   )
    #        else:
    #            self.fieldsets = (
    #                ['message',{
    #                 'fields':('message',),
    #                 }],
    #                ['sel imformations',{
    #                 'classes':('collapse',),
    #                 'fields':('sel', 'smart_info', ),
    #                        }],
    #                ['change', {
    #                 'classes':('collapse',),
    #                 'fields':(('stress_test','status', 'boot_time'), 'enclosure',),
    #                }],
    #                )
    #        return super(HostAdmin, self).changelist_view(request, extra_context=None)

    def save_model(self, request, obj, form, change):
        if change:
            obj_old = self.model.objects.get(pk=obj.pk)
        else:
            obj_old = None
        obj.user = request.user
        if request.user.is_superuser:
            obj.save()

    def get_account_state(self, obj):
        if 'OS off' in obj.stress_test:
            return u'<a href=/technology/web/Host/detail/%s>\
                   <span style="color:gray;font-weight:bold">%s</span></a>' % (obj.id, obj.stress_test)
        elif obj.stress_test == 'running':
            return u'<a href=/technology/web/Host/detail/%s>\
                  <span style="color:green;font-weight:bold">%s %s</span></a>' % (
            obj.id, obj.stress_test, obj.boot_time)
        else:
            return u'<a href=/technology/web/Host/detail/%s>\
                <span style="color:#6C3365;font-weight:bold">%s %s</span></a>' % (
            obj.id, obj.stress_test, obj.boot_time)

    get_account_state.short_description = u'run_stat'
    get_account_state.allow_tags = True

    def get_test(self, obj):
        return u'<span style="color:red;font-weight:bold"> sdc_write_speed lower</span></a>'

    get_test.short_description = u'压力测试'
    get_test.allow_tags = True

    def get_img(self, obj):
        sn = obj.sn
        sn_1 = obj.sn_1
        name1 = obj.name1
        import os
        from django.core.files import File
        if os.path.exists('/data/ftp/breakin/breakin-img/%s-1.png' % sn):
            return u'<a href=/file/%s-1.png>%s</a>' % (sn, name1)
        elif os.path.exists('/data/ftp/breakin/breakin-img/%s-1.png' % sn_1):
            return u'<a href=/file/%s-1.png>%s</a>' % (sn_1, name1)
        else:
            return name1

    get_img.short_description = u'name1'
    get_img.allow_tags = True

    def get_dmp(self, obj):
        sn = obj.sn
        sn_1 = obj.sn_1
        name = obj.name
        import os
        from django.core.files import File
        if os.path.exists('/data/ftp/breakin/breakin-img/%s.dmp' % sn):
            return u'<a href=/file/%s.dmp>%s</a>' % (sn, name)
        elif os.path.exists('/data/ftp/breakin/breakin-img/%s.dmp' % sn_1):
            return u'<a href=/file/%s.dmp>%s</a>' % (sn_1, name)
        else:
            return name

    get_dmp.short_description = u'name'
    get_dmp.allow_tags = True

    def get_stat(self, obj):
        if obj.status == 'pass':
            return u'<span style="color:green;font-weight:bold">{}</span></a>'.format(obj.status)
        elif obj.status == 'complete':
            return u'<span style="color:gray;font-weight:bold">{}</span></a>'.format(obj.status)
        elif obj.status == 'no check data':
            return u'<span style="color:#444444;font-weight:bold">{}</span></a>'.format(obj.status)
        else:
            return u'<span style="color:red;font-weight:bold">{}</span></a>'.format(obj.status)

    get_stat.short_description = u'status'
    get_stat.allow_tags = True

    def get_log(self, obj):
        id = obj.id
        sn = obj.sn
        message = obj.message
        sel = obj.sel
        import os
        if os.path.exists('/data/ftp/breakin/breakin-img/%s-%s.dmp' % (sn, id)):
            with open('/data/ftp/breakin/breakin-img/%s-%s.dmp' % (sn, id), 'w') as fd:
                for i in message.split('\n'):
                    info = i + '\r\n'
                    fd.write(info)
                fd.write('\r\n')
                fd.write('SelLog:' + '\r\n')
                for i in sel.split('\n'):
                    info = i + '\r\n'
                    fd.write(info)
            return u'<a href=/file/%s-%s.dmp>%s</a>' % (sn, id, id)
        else:
            return id

    get_log.short_description = u'id'
    get_log.allow_tags = True

    def get_power_status(self, obj):
        msg = obj.message
        import re
        power = re.search(r'POWER:(.*)', msg, re.M)
        off_time = re.search(r'TIME:\n(.*)', msg, re.M)
        if off_time:
            off = off_time.group(1).strip()
        else:
            off = ''
        if power:
            power = power.group(1)
            power = power.strip()
        else:
            power = ''
        if 'OS off' in obj.stress_test:
            return u'<span style="color:gray;font-weight:bold">off</span>'
        else:
            if power == 'SET':
                return u'<span style="color:green;font-weight:bold">%s</span>' % power
            elif power == 'UNSET':
                return u'<span style="color:red;font-weight:bold">%s</span>' % power
            else:
                return u'<span style="color:green;font-weight:bold">%s</span>' % power

    get_power_status.short_description = u'off_time'
    get_power_status.allow_tags = True


def update(self, request, queryset):
    num = len(queryset)
    erro_num = 0
    msg = []
    for q in queryset:
        if q.stress_test != 'running':
            msg.append('erro')
            erro_num += 1
    if len(msg) > 0:
        self.message_user(request, u"共选择了%s台设备，其中%s台不在运行状态" % (num, erro_num))
    else:
        import os
        from django.shortcuts import render
        PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return render(request, os.path.join(PROJECT_ROOT, 'web/templates', 'sn.html'), {'form': queryset})


update.short_description = u'关机时间设定'


class HostCheckAdmin(admin.ModelAdmin):
    actions = [update]
    list_display = [
        'id',
        'get_account_state',
        'get_stat',
        'sn',
        'hostname',
        'sn_1',
        'name',
        'name1',
        'family',
        'bios',
        'bmc',
        'get_power_status',
    ]

    list_filter = ('status', 'time', 'name', 'family', 'stress_test',)
    search_fields = ('status', 'hostname', 'time', 'sn', 'sn_1', 'name', 'family',)
    list_per_page = 50
    ordering = ['id']
    list_display_links = None
    fieldsets = (
        ['message', {
            'fields': ('message',),
        }],
        ['sel imformations', {
            'classes': ('collapse',),
            'fields': ('sel', 'smart_info'),
        }],
    )
    list_select_related = True

    def save_model(self, request, obj, form, change):
        if change:
            obj_old = self.model.objects.get(pk=obj.pk)
        else:
            obj_old = None
        obj.user = request.user
        if request.user.is_superuser:
            obj.save()

    def get_account_state(self, obj):
        if 'OS off' in obj.stress_test:
            return u'<a href=/technology/web/HostCheck/detail/%s> \
                   <span style="color:gray;font-weight:bold">%s</span></a>' % (obj.id, obj.stress_test)
        elif obj.stress_test == 'running':
            return u'<a href=/technology/web/HostCheck/detail/%s> \
                  <span style="color:green;font-weight:bold">%s %s</span></a>' % (
            obj.id, obj.stress_test, obj.boot_time)
        else:
            return u'<a href=/technology/web/HostCheck/detail/%s> \
                <span style="color:#6C3365;font-weight:bold">%s %s</span></a>' % (
            obj.id, obj.stress_test, obj.boot_time)

    get_account_state.short_description = u'run_stat'
    get_account_state.allow_tags = True

    def get_stat(self, obj):
        if obj.status == 'pass':
            return u'<span style="color:green;font-weight:bold">{}</span></a>'.format(obj.status)
        elif obj.status == 'complete':
            return u'<span style="color:gray;font-weight:bold">{}</span></a>'.format(obj.status)
        elif obj.status == 'no check data':
            return u'<span style="color:#444444;font-weight:bold">{}</span></a>'.format(obj.status)
        else:
            return u'<span style="color:red;font-weight:bold">{}</span></a>'.format(obj.status)

    get_stat.short_description = u'status'
    get_stat.allow_tags = True

    def get_power_status(self, obj):
        msg = obj.message
        import re
        power = re.search(r'POWER:(.*)', msg, re.M)
        off_time = re.search(r'TIME:\n(.*)', msg, re.M)
        if off_time:
            off = off_time.group(1).strip()
        else:
            off = ''
        if power:
            power = power.group(1)
            power = power.strip()
        else:
            power = ''
        if 'OS off' in obj.stress_test:
            return u'<span style="color:gray;font-weight:bold">off</span>'
        else:
            if power == 'SET':
                return u'<span style="color:green;font-weight:bold">%s</span>' % power
            elif power == 'UNSET':
                return u'<span style="color:red;font-weight:bold">%s</span>' % power
            else:
                return u'<span style="color:green;font-weight:bold">%s</span>' % power

    get_power_status.short_description = u'off_time'
    get_power_status.allow_tags = True


class StatAdmin(admin.ModelAdmin):
    list_display = [
        'sn',
        'ip',
        'status',
        'cpu',
        'mem',
        'hostname',
    ]


class SmartAdmin(admin.ModelAdmin):
    list_display = [
        'sn',
        'get_smart',
        'explain',
        'sn_1',
        'time',
    ]
    search_fields = ('sn', 'sn_1',)
    list_filter = ('sn', 'sn_1',)

    def get_smart(self, obj):
        return u'<a href=/smart/%s>%s</a>' % (obj.id, obj.sn)

    get_smart.short_description = u'sn'
    get_smart.allow_tags = True


# class ProductAdmin(admin.ModelAdmin):
#    list_select_related = True
#    filter_horizontal = ('orders',)
#    list_display = [
#		"name",
#	]

admin.site.register(Stat, StatAdmin)
admin.site.register(Host, HostAdmin)
admin.site.register(HostCheck, HostCheckAdmin)
admin.site.register(Smart, SmartAdmin)
# admin.site.register(Product, ProductAdmin)
