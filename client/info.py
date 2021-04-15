"""
@author: Kartik Saini

"""

mds_ip = {"primary":{"ip":"127.0.0.1", "port":8089},#, "client_req_ip":"127.0.0.1", "client_req_port":8090, "cluster_req_ip":"127.0.0.1", "cluster_req_port":8091}, 
			"backup":{"ip":"127.0.0.1", "port":8092}}#, "client_req_ip":"127.0.0.1", "client_req_port":8090, "cluster_req_ip":"127.0.0.1", "cluster_req_port":8091}}
monitor_ip = {"primary":{"ip":"3.16.150.43", "port":12345}, "backup":{"ip":"", "port":0}}

num_objects_per_file = 1

max_num_objects_per_pg = 1

MSG_SIZE = 1024
HEADERSIZE = 10

TREE = {	
			"username":"",
			"client_id":"",
			"last_file_id":"",
            "root":{  # dir = {file_id:[list of PG ids]}
            }
        }

"""
PG -> osds hash table on monitor

OSDs -> ip, port .. for live osds on monitor

OSD -> replicas ... for monitoring on OSD

Add tree/ folder in MDS

initiate demo clients using demo_clients.py on MDS; it will create some new clients with their empty trees
"""