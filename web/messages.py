#!/usr/bin/python
# _*_encoding:utf-8_*_
"""
# @TIME:2018/11/19 16:03
# @FILE:messages.py
# @Author:ytym00
"""

import datetime
import json
import os
import re
import time
from optparse import OptionParser
from subprocess import Popen, PIPE, STDOUT
import MySQLdb
import threading
import requests


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


# noinspection PyBroadException
def connMysql(cmd):
    try:
        con = MySQLdb.connect('172.16.1.1', 'root', '123456', 'cmdb')
    except:
        return ''
    cur = con.cursor()
    cur.execute(cmd)
    data = cur.fetchall()
    con.close()
    cur.close()
    return data


def memLocator():
    cmd = '/usr/sbin/dmidecode -t 17'
    info = execCommand(cmd)
    all_mem = re.findall(r'\t+Size:\s+(.*)', info, re.M)
    locate_mem = re.findall(r'\t+Locator:\s+(.*)', info, re.M)
    lo_mem = re.findall(r'\t+Bank Locator:\s+(.*)', info, re.M)
    mem_speed = re.findall(r'\t+Speed:\s+(.*)', info, re.M)
    mem_conf = re.findall(r'\t+Configured Clock Speed:\s+(.*)', info, re.M)
    mem_man = re.findall(r'\t+Manufacturer:\s+(.*)', info, re.M)
    count = 0
    mem_locate, mem_locate1 = '', ''
    for i in locate_mem:
        mem_locate += "%s\t||\t%s\t||\t%s\t||\t%s\t||\t%s\t||\t%s\n" % (
            lo_mem[count], i, all_mem[count], mem_speed[count], mem_conf[count], mem_man[count])
        if 'No' not in all_mem[count]:
            mem_locate1 += "%s\t %s\n" % (lo_mem[count], i,)
        count += 1
    return mem_locate.strip(), mem_locate1.strip()


class CollectMessage(object):
    def __init__(self):
        self.get_message = dict()

    def cpuMessage(self):
        cmd = 'dmidecode -t 4'
        info = execCommand(cmd)
        cpu_info = re.findall(r'\sVersion:(.*CPU.*)', info, re.M)
        cpu_num = len(cpu_info)
        if 'CPU @' in str(cpu_info):
            try:
                cpu = [i for i in set(cpu_info) if i][0].split('Xeon(R)')[1].strip()
            except:
                cpu = [i for i in set(cpu_info) if i][0].split('Core(TM)')[1].strip()
        else:
            cpu = [i for i in set(cpu_info) if i][0].split('CPU')[1].strip()
        self.get_message.update({"cpu_data": cpu, "cpu_num": cpu_num, "cpu": "%s  (%s)" % (cpu, cpu_num)})
        return {"cpu_data": cpu, "cpu_num": cpu_num, "cpu": "%s  (%s)" % (cpu, cpu_num)}

    def memoryMessage(self):
        cmd = 'dmidecode -t 17'
        info = execCommand(cmd)
        size = re.compile(r'Size:[\s]+([\d]+[\s]+[a-zA-Z]{1,2})', re.M)
        mz = re.compile(r'\t+Speed:\s+([\d]+\s+MHz)', re.M)
        mem_mz = set(mz.findall(info)).pop()
        mem_size = set(size.findall(info)).pop()
        mem_num = len(size.findall(info))
        self.get_message.update({'mem_size': mem_size, 'mem_mz': mem_mz, 'mem_num': mem_num,
                                 'memory': "{0}  ({1})".format(mem_size, mem_num)})
        return {'mem_size': mem_size, 'mem_mz': mem_mz, 'mem_num': mem_num,
                'memory': "{0}  ({1})".format(mem_size, mem_num)}

    # noinspection PyBroadException
    @staticmethod
    def _raidMessage():
        cmd = '/opt/MegaRAID/MegaCli/MegaCli64 -cfgdsply -aall'
        try:
            info = execCommand(cmd)
            raid = re.search(r'Product Name: (.*)', info)
            if raid:
                raid = raid.group(1).split()
            else:
                raid = ''
            raid_id = [i.split(':')[1].strip() for i in info.split('\n') if i.startswith('Device Id:')]
            raid = "{0} {1}".format(raid[0], raid[-1])
        except:
            cmd = "lspci | grep SAS | awk -F : '{print $3}' | awk -F [ '{print $1}'"
            raid = execCommand(cmd)
            raid_id = ''
        return raid, raid_id

    def _diskMessage(self):
        cmd = '/usr/bin/lsscsi|egrep -iv "SanDisk|enclosu|Virtual|scsi" | grep disk'
        disk_info = execCommand(cmd)
        disk_name = re.findall(r'/dev/sd.*', disk_info, re.M)
        msg, ssd_fw = [], {}
        for i in disk_name:
            cmd = '/usr/sbin/smartctl -i %s' % i
            info = execCommand(cmd)
            if 'INTEL' in info:
                for b in info.split('\n'):
                    if b.startswith('Firmware Version:'):
                        intel_ssd_fw = b.split()[-1][-4:]
                        ssd_fw[i] = intel_ssd_fw
        for i in disk_name:
            cmd = '/usr/sbin/smartctl -i %s' % i
            info = execCommand(cmd)
            for a in info.split('\n'):
                if a.startswith('Device Model'):
                    msg.append(a.split(':')[1].strip())
                elif a.startswith('Product'):
                    msg.append(a.split(':')[1].strip())
        disk_dict = {}
        for disk in set(msg):
            if 'Ultra' not in disk:
                num = msg.count(disk)
                disk_dict[disk] = num
        disk_num = sum(disk_dict.values())
        # self.get_message.update({'disk': disk_dict, 'disk_num': disk_num, 'locate_disk': info})
        return {'ssd_fw':ssd_fw, 'disk': disk_dict, 'disk_num': disk_num, 'locate_disk': disk_info}

    def raidDiskMessage(self):
        raid, raid_id = self._raidMessage()
        diskmessage = self._diskMessage()
        disk_dict = diskmessage['disk']
        if raid:
            cmd = '/opt/MegaRAID/MegaCli/MegaCli64 -pdlist -aall'
            info = execCommand(cmd)
            raid_size = re.findall(r'Raw Size:\s+([\d.]+\s[A-Z]{2})', info, re.M)
            raid_data = re.findall(r'Inquiry Data:\s+(.*)', info, re.M)
            raid_num = re.findall(r'Slot (Number: [\d]+)', info, re.M)
            raid_type = re.findall(r'PD (Type: [A-Z]+)', info, re.M)
            raid_data = [i.split() for i in raid_data if i]
            disk_locate, t, disk_other = '', 0, []
            for i in raid_data:
                disk_locate += '{}    {}    {}    {} {}\n'.format(raid_num[t], raid_type[t], raid_size[t], i[0][8:],
                                                                  i[1])
                t += 1
            disk_locate += diskmessage['locate_disk']
            for i in raid_data:
                if len(i[0]) < 8:
                    disk_other.append(i[1])
                else:
                    disk_other.append(i[0][8:])
            for i in disk_other:
                n = 0
                for j in set(disk_other):
                    if i == j:
                        n += 1
                    disk_dict.update({i: n})
            raid_disk_num = sum(disk_dict.values()) + int(diskmessage['disk_num'])
        else:
            disk_locate = diskmessage['locate_disk']
            raid_disk_num = diskmessage['disk_num']
        self.get_message.update(
                {'ssd_fw':diskmessage['ssd_fw'], 'disk': disk_dict, 'raid': raid, 'disk_num': raid_disk_num, 'locate_disk': disk_locate})
        return {'ssd_fw':diskmessage['ssd_fw'], 'disk': disk_dict, 'raid': raid, 'disk_num': raid_disk_num, 'locate_disk': disk_locate}

    def smartMessage(self):
        cmd = 'ls /dev/ | grep ^sd | grep -v [0-9]'
        info = execCommand(cmd).split()
        msg = ''
        for i in info:
            cmd = 'smartctl -i /dev/{0}'.format(i)
            cmd1 = 'smartctl -A /dev/{0}'.format(i)
            smart_name = execCommand(cmd)
            smart_data = execCommand(cmd1).split('\n\n')[1].strip()
            smart_data = [j for j in smart_data.split('\n') if '/dev/{0}'.format(i) not in smart_data]
            for name in smart_name.split('\n'):
                if name.startswith('=== START'):
                    msg += 'POSITION:{}\n'.format(i)
                for k, v in {'Device Model': 'MODEL', 'Serial Number': 'DISK SN',
                             'User Capacity': 'DISK SIZE','Firmware Version': 'Firmware Version'}.iteritems():
                    if name.startswith(k):
                        msg += '{0}:{1}\n'.format(v, name.split(':')[1].strip())
            if msg:
                for data in smart_data:
                    msg += '{0}\n'.format(data.strip())
                msg += '\n'
        if not msg:
            cmd = 'lsblk'
            msg = execCommand(cmd)
        self.get_message.update({"smart_info": msg})
        return {"smart_info": msg}

    def smartRaidMessage(self):
        raid, raid_id = self._raidMessage()
        msg = ''
        if raid_id:
            for i in sorted(raid_id):
                cmd = 'smartctl -i -d megaraid,{0} /dev/sda '.format(i)
                cmd1 = 'smartctl -A -d megaraid,{0} /dev/sda '.format(i)
                smart_raid_info = execCommand(cmd).split('\n')
                smart_raid_data = execCommand(cmd1).split('\n\n')[1].strip()
                smart_raid_data = ["{0}\n".format(i) for i in smart_raid_data.strip('\n') if
                                   '/dev' not in smart_raid_data]
                if not smart_raid_data:
                    cmd = 'smartctl -i -d sat+megaraid,{0} /dev/sda '.format(i)
                    cmd1 = 'smartctl -A -d sat+megaraid,{0} /dev/sda '.format(i)
                    smart_raid_info = execCommand(cmd).split('\n')
                    smart_raid_data = execCommand(cmd1).split('\n\n')[1].strip()
                    smart_raid_data = [i for i in smart_raid_data.strip('\n') if
                                       '/dev' not in smart_raid_data]
                for j in smart_raid_info:
                    if j.startswith('Device Model'):
                        msg += 'POSITION: {}\nmodel: {}\n'.format(i, j.split(':')[1].strip())
                    if j.startswith('Serial Number'):
                        msg += 'DISK SN: {}\n'.format(j.split(':')[1].strip())
                    if j.startswith('User Capacity'):
                        msg += 'DISK SIZE: {}\n'.format(j.split('[')[1][:-1])
                if msg:
                    for k in smart_raid_data:
                        msg += '\n{0}\n\n'.format(k)
        self.get_message.update({'smart_raid_info': msg})
        return {'smart_raid_info': msg}

    def macMessage(self):
        cmd = "ifconfig"
        info = execCommand(cmd)
        ip_adder = re.search(r'inet addr:(172.16.1.\d{1,3})', info, re.M)
        if ip_adder:
            ip_adder = str(ip_adder.group(1))
        else:
            ip_adder = re.search(r'inet\s(172.16.1.\d{1,3})', info, re.M)
            if ip_adder:
                ip_adder = str(ip_adder.group(1))
            else:
                ip_adder = ''
        msg = [i for i in info.split('\n') if
               i and not i.startswith('virbr') and not i.startswith('ib0') and not i.startswith('lo')]
        eth_list = [i.split()[0] for i in msg if i[0].strip() and not i.strip()[0].startswith('ib0')
                    and not i.split()[0].startswith('lo') and not i.split()[0].startswith('virbr')]
        mac_msg, mac_dic = '', {}
        for i in info.split('\n\n'):
            if not i.startswith('virbr') and not i.startswith('lo'):
                mac_msg += i
        mac_adder = re.findall(r'HWaddr\s([\da-fA-Z:]{17})', mac_msg, re.M)
        if not mac_adder:
            mac_adder = re.findall(r'ether\s([\da-fA-Z:]{17})', mac_msg, re.M)
        for i in range(len(eth_list)):
            mac_dic[eth_list[i]] = mac_adder[i]
        self.get_message.update({'mac': mac_dic, 'mac_addr': mac_adder, 'ip': ip_adder})
        return {'mac': mac_dic, 'mac_addr': mac_adder, 'ip': ip_adder}

    def networkMessage(self):
        cmd = '/sbin/lspci -v'
        info = execCommand(cmd)
        ether = re.findall(r'Ethernet controller:\s+(.*)', info, re.M)
        ether_list = [' '.join(i.split()[2:-2]) for i in ether if i]
        network = {}
        for i in set(ether_list):
            n = 0
            for j in ether_list:
                if i == j:
                    n += 1
            network[i] = n
        self.get_message.update({'network': network})
        return {'network': network}

    def productSnMessage(self):
        cmd = '/usr/sbin/dmidecode'
        info = execCommand(cmd)
        sn_info = re.findall(r'Serial Number:\s+(.*)', info, re.M)
        if len(sn_info[:2]) == 2:
            sn = sn_info[0]
            sn_1 = sn_info[1]
        else:
            sn = sn_info[0]
            sn_1 = ''
        self.get_message.update({'sn': str(sn.strip()), 'sn_1': str(sn_1.strip())})
        return {'sn': str(sn.strip()), 'sn_1': str(sn_1.strip())}

    def timeMessage(self):
        time = datetime.datetime.now()
        time = time.strftime('%Y-%m-%d %H:%M')
        self.get_message.update({'time': time})
        return {'time': time}

    def productNameMessage(self):
        cmd = '/usr/sbin/dmidecode'
        info = execCommand(cmd)
        product_name = re.findall(r'Product Name:\s+(.*)', info, re.M)
        if len(product_name) == 2:
            name = product_name[0]
            name1 = product_name[1]
        else:
            name = product_name[0]
            name1 = ''
        self.get_message.update({'name': name.strip(), 'name1': name1.strip()})
        return {'name': name.strip(), 'name1': name1.strip()}

    def produceFamilyMessage(self):
        cmd = '/usr/sbin/dmidecode'
        info = execCommand(cmd)
        family = re.search(r'Family:(.*)', info, re.M)
        if family:
            family = family.group(1).strip()
        else:
            family = ''
        self.get_message.update({'family': family})
        return {'family': family}

    def produceBiosMessage(self):
        cmd = '/usr/sbin/dmidecode -t bios'
        info = execCommand(cmd)
        bios = re.search(r'Version:\s+(.*)', info, re.M)
        if bios:
            bios = bios.group(1).strip()
        else:
            bios = ''
        self.get_message.update({'bios': bios})
        return {'bios': bios}

    def bmcMessage(self):
        cmd = '/usr/bin/ipmitool mc info'
        try:
            info = execCommand(cmd)
            bmc = re.search(r'Firmware Revision\s+:\s+(.*)', info, re.M)
        except OSError:
            bmc = ''
        if bmc:
            bmc = bmc.group(1)
        else:
            bmc = ''
        self.get_message.update({'bmc': bmc})
        return {'bmc': bmc}

    def fruMessage(self):
        cmd = '/usr/bin/ipmitool fru'
        info = execCommand(cmd)
        fru_info = ''
        if info:
            for msg in info.split('\n'):
                if msg:
                    if 'Date' not in msg:
                        if len(msg.split(' : ')) == 2:
                            msgKey, msgValues = msg.split(' : ')
                            if msgValues.strip() == 'N/A' or not msgValues.strip():
                                pass
                            else:
                                fru_info += '{} : {}\n'.format(msgKey, msgValues)
                    else:
                        fru_info += msg + '\n'
            fru_version = re.search(r'Product Version\s*:\s(.*)', fru_info, re.M)
            if fru_version:
                fru_version = fru_version.group(1).strip()
        else:
            fru_version = ''
            fru_info = ''
        self.get_message.update({"fru": fru_info, 'fru_version': fru_version})
        return {"fru": fru_info, 'fru_version': fru_version}

    def selMessage(self):
        cmd = "/usr/bin/ipmitool sel list"
        info = execCommand(cmd)
        self.get_message.update({'sel': info})
        return {'sel': info}

    def hostnameMessage(self):
        cmd = 'hostname'
        info = execCommand(cmd)
        self.get_message.update({'hostname': info})
        return {'hostname': info}

    def powerMessage(self):
        cmd = 'ps aux | grep shutdown | grep -v grep | wc -l'
        info = int(execCommand(cmd))
        if info == 0:
            power = 'UNSET'
        else:
            if os.path.exists('/root/shutdown.time'):
                with open('/root/shutdown.time') as fd:
                    msg_info = fd.read().split(',')[0].split('for')[1].split()[1:-1]
                    msg = msg_info[0] + ' ' + msg_info[1]
            else:
                msg = 'SET'
            power = msg
        self.get_message.update({"power": power})
        return {'power': power}

    def bootTimeMessage(self):
        cmd = 'date -d "$(awk -F. \'{print $1}\' /proc/uptime) second ago" +"%Y-%m-%d %H:%M"'
        bios_time = execCommand(cmd)
        self.get_message.update({'boot_time': bios_time})
        return {'boot_time': bios_time}

    def biosTimeMessage(self):
        cmd = 'hwclock -r'
        bios_time = execCommand(cmd)
        self.get_message.update({'bios_time': bios_time})
        return {'bios_time': bios_time}

    def pcieMessage(self):
        cmd = 'lspci | grep "[01|02|03]:00" | grep -v ^00'
        pci_info = execCommand(cmd)
        self.get_message.update({"pci_info": pci_info})
        return {"pci_info": pci_info}

    def main(self):
        ret = []
        func_list = {self.cpuMessage, self.memoryMessage, self.raidDiskMessage, self.smartMessage,
                     self.macMessage, self.networkMessage, self.productSnMessage, self.timeMessage,
                     self.productNameMessage, self.produceFamilyMessage, self.produceBiosMessage,
                     self.bmcMessage, self.fruMessage, self.selMessage, self.hostnameMessage, self.powerMessage,
                     self.bootTimeMessage, self.biosTimeMessage, self.pcieMessage}
        for func in func_list:
            woker = threading.Thread(target=func, args=())
            ret.append(woker)
        for rt in ret:
            rt.start()
        for rt in ret:
            rt.join()
        return self.get_message


class CheckMessage(object):
    def __init__(self):
        self.check_info = dict()

    @staticmethod
    def parse(argv):
        cmd = '/bin/lsblk -b'
        info = execCommand(cmd)
        disk = re.compile(r'({0})'.format(argv), re.M)
        data = disk.findall(info)
        return data

    def getDisk(self):
        disk_dict = {'disk_4t': len(self.parse('4000787030016')), 'disk_2t': len(self.parse('2000398934016')),
                     'disk_1t': len(self.parse('1000204886016')), 'ssd_960': len(self.parse('960197124096')),
                     'ssd_240': len(self.parse('240057409536')), 'ssd_128': len(self.parse('128032974848')),
                     'ssd_128_1': len(self.parse('128035676160')), 'ssd_64': len(self.parse('64017212928')),
                     'ssd_600': len(self.parse('600127266816'))}
        self.check_info.update(disk_dict)
        return disk_dict

    def pcieCheckInfo(self):
        pci_info = '''01:00.0 Ethernet controller: Intel Corporation I350 Gigabit Network Connection (rev 01)
01:00.1 Ethernet controller: Intel Corporation I350 Gigabit Network Connection (rev 01)
01:00.2 Ethernet controller: Intel Corporation I350 Gigabit Network Connection (rev 01)
01:00.3 Ethernet controller: Intel Corporation I350 Gigabit Network Connection (rev 01)
02:00.0 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+ Network Connection (rev 01)
02:00.1 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+ Network Connection (rev 01)
03:00.0 Serial Attached SCSI controller: LSI Logic / Symbios Logic SAS3008 PCI-Express Fusion-MPT SAS-3 (rev 02)
'''
        self.check_info.update({'pci_info': pci_info})
        return {'pci_info': pci_info}

    def memLocatorInfo(self):
        RG_RCD6000_Main = """NODE 1	 DIMM_A0
NODE 1	 DIMM_A1
NODE 1	 DIMM_B0
NODE 2	 DIMM_C0
NODE 2	 DIMM_D0
NODE 3	 DIMM_A0
NODE 3	 DIMM_A1
NODE 3	 DIMM_B0
NODE 4	 DIMM_C0
NODE 4	 DIMM_D0"""
        RG_RCD6000_Office = """NODE 1	 DIMM_A0
NODE 1	 DIMM_A1
NODE 1	 DIMM_B0
NODE 2	 DIMM_C0
NODE 2	 DIMM_D0
NODE 3	 DIMM_A0
NODE 3	 DIMM_A1
NODE 3	 DIMM_B0
NODE 4	 DIMM_C0
NODE 4	 DIMM_D0"""
        RG_RCM1000_Edu = """BANK 3	 DIMM_B2"""
        RG_RCM1000_Office = """BANK 3	 DIMM_B2"""
        RG_RCP = """BANK 0	 DIMM_A1"""
        RG_SE04 = """DIMM_A1	 DIMM_A1
DIMM_B1	 DIMM_B1"""
        Elog = """BANK 0	 DIMM_A1"""
        RG_ONC_AIO_E = """NODE 1	 DIMM_A1
NODE 1	 DIMM_B1"""
        UDS1022_G1 = """_Node0_Channel0_Dimm0	 DIMM_A0
_Node0_Channel1_Dimm0	 DIMM_B0
_Node0_Channel2_Dimm0	 DIMM_C0
_Node0_Channel3_Dimm0	 DIMM_D0
_Node1_Channel0_Dimm0	 DIMM_E0
_Node1_Channel1_Dimm0	 DIMM_F0
_Node1_Channel2_Dimm0	 DIMM_G0
_Node1_Channel3_Dimm0	 DIMM_H0"""
        XINWEIH_C612_ASERVER_2400 = """NODE 1	 DIMM_A1
NODE 1	 DIMM_B1
NODE 3	 DIMM_E1
NODE 3	 DIMM_F1"""
        XINWEIH_C612_ASERVER_2405 = """NODE 1	 DIMM_A1
NODE 1	 DIMM_B1
NODE 3	 DIMM_E1
NODE 3	 DIMM_F1"""
        XINWEIH_C612_VDS_8050 = """NODE 1	 DIMM_A1
NODE 1	 DIMM_B1
NODE 2	 DIMM_C1
NODE 2	 DIMM_D1
NODE 3	 DIMM_E1
NODE 3	 DIMM_F1
NODE 4	 DIMM_G1
NODE 4	 DIMM_H1"""
        RG_iData_Server = """NODE 1		DIMM_A0
NODE 1   DIMM_A1
NODE 1   DIMM_B0
NODE 1   DIMM_B1
NODE 2   DIMM_C0
NODE 2   DIMM_C1
NODE 2   DIMM_D0
NODE 2   DIMM_D1
NODE 3   DIMM_A0
NODE 3   DIMM_A1
NODE 3   DIMM_B0
NODE 3   DIMM_B1
NODE 4   DIMM_C0
NODE 4   DIMM_C1
NODE 4   DIMM_D0
NODE 4   DIMM_D1"""
        memory_locate_dic = {'RG-RCD6000-Main': RG_RCD6000_Main, 'RG-RCD6000-Office': RG_RCD6000_Office,
                             'RG-RCM1000-Edu': RG_RCM1000_Edu, 'RG-RCM1000-Office': RG_RCM1000_Office, 'RG-RCP': RG_RCP,
                             'RG-SE04': RG_SE04, 'Elog': Elog, 'RG-ONC-AIO-E': RG_ONC_AIO_E, 'UDS1022-G1': UDS1022_G1,
                             'XINWEIH_C612_ASERVER-2400': XINWEIH_C612_ASERVER_2400,
                             'XINWEIH_C612_ASERVER-2405': XINWEIH_C612_ASERVER_2405,
                             'XINWEIH_C612_VDS-8050': XINWEIH_C612_VDS_8050,
                             'RG_iData_Server': RG_iData_Server}
        self.check_info.update(memory_locate_dic)
        return memory_locate_dic

    def main(self):
        self.memLocatorInfo()
        self.getDisk()
        self.pcieCheckInfo()
        return self.check_info


class CheckDetailMessage(object):
    def __init__(self, msg, name, family):
        self.ret = []
        self.dic = msg
        self.name = name
        self.family = family
        self.check_info = CheckMessage().main()

    @property
    def info(self):
        if self.dic['name'] in self.name or self.dic['family'] in self.family:
            for i in self.name:
                if i == self.dic['name']:
                    return {'status': [{'name': i}]}
            for i in self.family:
                if i == self.dic['family']:
                    return {'status': [{'family': i}]}
        else:
            return {'status': 'no check data'}

    def checkMessage(self, *info):
        if len(info) == 2:
            sql_cmd = "select * from base WHERE {0}=\"{1}\"".format(info[0], info[1])
            data = connMysql(sql_cmd)
        else:
            cmd = "select * from base where name='{}'".format(self.dic['name'])
            data = connMysql(cmd)
            if not data:
                cmd = 'select * from base where family=\'{}\''.format(self.dic['family'])
                data = connMysql(cmd)
        if not data:
            return {'status': 'DB error'}
        elif data:
            data = data[0]
        cpu = data[1]
        cpu_num = int(data[2])
        memory = data[3]
        memory_num = int(data[4])
        disk_num = data[5]
        ssd_num = data[6]
        bios = data[7]
        bmc = data[8]
        speed = data[10]
        mac_num = len(self.dic['mac_addr'])
        if memory:
            if self.dic['mem_size'] != memory or self.dic['mem_num'] != memory_num or self.dic['mem_mz'] != speed:
                self.ret.append('memory fail')
        if cpu:
            if self.dic['cpu_data'] != cpu or self.dic['cpu_num'] != cpu_num:
                self.ret.append('cpu fail')
        if bios:
            if self.dic['bios'] != bios:
                self.ret.append('bios fail')
        if bmc:
            if self.dic['bmc'] != bmc:
                self.ret.append('bmc fail')
        return self.ret, disk_num, ssd_num, mac_num

    def checkPCIE(self):
        pci_info = self.dic['pci_info']
        pci_check_info = self.check_info['pci_info']
        if self.dic['family'] == 'XINWEIH_C612_VDS-8050':
            if pci_info != pci_check_info:
                self.ret.append('PCI-E fail')
                return self.ret

    def checkBreakinLog(self):
        if os.path.exists('/var/log/breakin.log'):
            with open('/var/log/breakin.log', 'r') as fd:
                msg = fd.read()
                for i in msg.split():
                    if i == 'hpl':
                        self.ret.append('breakin-hpl')
                    if i == 'fail':
                        self.ret.append('breakin-fail')
                    if i == 'ecc':
                        self.ret.append('breakin-ecc')
                    if i == 'failid':
                        if 'No IPMI' not in msg:
                            self.ret.append('breakin-failid')
                    if i == 'hdhealth':
                        self.ret.append('breakin-hdhealth')
                    if i == 'mcelog':
                        self.ret.append('breakin-mcelog')
        return self.ret

    def checkSelLog(self):
        sel_log = self.dic['sel'].split()
        error_list = ['ecc', 'temperature', 'processor', 'fan', 'lower', 'high', 'pcie']
        if sel_log:
            for slog in sel_log:
                for j in range(len(error_list)):
                    if error_list[j] == slog.lower():
                        self.ret.append('{0} error'.format(slog))
                        continue
        return self.ret

    def checkMemoryLocator(self):
        mem_locator = memLocator()[1]
        for memory_key, memory_value in self.check_info.items():
            if self.dic['name'] == memory_key:
                if memory_value != mem_locator:
                    self.ret.append('mem locator fail')
                break
            if self.dic['family'] == memory_key:
                if memory_value != mem_locator:
                    self.ret.append('mem locator fail')
                break
        return self.ret

    def checkFru(self):
        if self.dic['name'] == 'UDS1022-G':
            if self.dic['bios'] == 'S2BA3B10':
                if self.dic['fru_version'] != 'V1.10':
                    self.ret.append('fru fail')
        if self.dic['name'] == 'UDS1022-G':
            if self.dic['bios'] == 'S2B_3B10.01':
                if self.dic['fru_version'] != 'V1.00':
                    self.ret.append('fru fail')
        if self.dic['name'] == 'UDS1022-G':
            if self.dic['bios'] == 'S2B_3A22':
                if self.dic['fru_version'] != 'V1.00':
                    self.ret.append('fru fail')
        return self.ret

    def checkSsdFW(self):
        try:
            for name, num in self.dic['ssd_fw'].items():
                if int(num) < 142:
                    self.ret.append('ssd fw fail')
        except Exception,err:
            self.ret.append(err)
        return self.ret

    def checkSmart(self):
        msg = self.dic['smart_info']
        if msg:
            smart_msg = msg.split('\n\n')
            for smart in smart_msg:
                for_msg = smart.split('\n')
                disk_pt = for_msg[0].split(':')
                if len(disk_pt) == 2:
                    disk_pt = disk_pt[1]
                else:
                    disk_pt = disk_pt[0]
                for each in for_msg:
                    data = each.split()
                    if len(data) > 8:
                        for num in [5, 197, 198, 199]:
                            if str(num) == data[0]:
                                if data[-1] != '0':
                                    self.ret.append("{}-{}erro".format(disk_pt, num))
                        if data[0] == "9":
                            if data[-1].isdigit():
                                if int(data[-1]) > 4800:
                                    self.ret.append("{}-{}erro".format(disk_pt, num))

    def checkDisk(self, disk_num, ssd_num, mac_num):
        if self.dic['name'] == 'RG-RCD6000-Main':
            self.checkSsdFW()
            if self.check_info['disk_4t'] != disk_num or self.check_info['ssd_960'] != ssd_num:
                self.ret.append('disk fail')
        elif self.dic['name'] == 'RG-RCD6000-Office':
            self.checkSsdFW()
            if self.check_info['disk_1t'] != disk_num or self.check_info['ssd_960'] != ssd_num:
                self.ret.append('disk fail')
        elif self.dic['name'] == 'RG-RCM1000-Smart' or \
                self.dic['name'] == 'RG-RCM1000-Office' or \
                self.dic['name'] == 'RG-RCM1000-Edu':
            self.checkSsdFW()
            if self.check_info['disk_4t'] != disk_num or self.check_info['ssd_240'] != ssd_num:
                self.ret.append('disk fail')
        elif self.dic['name'] == 'RG-ONC-AIO-E':
            if self.check_info['disk_2t'] != 2:
                self.ret.append('disk fail')
        elif self.dic['name'] == 'UDS1022-G1':
            if self.check_info['disk_4t'] != disk_num or self.check_info['ssd_600'] != ssd_num:
                self.ret.append('disk fail')
        elif self.dic['name'] == 'RG-RCP':
            if self.check_info['disk_2t'] != disk_num:
                self.ret.append('disk fail')
        elif self.dic['name'] == 'Elog':
            if self.check_info['disk_2t'] != disk_num:
                self.ret.append('disk fail')
        elif self.dic['name'] == 'RG-SE04':
            if self.check_info['disk_2t'] != disk_num:
                self.ret.append('disk fail')
        elif self.dic['name'] == 'RG-RCD6000E V3':
            self.checkSsdFW()
            if self.check_info['disk_1t'] != disk_num or self.check_info['ssd_240'] != ssd_num:
                self.ret.append('disk fail')
        elif self.dic['family'] == 'XINWEIH_C612_VDS-5050':
            if self.check_info['ssd_64'] != ssd_num:
                self.ret.append('disk fail')
        elif self.dic['family'] == 'XINWEIH_C612_VDS-6550':
            if self.check_info['ssd_64'] != ssd_num:
                self.ret.append('disk fail')
        elif self.dic['family'] == 'XINWEIH_C612_ASERVER-2400':
            if self.check_info['ssd_128'] != ssd_num:
                self.ret.append('disk fail')
            if mac_num != 8:
                self.ret.append('net card erro')
        elif self.dic['family'] == 'XINWEIH_C612_ASERVER-2405':
            if self.check_info['ssd_128'] != ssd_num and self.check_info['ssd_128_1'] != ssd_num:
                self.ret.append('disk fail')
            if mac_num != 8:
                self.ret.append('net card erro')
        elif self.dic['family'] == 'XINWEIH_C612_VDS-G680':
            if self.check_info['ssd_128'] != ssd_num:
                self.ret.append('disk fail')
            if mac_num != 6:
                self.ret.append('net card erro')
        elif self.dic['family'] == 'XINWEIH_C612_VDS-8050':
            if self.check_info['ssd_64'] != ssd_num:
                self.ret.append('disk fail')
            if mac_num != 8:
                self.ret.append('net card erro')
        return self.ret

    def allCheck(self):
        self.checkSelLog()
        self.checkBreakinLog()
        self.checkFru()
        self.checkPCIE()
        self.checkMemoryLocator()
        self.checkSmart()

    def runCheck(self):
        status = self.info.get('status')
        if isinstance(status, list):
            for status_key, status_values in status[0].items():
                server_msg = self.checkMessage(status_key, status_values)
                try:
                    ret, disk_num, ssd_num, mac_num = server_msg
                    self.checkDisk(disk_num, ssd_num, mac_num)
                except ValueError:
                    return server_msg
        else:
            return {'status': status}
        self.allCheck()
        if len(self.ret) == 0:
            return {'status': 'pass'}
        else:
            return {'status': str(list(set(self.ret)))}


# noinspection PyBroadException
def getNameFamily(sn, sn_1):
    try:
        cmd = 'SELECT * FROM base'
        data = connMysql(cmd)
        name, family = [], []
        for i in data:
            if i[0]:
                name.append(i[0])
            if i[9]:
                family.append(i[9])
        SN = [sn, sn_1]
        cmd = "select * from web_stat where sn=\"{}\"".format(SN)
        stress_test = connMysql(cmd)
        if stress_test:
            stress_test = stress_test[0][3]
        else:
            cmd = "select * from web_stat where sn=\"['{}']\"".format(sn_1)
            stress_test = connMysql(cmd)
            if stress_test:
                stress_test = stress_test[0][3]
            else:
                cmd = "select * from web_stat where sn=\"['{}']\"".format(sn)
                stress_test = connMysql(cmd)
                if stress_test:
                    stress_test = stress_test[0][3]
                else:
                    cmd = "select * from web_stat where sn like \"%{}%\" or sn like \"%{}%\"".format(sn, sn_1)
                    stress_test = connMysql(cmd)[0][3]
    except Exception:
        name = [
            'RG-RCD6000-Main',
            'RG-RCD6000-Office',
            'RG-RCM1000-Smart',
            'RG-RCM1000-Office',
            'RG-RCM1000-Edu',
            'RG-ONC-AIO-E',
        ]
        family = [
            'XINWEIH_C612_VDS-5050',
            'XINWEIH_C612_VDS-6550',
            'XINWEIH_C612_ASERVER-2400',
            'XINWEIH_C612_VDS-G680',
            'XINWEIH_C612_VDS-8050',
            'XINWEIH_C612_ASERVER-2405',
        ]
        stress_test = 'wait'
    return name, family, stress_test


def runMain(msg):
    name, family, stress_test = getNameFamily(msg['sn'], msg['sn_1'])
    checkDetailMessage = CheckDetailMessage(msg, name, family)
    msg.update(checkDetailMessage.runCheck())
    msg.update({'stress_test': stress_test})
    sn = msg['sn']
    sn1 = msg['sn_1']
    name = msg['name']
    family = msg['family']
    status = msg['status']
    cpu = msg['cpu']
    memory = msg['memory']
    disk = msg['disk'].items()
    raid = msg['raid']
    network = msg['network'].items()
    bios = msg['bios']
    bmc = msg['bmc']
    fru = msg['fru']
    boot_time = msg['boot_time']
    bios_time = msg['bios_time']
    time = msg['time']
    mac = msg['mac'].items()
    pci_info = msg['pci_info']
    locate_disk = msg['locate_disk']
    disk_info, network_info, mac_info = '', '', ''
    for k, v in disk:
        disk_info += "{}  ({})\n".format(k, v)
    for k, v in network:
        network_info += "{}  ({})\n".format(k, v)
    for k, v in sorted(mac):
        mac_info += "{}    {}\n".format(k, v)
    if not locate_disk:
        locate_disk = msg['locate_disk']
        if not locate_disk:
            locate_disk = ''
    mem_locate = memLocator()[0]
    message = "NAME:  {0}\n" \
              "FAMILY:  {1}\n" \
              "CHECK STAT:\n" \
              "    {2}\n" \
              "SN:\n" \
              "    {3}\n" \
              "SN1:\n" \
              "    {4}\n" \
              "TIME:\n" \
              "    {5}\n" \
              "BOOT TIME:\n" \
              "    {6}\n" \
              "BIOS TIME:\n" \
              "    {7}\n" \
              "CPU:\n" \
              "    {8}\n" \
              "MEMORY INFO:\n" \
              "    {9}\n" \
              "DISK INFO:\n" \
              "    {10}\n" \
              "RAID INFO:\n" \
              "    {11}\n" \
              "NETWORK INFO:\n" \
              "    {12}\n" \
              "MAC INFO:\n" \
              "    {13}\n" \
              "BIOS VERSION:\n" \
              "    {14}\n" \
              "BMC VERSION:\n" \
              "    {15}\n" \
              "PCIE INFO:\n" \
              "{16}\n" \
              "FRU INFO:\n" \
              "{17}\n" \
              "LOCATE DISK:\n" \
              "{18}\n" \
              "LOCATE MEMORY:\n" \
              "{19}\n" \
              "IP:	 {20}\n" \
              "POWER: {21}\n" \
              "DISK_SN: {22}".format(name,
                                     family,
                                     status,
                                     sn,
                                     sn1,
                                     time,
                                     boot_time,
                                     bios_time,
                                     cpu,
                                     memory,
                                     disk_info.strip(),
                                     raid,
                                     network_info.strip(),
                                     mac_info.strip(),
                                     bios,
                                     bmc,
                                     pci_info,
                                     fru,
                                     locate_disk,
                                     mem_locate,
                                     msg['ip'],
                                     msg['power'],
                                     '', )
    msg.update({'message': message})
    return msg


def sedMessage(msg):
    url = "http://172.16.1.1/login/"
    UA = "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.13 Safari/537.36"
    header = {"User-Agent": UA,
              }
    session = requests.Session()
    postData = {'username': 'admin',
                'passwd': 'trusme123',
                }
    session.post(url,
                 data=postData,
                 headers=header)
    data = json.dumps(msg)
    try:
        p = session.post('http://172.16.1.1/control/msgParsePost', data=data, headers=header)
    finally:
        pass


if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option('-v', '--version', dest='version', action='store_true')
    parser.add_option('-s', '--show', dest='show', action='store_true')
    (options, args) = parser.parse_args()
    if options.version:
        print("Version: V1.3.5")
    if options.show:
        msg_dict = CollectMessage().main()
        info_dict = runMain(msg_dict)
        for key, values in info_dict.items():
            print("=" * 50)
            print("##{}".format(key))
            print("=" * 50)
            print("{}##".format(values))
            print()
    msg_dict = CollectMessage().main()
    info_dict = runMain(msg_dict)
    sedMessage(info_dict)
