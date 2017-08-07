#!/usr/bin/python
# -*- coding: utf-8 -*-
import re
import requests
import logging
import argparse
import getpass
from pymongo import MongoClient
from cStringIO import StringIO
import configparser

header1 = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connectionn': 'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded'
        }


def get_args():
    parser = argparse.ArgumentParser(
        description='Arguments for talking to openstack deploy topology')

    parser.add_argument('-u', '--user',
                        required=True,
                        action='store',
                        help='User name to use')

    parser.add_argument('-p', '--password',
                        required=False,
                        action='store',
                        help='Password to use')

    parser.add_argument('-t', '--topology_file',
                        required=False,
                        action='store',
                        help='use topology file to deploy')

    parser.add_argument('-s', '--script_file',
                        required=False,
                        action='store',
                        help='excute script on the openstack pc1')

    parser.add_argument('-i', '--UTM_ID',
                        required=False,
                        action='store',
                        help='the UTM_id')

    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password:')
    return args


# save the user to db, if user create the topology
def connect_db():
    client = MongoClient('10.8.71.164', 27017)
    db_name = "topoloy_data"
    db = client[db_name]
    topology_info = db.topology_info
    return topology_info


def save_user_to_db(user, UTM_ID):
    topology_info = connect_db()
    data = {"user" : user, "UTM_ID" : UTM_ID}
    topology_info.insert(data)


def del_user_from_db(UTM_ID):
    topology_info = connect_db()
    topology_info.remove({'UTM_ID' : UTM_ID})


def del_utm_from_db(user):
    topology_info = connect_db()
    topology_info.remove({'user' : user})


# verify the UTM whether in the DB
def verify_utm_in_db(UTM_ID):
    topology_info = connect_db()
    utm_list = []
    user_list = []
    for item in topology_info.find():
        utm_list.append(item.get("UTM_ID"))
        user_list.append(item.get('user'))
    user_utm_map = dict(zip(utm_list, user_list))
    if str(UTM_ID) in utm_list:
        print "the utm was used by %s"%user_utm_map.get(str(UTM_ID))
        print "if you want to user the UTM, please ask %s to destroy the topology"%user_utm_map.get(str(UTM_ID))
        return True
    else:
        pass


# verify topology_file whether has UTM
def compare(file, UTM_ID):
    with open(file, 'r') as f:
        for line in f:
            if str(UTM_ID) in line:
                return True


# save the html content
def save_file(session, file_name):
    base_url = 'http://10.203.26.61'
    get_url = base_url + "/topologies"
    r = session.get(get_url)
    content = r.content
    try:
        file1= open(file_name,'w')
        file1.write(content)
    except Exception as e:
        print('unexpect error happen')
    finally:
        file1.close()


# get the token from html content
def get_token(session, file_name):
    # get the token
    with open(file_name, 'r') as f:
        for line in f:
            if "csrf-token" in line:
                token = line.split('"')[1]
    return token


# get all the utm id who was used by topology
def get_utm_list(file_name):
    utm_list = []
    with open(file_name, 'r') as f:
        for line in f:
            if  "topology_resource_id" and 'team=UTM' in line:
                utm = line.split(":")[4].split(',')[0]
                utm_list.append(utm)
    return utm_list


# get topology ID , if we destroy the topology, we will use it
def get_topologyID_list(file_name):
    topology_id_list = []
    with open(file_name, 'r') as f:
        for line in f:
            if 'Destroy' in line:
                topology_id= line.split('"')[3].strip('/ ').split('/')[1]
                topology_id_list.append(topology_id)
    return topology_id_list


# map the utm and topology id, we can used it when we delete the topology
def get_utm_topology_map(file_name):
    utm_list = get_utm_list(file_name)
    topology_id_list = get_topologyID_list(file_name)
    dict1 = dict(zip(utm_list, topology_id_list))
    return dict1


# when create the topology, post the data
def post_topology_data(session, topology_file):
    base_url = 'http://10.203.26.61'
    post_url = base_url + "/topologies"
    topology_data = open(topology_file,'r').read()
    post_data = {'location': 'BJ',
                'topology_definition': topology_data,
                'commit': 'Create Topology'
                }
    session.post(post_url, data=post_data, headers=header1)


# login to the server to make topology
def login(session, user, password):
    base_url = 'http://10.203.26.61'
    login_infor = {'email': user, "password": password, "location": "BeiJing"}
    login_url = base_url+"/sessions/create"
    r = session.post(login_url, login_infor)


# get the topology ip, usually it's PC1's ip, we will use it when we excute the testing script by SSH
def get_topology_ip(file_name, UTM_ID):
    with open(file_name, 'r') as f:
        for line in f:
            if "floatingip" and str(UTM_ID) in line:
                t = line.split(":")
                for i in range(0, len(t)):
                    if "10.6.72" in t[i]:
                        ip = t[i].split(";")[1].split("&")[0]
    return ip

'''
def get_utm_ip_map(file_name,UTM_ID):
    utm_list = get_utm_list(file_name)
    ip_list = get_topology_iplist(file_name)
    map_dict = dict(zip(utm_list, ip_list))
    return map_dict
'''