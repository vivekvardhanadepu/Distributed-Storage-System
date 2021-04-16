"""
@author: Kartik Saini

"""

mds_ip = {"primary":{"ip":"", "port":0}, "backup":{"ip":"", "port":0}}

num_objects_per_file = 1

max_num_objects_per_pg = 1

_port = 9999

MSG_SIZE = 1024
HEADERSIZE = 10

"""
Message Name/type Harshit is using :
ALIVE = will be send to check the heartbeat
ACK = will be send in return of heartbeat 
FAIL = will be send by storage node to monitor along with the IP or storage number
"""

dir_tree = {
            "dir1":{},
            "dir2":{}
            }

"""
PG -> osds hash table on monitor

OSDs -> ip, port .. for live osds on monitor

OSD -> replicas ... for monitoring on OSD

"""

# Update all the stroage node IP everytime
storage_1 = {"ip":"127.0.0.1", "port":9001}
storage_2 = {"ip":"127.0.0.1", "port":9002}
storage_3 = {"ip":"127.0.0.1", "port":9003}
storage_4 = {"ip":"4.0.0.0", "port":9004}

storage_ip = {"osd_id1":storage_1,"osd_id2":storage_2,"osd_id3":storage_3,"osd_id4":storage_4}

# add 10 to port to get read/write IP


# Update all the monitor node IP
monitor_1 = {"ip":"127.0.0.1", "port":8801}
monitor_2 = {"ip":"127.0.0.1", "port":8802}
monitor_ip = {"primary": monitor_1, "backup": monitor_2}
