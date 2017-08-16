
#!/usr/bin/python
import re
import requests
from log import *
import argparse
import getpass
from pymongo import MongoClient
from cStringIO import StringIO
import configparser


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
                        required=True,
                        action='store',
                        help='use topology file to deploy')

    parser.add_argument('-i', '--UTM_ID',
                        required=False,
                        action='store',
                        help='the UTM_id')


    args = parser.parse_args()

    if not args.password:
        args.password = getpass.getpass(
            prompt='Enter password')

    return args


def compare(file, UTM_ID):
    t = str(UTM_ID)
    with open(file, 'r') as f:
        for line in f:
            if t in line:
                return True


def save_file(session, file_name):
    base_url = 'http://10.203.26.61'
    get_url = base_url + "/topologies"
    r = session.get(get_url)
    content = r.content
    try:
        file1= open(file_name,'w')
        file1.write(content)
    except Exception as e:
        logger.info('unexpect error happen')
    finally:
        file1.close()


def get_token(session, file_name):
    # get the token
    with open(file_name, 'r') as f:
        for line in f:
            if "csrf-token" in line:
                token = line.split('"')[1]
    return token


def get_utm_list(file_name):
    utm_list = []
    with open(file_name, 'r') as f:
        for line in f:
            if "topology_resource_id" and 'team=UTM' in line:
                utm = line.split(":")[4].split(',')[0]
                utm_list.append(utm)
    return utm_list


def get_topologyID_list(file_name):
    topology_id_list = []
    with open(file_name, 'r') as f:
        for line in f:
            if 'Destroy' in line:
                topology_id= line.split('"')[3].strip('/ ').split('/')[1]
                topology_id_list.append(topology_id)
    return topology_id_list


def get_utm_topology_map(file_name):
    utm_list = get_utm_list(file_name)
    topology_id_list = get_topologyID_list(file_name)
    dict1 = dict(zip(utm_list, topology_id_list))
    return dict1


def post_topology_data(session, topology_file):
    header1 = {
            'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:52.0) Gecko/20100101 Firefox/52.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Connectionn': 'keep-alive',
            'Content-Type':'application/x-www-form-urlencoded'
        }
    base_url = 'http://10.203.26.61'
    post_url = base_url + "/topologies"
    topology_data = open(topology_file,'r').read()
    post_data = {'location': 'BJ',
                'topology_definition': topology_data,
                'commit' : 'Create Topology'
                                }
    session.post(post_url, data=post_data, headers=header1)


def save_user_to_db(user, UTM_ID):
    client = MongoClient('10.8.71.164', 27017)
    db_name = "topoloy_data"
    db = client[db_name]

    posts = db.posts
    post = {"user" : user, 'UTM_ID': UTM_ID}
    post_id = posts.insert(post)
    print posts.find_one({"user" : user})
    test = posts.find_one({"user" : 'wdong'})
    logger.info('the utm id is %s'%test.get('UTM_ID'))


def login(session, user, password):
    base_url = 'http://10.203.26.61'
    login_infor = {'email': user, "password": password, "location": "BeiJing"}
    login_url = base_url+"/sessions/create"
    r = session.post(login_url, login_infor)


def create_topology(user, password, topology_file, UTM_ID):
    if compare(topology_file, UTM_ID):
        #login to the server
        session = requests.Session()
        login(session, user, password)

        # verify the UTM whether was used by yourself
        save_file(session, 'before_create.txt')
        utm_list = get_utm_list("before_create.txt")
        # if you first to make topology, it will post the date to server
        if len(utm_list) == 0:
            post_topology_data(session, topology_file)
            save_file(session, 'after_create.txt')
            utm_list1 = get_utm_list('after_create.txt')
            for i in range(0, len(utm_list1)):
                if UTM_ID == utm_list1[i]:
                    logger.info('create topology successful')
                    # add the topology creater and UTM_ID to database
                    #save_user_to_db(user, UTM_ID)
                else:
                    logger.info('create topology fail')
        else:
            for i in range(0, len(utm_list)):
                if UTM_ID == utm_list[i]:
                    logger.info("the UTM was used by others, please ask others detroy the topology")
                else:
                    # create topology
                    post_topology_data(session, topology_file)
                    save_file(session, 'after_create.txt')
                    utm_list1 = get_utm_list('after_create.txt')
                    for i in range(0, len(utm_list1)):
                        if UTM_ID == utm_list1[i]:
                            print 'create topology successful'
                            logger.info( 'create topology successful')
                            # add the topology creater and UTM_ID to database
                           # save_user_to_db(user, UTM_ID)
                        else:
                            print 'create topology fail'
                            logger.info( 'create topology fail')

    else:
        logger.info("please insure the file has the correct UTM ID")


def main():
    args = get_args()
    if os.path.isfile('*.txt'):
        os.system('rm -rf *.txt')
    else:
        pass
    create_topology(args.user, args.password, args.topology_file, args.UTM_ID)

# start this thing
if __name__ == "__main__":
    main()
'''

if compare('test.json', 418):
    print "test"
else:
    print 'fail'
'''