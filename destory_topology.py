#!/usr/bin/python
# -*- coding: utf-8 -*-

from common import *


# destroy the specify topology
def destroy__specify_topology(user, password, utm):
    base_url = 'http://10.203.26.61'
    session = requests.Session()
    login(session, user, password)
    save_file(session, 'topology_html.txt')
    token = get_token(session, 'topology_html.txt')
    topologyID_UTM_map = get_utm_topology_map('topology_html.txt')
    specify_id = topologyID_UTM_map.get(utm)
    if specify_id:
        post_url = base_url + '/topologies/%s'%specify_id
        print 'now we will delete the topology'
        post_data = {'_method':'delete', "authenticity_token": token}
        session.post(post_url, data=post_data, headers=header1)
        del_user_from_db(utm)
    else:
        logging.info('please input the correctly UTM ID')
        print 'please input the correctly UTM ID'


def main():
    args = get_args()
    destroy__specify_topology(args.user, args.password, args.UTM_ID)

# start this thing
if __name__ == "__main__":
    main()
