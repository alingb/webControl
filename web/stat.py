#!/usr/bin/python
# _*_encoding:utf-8_*_
"""
# @TIME:2018/11/19 15:54
# @FILE:stat.py
# @Author:ytym00
"""
import re
from subprocess import Popen, PIPE
import requests
import json
import time
import MySQLdb


def sn():
    cmd = '/usr/sbin/dmidecode'
    info = Popen(cmd, stdout=PIPE, stderr=PIPE, shell=True)
    info = info.stdout.read()
    n = 0
    dmi_info = ''
    for i in info.split('\n'):
        if i.startswith('SMBIOS'):
            n += 1
        if n < 2:
            dmi_info += i + "\n"
    if n > 1:
        info = dmi_info
    sn_info = re.findall(r'Serial Number:\s+(.*)\s*', info, re.M)

    if len(sn_info[:2]) == 2:
        sn = sn_info[0].strip()
        sn_1 = sn_info[1].strip()
    else:
        sn = sn_info[0].strip()
        sn_1 = ''

    return {'sn': str([sn, sn_1]), 'sn_1': str(sn_1.strip()).strip()}


def ip():
    info = Popen(['/sbin/ifconfig'], stdout=PIPE, stderr=PIPE, shell=True)
    info = info.stdout.read().split('\n\n')
    if not info:
        info = Popen(['/usr/sbin/ifconfig'], stdout=PIPE, stderr=PIPE, shell=True)
        info = info.stdout.read().split('\n\n')
    info = '\n'.join([i for i in info if i and not i.startswith('lo') and not i.startswith('vir')])
    ip_gen = re.compile(r'inet addr:(172.16.\d.\d{1,3})', re.M)
    ip = ip_gen.search(info)
    if ip:
        ip = str(ip.group(1))
    else:
        ip_gen = re.compile(r'inet\s(172.16.\d.\d{1,3})', re.M)
        ip = str(ip_gen.search(info).group(1))
    return {'ip': ip}


def info():
    with open('/proc/stat') as fd:
        info = fd.readline().split()[1:]
    return info


def getInfo():
    data = info()
    total = 0
    for i in data:
        total += long(i)
    return total, long(data[3])


def mem():
    global total_mem, free_mem
    with open('/proc/meminfo') as fd:
        info = fd.readlines()
    for i in info:
        if i.startswith('MemTotal:'):
            total_mem = long(i.split()[1])
            continue
        if i.startswith('MemFree:'):
            free_mem = long(i.split()[1])
            continue
    mem = float(total_mem - free_mem) / total_mem * 100
    return {'mem': '%.2f%%' % mem}


def cpu():
    total, ide = getInfo()
    time.sleep(2)
    total1, ide1 = getInfo()
    total_a = total1 - total
    ide_a = ide1 - ide
    cpu = float(total_a - ide_a) / total_a * 100
    cpu = '%.2f%%' % cpu
    return {'cpu': cpu}


def hostName():
    info = Popen('hostname', stdout=PIPE, stderr=PIPE, shell=True)
    hostname = info.stdout.read().strip()
    return {'hostname': hostname}


def stat():
    k, v = sn().items()[0]
    con = MySQLdb.Connect("192.168.1.57", "trusme", "6286280300", "cmdb")
    cur = con.cursor()
    cur.execute('select * from cmdb.web_stat')
    data = cur.fetchall()
    status = ''
    for i in data:
        if v in str(i):
            status = i[3]
    if status:
        if 'OS off' not in status:
            status = status
        else:
            status = 'reload'
    else:
        status = 'wait'
    return {'status': status}


def main(data):
    url = "http://172.16.1.1/login/"
    UA = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36"
    header = {"User-Agent": UA,}
    session = requests.Session()
    postData = {'username': 'admin',
                'passwd': 'trusme123',
                }
    session.post(url,
                 data=postData,
                 headers=header)
    session.post('http://172.16.1.1/', data=data, headers=header)


if __name__ == '__main__':
    dic = {}
    dic.update(sn())
    dic.update(ip())
    dic.update(cpu())
    dic.update(mem())
    dic.update(stat())
    dic.update(hostName())
    info = json.dumps(dic)
    main(info)
