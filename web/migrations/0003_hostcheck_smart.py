# -*- coding: utf-8 -*-
# Generated by Django 1.11.16 on 2019-03-23 00:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0002_auto_20181121_1748'),
    ]

    operations = [
        migrations.CreateModel(
            name='HostCheck',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('sn', models.CharField(max_length=250)),
                ('sn_1', models.CharField(max_length=250)),
                ('name', models.CharField(max_length=250)),
                ('name1', models.CharField(max_length=250)),
                ('family', models.CharField(max_length=250)),
                ('status', models.CharField(max_length=550)),
                ('time', models.DateTimeField()),
                ('boot_time', models.CharField(max_length=250)),
                ('cpu', models.CharField(max_length=250)),
                ('memory', models.CharField(max_length=250)),
                ('disk', models.CharField(max_length=550)),
                ('raid', models.CharField(max_length=550)),
                ('network', models.CharField(max_length=550)),
                ('mac', models.CharField(max_length=550)),
                ('mac_addr', models.CharField(max_length=550)),
                ('bios', models.CharField(max_length=250)),
                ('bmc', models.CharField(max_length=250)),
                ('sel', models.TextField()),
                ('stress_test', models.CharField(max_length=250)),
                ('hostname', models.CharField(max_length=250)),
                ('disk_num', models.IntegerField()),
                ('message', models.TextField()),
                ('fru', models.TextField()),
                ('smart_info', models.TextField(blank=True)),
                ('enclosure', models.FileField(blank=True, upload_to=b'')),
            ],
            options={
                'verbose_name': '\u670d\u52a1\u5668\u4fe1\u606f',
                'verbose_name_plural': '\u8fd1\u671f\u670d\u52a1\u5668\u4fe1\u606f',
            },
        ),
        migrations.CreateModel(
            name='Smart',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sn', models.CharField(max_length=250, verbose_name='sn')),
                ('sn_1', models.CharField(max_length=250, verbose_name='sn_1')),
                ('sel', models.TextField(verbose_name='BMC\u65e5\u5fd7')),
                ('smart_info', models.TextField(verbose_name='\u6570\u636e')),
                ('time', models.CharField(blank=True, max_length=150, verbose_name='\u65f6\u95f4')),
                ('explain', models.CharField(blank=True, max_length=550, verbose_name='\u8bf4\u660e')),
            ],
        ),
    ]
