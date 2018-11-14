#!/usr/bin/python
# _*_encoding:utf-8_*_
"""
# @TIME:2018/8/17 13:39
# @FILE:saltstack.py
# @Author:ytym00
"""

import json

import requests

try:
    import cookielib
except:
    import http.cookiejar as cookielib
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


salt_api = "https://127.0.0.1:8000/"


class SaltApi:
    def __init__(self, url):
        self.url = url
        self.username = "salt-api"
        self.password = "salt-api"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36",
            "Content-type": "application/json"
            # "Content-type": "application/x-yaml"
        }
        self.params = {'client': 'local', 'fun': '', 'tgt': ''}
        # self.params = {'client': 'local', 'fun': '', 'tgt': '', 'arg': ''}
        self.login_url = salt_api + "login"
        self.login_params = {'username': self.username, 'password': self.password, 'eauth': 'pam'}
        self.token = self.get_data(self.login_url, self.login_params)['token']
        self.headers['X-Auth-Token'] = self.token

    def get_data(self, url, params):
        send_data = json.dumps(params)
        request = requests.post(url, data=send_data, headers=self.headers, verify=False )
        response = request.json()
        result = dict(response)
        return result['return'][0]

    def cmd(self, tgt, method, arg=None):
        """远程执行命令，相当于salt 'client1' cmd.run 'free -m'"""
        if arg:
            params = {'client': 'local', 'fun': method, 'tgt': tgt, 'arg': arg}
        else:
            params = {'client': 'local', 'fun': method, 'tgt': tgt}
        # print '命令参数: ', params
        result = self.get_data(self.url, params)
        return result

    def salt_async_command(self, tgt, method, arg=None):  # 异步执行salt命令，根据jid查看执行结果
        """远程异步执行命令"""
        if arg:
            params = {'client': 'local_async', 'fun': method, 'tgt': tgt, 'arg': arg}
        else:
            params = {'client': 'local_async', 'fun': method, 'tgt': tgt}
        jid = self.get_data(self.url, params)['jid']
        return jid

    def look_jid(self, jid):  # 根据异步执行命令返回的jid查看事件结果
        params = {'client': 'runner', 'fun': 'jobs.lookup_jid', 'jid': jid}
        print params
        result = self.get_data(self.url, params)
        return result


if __name__ == '__main__':
    print '=================='
    print '同步执行命令'
    salt = SaltApi(salt_api)
    print salt.token
    salt_client = '*'
    salt_test = 'test.ping'
    result1 = salt.cmd(salt_client, salt_test)
    for i in result1.keys():
        print i, ': ', result1[i]
