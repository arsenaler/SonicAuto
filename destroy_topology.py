#!/usr/bin/python
# -*- coding: utf-8 -*-

from common import *
from log import *
import os



# destroy the specify topology
def destroy__specify_topology(user, password, utm):
    base_url = 'http://10.203.26.61'
    session = requests.Session()
    login(session, user, password)
    save_file(session, 'topology_html.txt')
    token = get_token(session, 'topology_html.txt')
    topologyID_UTM_map = get_utm_topology_map('topology_html.txt')
    logger.info('topologyID_UTM_map is %s' %topologyID_UTM_map)
    specify_id = topologyID_UTM_map.get(utm)
    logger.info('the specify_id is %s'%specify_id)
    if specify_id:
        post_url = base_url + '/topologies/%s'%specify_id
        logger.info('now we will delete the topology')
        post_data = {'_method':'delete', "authenticity_token": token}
        session.post(post_url, data=post_data, headers=header1)
        del_user_from_db(utm)
        topology_id_utm = get_utm_topology_map('topology_html.txt')
        id = get_utm_topology_map.get(utm)

    else:
        logger.info('please input the correctly UTM ID')


def main():
    args = get_args()
    os.popen("rm *.txt")
    destroy__specify_topology(args.user, args.password, args.UTM_ID)
    os.popen("rm *.txt")
# start this thing
if __name__ == "__main__":
    main()
