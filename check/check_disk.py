#!/usr/bin/python
# _*_encoding:utf-8_*_
"""
# @TIME:2018/11/28 11:06
# @FILE:check_disk.py
# @Author:ytym00
"""
import json
import os
import time
from subprocess import Popen, PIPE


def printGreen(msg):
    print('\033[1;32;47m{}\033[0m'.format(msg))


def printRed(msg):
    print('\033[1;31;47m{}\033[0m'.format(msg))


class CheckDiskMsg(object):
    def __init__(self):
        self.sn = self.getSerialNumber()
        self.path = self.getPath()

    def checkMsg(self):
        green, red = [], []
        with open('{}/pdp_output.json'.format(self.path), 'r') as fd:
            file_msg = fd.read()
        file_json = json.loads(file_msg)
        id_dict = {5: 0, 197: 0, 198: 0, 199: 0}
        for each in file_json['PdpOutPut']['summary']:
            if each. has_key("codes"):
                error = 0
                for code in each["codes"]:
                    if code["severity"] == "failure":
                        error += 1
                        red.append(
                            "{} {} {} [serial:({}) error:({})]".format(each["blockDevice"], "'pdp check'",
                                                                       code['severity'], each['serial'],
                                                                       code["description"]))
                if error == 0:
                    green.append("{} {}".format(each["blockDevice"], "'pdp check' pass"))
            else:
                green.append("{} {}".format(each["blockDevice"], "'pdp check' pass"))
            for j in each['smart']["attribute"]:
                for id in id_dict.keys():
                    if j['id'] == id:
                        if j['raw'] != id_dict[id]:
                            red.append(
                                "{} {} {} [raw:({})serial:({})]".format(each["blockDevice"], id, "fail", j['raw'],
                                                                        each['serial']))
                        else:
                            green.append("{} {} {}".format(each["blockDevice"], id, "pass"))
        print
        for each in red:
            printRed(each)
        for each in green:
            printGreen(each)

    def checkInventory(self):
        with open("{}/inventory.json".format(self.path), 'r') as fd:
            inven_msg = json.loads(fd.read())
        disk_list = []
        for each in inven_msg['PdpOutPut']['summary']:
            if each["manufacturer"] == "HGST a Western Digital Company":
                disk_list.append(each['model'])
        return list(set(disk_list))

    def getSerialNumber(self):
        msg = Popen(r"dmidecode -t 1 | awk /'Serial Numbe'/'{print $3}'", stdout=PIPE, stderr=PIPE, shell=True)
        SN = msg.stdout.read().strip()
        return SN

    def getPath(self):
        path = os.path.join('/opt', self.sn)
        return path

    def runInventory(self):
        cmd = '/usr/bin/pdp /opt/wdc/pdp/configurations/inventory.json --outfile inventory.json -o {}'.format(self.path)
        os.popen(cmd)

    def runCheckMsg(self):
        model = self.checkInventory()
        if model:
            if len(model) == 1:
                cmd = '/usr/bin/pdp --model {0} /opt/wdc/pdp/configurations/standard/standardSequence.json  -o {1} --zip'.format(
                    model[0], self.path)
                os.popen(cmd)
                self.checkMsg()
            else:
                for each in model:
                    cmd = '/usr/bin/pdp --model {0} /opt/wdc/pdp/configurations/standard/standardSequence.json  -o {1} --zip'.format(
                        each, self.path)
                    os.popen(cmd)
                    self.checkMsg()

    def main(self):
        self.runInventory()
        self.checkInventory()
        self.runCheckMsg()


if __name__ == '__main__':
    check = CheckDiskMsg()
    check.main()
