"""
@author: Kartik Saini

"""

mds_ip = {"primary":{"ip":"", "port":0}, "backup":{"ip":"", "port":0}}
monitor_ip = {"primary":{"ip":"3.16.150.43", "port":12345}, "backup":{"ip":"", "port":0}}

num_objects_per_file = 1

max_num_objects_per_pg = 1

MSG_SIZE = 1024
HEADERSIZE = 10

dir_tree = {
            "dir1":{},
            "dir2":{}
            }

"""
PG -> osds hash table on monitor

OSDs -> ip, port .. for live osds on monitor

OSD -> replicas ... for monitoring on OSD

"""