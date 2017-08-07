#!/usr/bin/python
# -*- coding: utf-8 -*-
from common import *
import os

def create_topology(user, password, topology_file, UTM_ID):

    if compare(topology_file, UTM_ID):
        # login to the server
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
                    print 'create topology successful'
                    # add the topology creater and UTM_ID to database
                    save_user_to_db(user, UTM_ID)
                else:
                    print 'create topology fail'
        else:
            if UTM_ID in utm_list:
                    print "the UTM was used , please detroy the topology"
            else:
                    # create topology
                post_topology_data(session, topology_file)
                save_file(session, 'after_create.txt')
                utm_list1 = get_utm_list('after_create.txt')
                for i in range(0, len(utm_list1)):
                    if UTM_ID == utm_list1[i]:
                        print 'create topology successful'
                        logging.info( 'create topology successful')
                        # add the topology creater and UTM_ID to database
                        save_user_to_db(user, UTM_ID)
                    else:
                        pass
    else:
        print "please insure the file has the correct UTM ID"


def main():
    args = get_args()
    create_topology(args.user, args.password, args.topology_file, args.UTM_ID)
    os.popen("rm *.txt")

# start this thing
if __name__ == "__main__":
    main()
