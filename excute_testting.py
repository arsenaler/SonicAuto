#!/usr/bin/python
# -*- coding: utf-8 -*-

# we will ssh to topology ip and excute the script to testting


from comman import *
from ssh import *
import requests
import os


def excute_script(ip, script, user, version):

    ssh_connect = test_ssh()
    ssh_connect.test_connect(ip, 22, 'root', 'password')
    print 'dddddddddd'

    print 'tqtest.pl -cts %s -var G_OPENSTACK="1" -var G_USER=%s -sonicos_ver %s -log_level DEBUG -dev -nodb >wdong_test.txt'%(script, user, version)
    ssh_connect.test_cmd('tqtest.pl -cts %s -var G_OPENSTACK="1" -var G_USER=%s -sonicos_ver %s -log_level DEBUG -dev -nodb >wdong_test.txt'%(script, user, version))
    print 'dtttttttttttttttttt'
    ssh_connect.test_close()

def main():
    args = get_args()
    session = requests.session()
    login(session, args.user, args.password)
    save_file(session, 'topology_html.txt')
    ip = get_topology_ip('topology_html.txt' , 417)
    print ip
# /SWIFT4.0/TESTS/SonicOS/glx/DPI-SSH/dpi-ssh/testsuites
    excute_script(ip, "/DEV_TESTS/SonicOS/6.5/DPI-SSH/dpi-ssh/testsuites/dpi-ssh.cts", args.user, '6.5')
    os.system('rm -f topology_html.txt')

if __name__ == '__main__':
    main()

