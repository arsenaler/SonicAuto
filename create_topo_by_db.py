#!/usr/bin/python
# -*- coding: utf-8 -*-
from common import *
import os


def create_topology(user, password, topology_file, UTM_ID):

    if compare(topology_file, UTM_ID):
        # login to the server
        session = requests.Session()
        login(session, user, password)
        if verify_utm_in_db(UTM_ID):
            pass
        else:
            post_topology_data(session, topology_file)
            post_topology_data(session, topology_file)
            save_file(session, 'after_create.txt')
            utm_list1 = get_utm_list('after_create.txt')
            for i in range(0, len(utm_list1)):
                if UTM_ID == utm_list1[i]:
                    logger.info('create topology successful')
                    # add the topology creater and UTM_ID to database
                    save_user_to_db(user, UTM_ID)
                else:
                    logger.info('create topology fail')
            os.popen("rm after_create.txt")
    else:
        logger.info("please insure the file has the correct UTM ID")


def main():
    args = get_args()
    create_topology(args.user, args.password, args.topology_file, args.UTM_ID)


# start this thing
if __name__ == "__main__":
    main()