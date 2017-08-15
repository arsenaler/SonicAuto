#!/usr/bin/python
# -*- coding: utf-8 -*-

# we will ssh to topology ip and excute the script to testting


from common import *
from ssh import *
import requests
import os
from log import *


def excute_script(ip, script,user,UTM_ID):
    ssh_connect = test_ssh()
    ssh_connect.test_connect(ip, 22, 'root', 'password')

    logger.info('tqtest.pl -cts %s -var G_OPENSTACK="1" -var G_USER=%s -sonicos_ver 6.5 -log_level DEBUG -dev -nodb '%(script, user))
    ssh_connect.test_cmd('rm -rf /DEV_TESTS/SonicOS/6.5/Network/wdong; mkdir /DEV_TESTS/SonicOS/6.5/Network/wdong;cd /DEV_TESTS/SonicOS/6.5/Network/wdong;wget http://10.103.51.0:8000/topology/DNS_53.zip; unzip DNS_53.zip; tqtest.pl -cts %s -var G_OPENSTACK="1" -var G_USER=%s -sonicos_ver 6.5 -log_level DEBUG -dev -nodb >wdong_test.txt '%(script, user))
    ssh_connect.test_close()


def main():
    args = get_args()
    session = requests.session()
    login(session, args.user, args.password)
    os.system('rm -f topology_html.txt')
    save_file(session, 'topology_html.txt')
    ip = get_topology_ip('topology_html.txt' , args.UTM_ID)
    logger.info("we will ssh to %s to excute script" %ip)
# /SWIFT4.0/TESTS/SonicOS/glx/DPI-SSH/dpi-ssh/testsuites
    excute_script(ip, "/DEV_TESTS/SonicOS/6.5/Network/wdong/DNS_53/testsuites/DNS_53.cts", args.user, args.UTM_ID)

    os.system('rm -f topology_html.txt')

if __name__ == '__main__':
    main()
