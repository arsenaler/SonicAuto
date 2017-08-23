#!/usr/sbin/python
# -*- coding: utf-8 -*-

import os
import os.path
import time
from pysphere import *
from pysphere.resources import VimService_services as VI
from pysphere import VIServer
from pysphere import VIException, VIApiException, FaultTypes
import logging
from pysphere.resources import VimService_services as VI

import subprocess


class vcenter(object):
    '''
    ip = ''
    user = ''
    pwd = ''
    connect_flag = False
    server = None
    '''
    @classmethod
    def connect_server(cls,ip, user, pwd):
        cls.ip = ip
        cls.user = user
        cls.pwd = pwd
        cls.server = VIServer()
        cls.server.connect(cls.ip, cls.user, cls.pwd)
        print "if you use the vm.login_in_guest(), you must install vmware tools in the vm"
        cls.connect_flag = cls.server.is_connected()
        if cls.connect_flag:
            return True
        return False


    @classmethod
    def get_vm(cls, name):
        vm = cls.server.get_vm_by_name(name)
 #       subprocess.call(['ifconfig', 'eth0', 'up'])
        return vm

    @classmethod
    def get_hosts_by_name(cls, from_mor):
        try:
            hosts = cls.server.get_hosts(from_mor)
            return hosts
        except:
            print "the server doesn't connect"
            return None

    @classmethod
    def get_all_hosts(cls):
        return cls.server.get_hosts()

    @classmethod
    def disconnnect_server(cls):
        if cls.connect_flag == True:
            cls.disconnect = cls.server.disconnect()
            cls.connect_flag = False

    @classmethod
    def power_on_vm(cls, name):
        try:
            vm = cls.server.get_vm_by_name(name)
            if (vm.is_powered_off()):
                vm.power_on()
                print 'the vm is off, we will power on it'
                print 'now we power on the PC--' + name
                print 'we will wait for 100 seconds'
                time.sleep(100)
            else:
                print 'the PC -- ' + name + ' is already power on'
        except:
            print "pc is error"

    @classmethod
    def power_off_vm(cls, name):
        try:
            vm = cls.server.get_vm_by_name(name)
            if (vm.is_powered_on()):
                vm.power_off()
                print "now we power off the " + name
            else:
                print 'now the ' + name + ' is power off'
        except:
            print 'the '+ name + "  is error"

    @classmethod
    def get_all_vms(cls):
        return cls.server.get_registered_vms()

    @classmethod
    def login_vm(cls,name, user, pwd):
        vm = cls.server.get_vm_by_name(name)
        vm.login_in_guest(user, pwd)
        subprocess.call(['ifconfig', 'eth0 down'])
        vm.make_directory(r"c:\my\binary")

    @classmethod
    def create_snapshot(cls,vm_name,snap_name):
        vm = cls.server.get_vm_by_name(vm_name)
        return vm.create_snapshot(snap_name)

    @classmethod
    def delete_snapshot(cls, vm_name, snap_name):
        vm = cls.server.get_vm_by_name(vm_name)
        vm.delete_named_snapshot(snap_name)

    @classmethod
    def get_snaplist(cls, vm_name):
        vm = cls.server.get_vm_by_name(vm_name)
        return vm.get_snapshots()

    @classmethod
    def vm_clone(cls, vm_name,new_vm):
        vm = cls.server.get_vm_by_name(vm_name)
        vm.clone(new_vm)

    # if you use the vm.login_in_guest, you must install vmware-tools in the vm
    @classmethod
    def get_vm_ip(cls, vm_name, vm_user, vm_passwd, vm_vlan, iptype):

        vm = cls.server.get_vm_by_name(vm_name)
        vm.login_in_guest(vm_user, vm_passwd)
        net = vm.get_property('net',from_cache=False)
        for i in range(0, len(net)):
            ip_address = net[i].get('ip_addresses')
            ip_network = net[i].get('network')
            if ip_network == vm_vlan:
                if iptype == 'ipv4':
                    return ip_address[0]
                elif iptype == 'ipv6':
                    return ip_address[1]

    @classmethod
    def get_vm_eth0_ip(cls,vm_name, vm_user, vm_passwd):
        vm = cls.server.get_vm_by_name(vm_name)
        vm.login_in_guest(vm_user, vm_passwd)
        return vm.get_property('ip_address', from_cache=False)


    @classmethod
    def add_nic(cls, vm, label, nic_type):

        vm_obj = cls.server.get_vm_by_name(vm)
        if not vm_obj:
            raise Exception("VM %s not found" % vm)

        #Invoke ReconfigVM_Task
        request = VI.ReconfigVM_TaskRequestMsg()
        _this = request.new__this(vm_obj._mor)
        _this.set_attribute_type(vm_obj._mor.get_attribute_type())
        request.set_element__this(_this)
        spec = request.new_spec()
        #add a NIC. the network Name must be set as the device name.
        dev_change = spec.new_deviceChange()
        dev_change.set_element_operation("add")
        if nic_type == 'VMXNET3':
            nic_ctlr = VI.ns0.VirtualVmxnet3_Def("nic_ctlr").pyclass()
        elif nic_type == 'E1000':
            nic_ctlr = VI.ns0.VirtualE1000_Def("nic_ctlr").pyclass()
        else:
            nic_ctlr = VI.ns0.VirtualVmxnet2_Def("nic_ctlr").pyclass()

        nic_backing = VI.ns0.VirtualEthernetCardNetworkBackingInfo_Def("nic_backing").pyclass()
        nic_backing.set_element_deviceName(label)
        nic_ctlr.set_element_addressType("generated")
        nic_ctlr.set_element_backing(nic_backing)
        nic_ctlr.set_element_key(4)
        dev_change.set_element_device(nic_ctlr)

        spec.set_element_deviceChange([dev_change])
        request.set_element_spec(spec)
        ret = cls.server._proxy.ReconfigVM_Task(request)._returnval

        #Wait for the task to finish
        task = VITask(ret, cls.server)
        status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
        if status == task.STATE_SUCCESS:
            print "VM %s successfully reconfigured" % vm

        elif status == task.STATE_ERROR:
            print "Error reconfiguring vm: %s" % vm, task.get_error_message()

    @classmethod
    def delete_nic(cls, vm, label):

        vm_obj = cls.server.get_vm_by_name(vm)
        if not vm_obj:
            raise Exception("VM %s not found" % vm)

        #Find Virtual Nic device
        net_device = None
        print vm_obj.properties.config.hardware.device
        for dev in vm_obj.properties.config.hardware.device:
            if dev._type in ["VirtualE1000", "VirtualVmxnet3", "VirtualVmxnet2"]   \
                    and dev.backing.deviceName == label:

                net_device = dev._obj
            if not net_device:
                raise Exception("The vm seems to lack a Virtual Nic")

        print net_device

        #Invoke ReconfigVM_Task
        request = VI.ReconfigVM_TaskRequestMsg()
        _this = request.new__this(vm_obj._mor)
        _this.set_attribute_type(vm_obj._mor.get_attribute_type())
        request.set_element__this(_this)
        spec = request.new_spec()

        dev_change = spec.new_deviceChange()
        dev_change.set_element_device(net_device)
        dev_change.set_element_operation("remove")
        spec.set_element_deviceChange([dev_change])
        print spec
        request.set_element_spec(spec)

        spec.set_element_deviceChange([dev_change])
        request.set_element_spec(spec)
        ret = cls.server._proxy.ReconfigVM_Task(request)._returnval

        #Wait for the task to finish
        task = VITask(ret, cls.server)
        status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
        if status == task.STATE_SUCCESS:
            print "VM %s successfully reconfigured" % vm

        elif status == task.STATE_ERROR:
            print "Error reconfiguring vm: %s" % vm, task.get_error_message()

    @classmethod
    def change_nic_vlan(cls, vm, src_vlan, dst_vlan):

        vm_obj = cls.server.get_vm_by_name(vm)
        if not vm_obj:
            raise Exception("VM %s not found" % vm)

    #Find Virtual Nic device
        net_device = None
        for dev in vm_obj.properties.config.hardware.device:
            if dev._type in ["VirtualE1000", "VirtualVmxnet3", "VirtualVmxnet2"]   \
                    and dev.backing.deviceName == src_vlan:

                net_device = dev._obj
            if not net_device:
                raise Exception("The vm seems to lack a Virtual Nic")
        net_device.Backing.set_element_deviceName(dst_vlan)

    #Invoke ReconfigVM_Task
        request = VI.ReconfigVM_TaskRequestMsg()
        _this = request.new__this(vm_obj._mor)
        _this.set_attribute_type(vm_obj._mor.get_attribute_type())
        request.set_element__this(_this)
        spec = request.new_spec()
        #add a NIC. the network Name must be set as the device name.
        dev_change = spec.new_deviceChange()
        dev_change.set_element_device(net_device)
        dev_change.set_element_operation("edit")
        spec.set_element_deviceChange([dev_change])
        request.set_element_spec(spec)
        ret = cls.server._proxy.ReconfigVM_Task(request)._returnval

        #Wait for the task to finish
        task = VITask(ret, cls.server)
        status = task.wait_for_state([task.STATE_SUCCESS, task.STATE_ERROR])
        if status == task.STATE_SUCCESS:
            print "VM %s successfully reconfigured" % vm

        elif status == task.STATE_ERROR:
            print "Error reconfiguring vm: %s" % vm, task.get_error_message()


'''
vcenter.connect_server('10.8.2.21', 'root', 'sonicpassword')
print vcenter.get_vm('wdong-remote_vm')
vms = vcenter.get_all_vms()


for vm in vms:
    if 'wdong' in vm:
        print vm

print '=================================='
print '#####################################'
'''