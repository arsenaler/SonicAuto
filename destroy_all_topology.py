#!/usr/bin/python
# -*- coding: utf-8 -*-
from common import *
import os
from log import *


# delete all the topologies which was created by myself
def destroy_topology(user, password):
    base_url = 'http://10.203.26.61'
    session = requests.Session()
    login(session, user, password)
    save_file(session, 'topology_html.txt')
    token = get_token(session, 'topology_html.txt')
    topologyID_UTM_map = get_utm_topology_map('topology_html.txt')
    logger.info('now we will delete all the topology')
    for key, value in topologyID_UTM_map.iteritems():
        post_url = base_url + "/topologies/" + value
        post_data = {'_method':'delete', "authenticity_token": token}
        session.post(post_url, data=post_data, headers=header1)
    del_utm_from_db(user)
    os.system('rm -r topology_html.txt')


def main():
    args = get_args()
    destroy_topology(args.user, args.password)

# start this thing
if __name__ == "__main__":
    main()
