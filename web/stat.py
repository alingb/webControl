#!/usr/bin/python
# _*_encoding:utf-8_*_
"""
# @TIME:2018/11/19 15:54
# @FILE:runStat.py
# @Author:ytym00
"""
import re
from subprocess import Popen, PIPE, STDOUT
import requests
import json
import time
import MySQLdb


def execCommand(cmd, timeout=1):
    info = Popen(cmd, stdout=PIPE, stderr=STDOUT, shell=True)
    t_start = time.time()
    while 1:
        if info.poll() is not None:
            break
        seconds = time.time() - t_start
        if timeout and seconds > timeout:
            info.terminate()
            return ''
        time.sleep(0.1)
    info = info.stdout.read()
    if "SMBIOS" in info:
        msg, count = '', 0
        for i in info.strip().split('\n'):
            if i.startswith('SMBIOS'):
                count += 1
            if count < 2:
                msg += "{}\n".format(i)
        if count > 1:
            info = msg
        return info.strip()
    else:
        return info


def productSN():
    cmd = '/usr/sbin/dmidecode'
    info = execCommand(cmd)
    sn_info = re.findall(r'Serial Number:\s+(.*)\s*', info, re.M)
    if len(sn_info[:2]) == 2:
        sn = sn_info[0].strip()
        sn_1 = sn_info[1].strip()
    else:
        sn = sn_info[0].strip()
        sn_1 = ''
    return {'sn': str([sn, sn_1]), 'sn_1': str(sn_1.strip()).strip()}


def serverIP():
    cmd = '/sbin/ifconfig'
    info = execCommand(cmd).split('\n\n')
    if not info:
        cmd = '/usr/sbin/ifconfig'
        info = execCommand(cmd).split('\n\n')
    info = '\n'.join([i for i in info if i and not i.startswith('lo') and not i.startswith('vir')])
    ip_gen = re.compile(r'inet addr:(172.16.\d.\d{1,3})', re.M)
    ip = ip_gen.search(info)
    if ip:
        ip = str(ip.group(1))
    else:
        ip_gen = re.compile(r'inet\s(172.16.\d.\d{1,3})', re.M)
        ip = str(ip_gen.search(info).group(1))
    return {'ip': ip}


def cpuInfo():
    with open('/proc/stat') as fd:
        info = fd.readline().split()[1:]
    return info


def getInfo():
    data = cpuInfo()
    total = 0
    for i in data:
        total += long(i)
    return total, long(data[3])


def productMemInfo():
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


def productCpuInfo():
    total, ide = getInfo()
    time.sleep(2)
    total1, ide1 = getInfo()
    total_a = total1 - total
    ide_a = ide1 - ide
    cpu = float(total_a - ide_a) / total_a * 100
    cpu = '%.2f%%' % cpu
    return {'cpu': cpu}


def hostName():
    cmd = 'hostname'
    hostname = execCommand(cmd).strip()
    return {'hostname': hostname}


def runStat():
    k, v = productSN().items()[0]
    con = MySQLdb.Connect("172.16.1.1", "root", "123456", "cmdb")
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
    header = {"User-Agent": UA}
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
    dic.update(productSN())
    dic.update(serverIP())
    dic.update(productCpuInfo())
    dic.update(productMemInfo())
    dic.update(runStat())
    dic.update(hostName())
    info = json.dumps(dic)
    main(info)
