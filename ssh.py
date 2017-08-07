#!/usr/sbin/python
# -*- coding: utf-8 -*-


import paramiko

class test_ssh(object):

    @classmethod
    def test_connect(cls, host, port, username, pwd):
        transport = paramiko.Transport((host, port))
        transport.connect(username = username, password = pwd)
        cls.__transport = transport


    @classmethod
    def test_close(cls):
        cls.__transport.close()

    @classmethod
    def test_cmd(cls, command):
        ssh = paramiko.SSHClient()
        ssh._transport = cls.__transport
        stdin, stdout, stderr = ssh.exec_command(command)
        result = stdout.read()
        return result
'''
test_ssh.test_connect("10.8.71.56", 22, 'qa', 'password')
t = test_ssh.test_cmd('ifconfig')
print t
test_ssh.test_close()
'''