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
storage_1 = {"ip":"18.223.120.174", "port":9991}
storage_2 = {"ip":"18.223.120.174", "port":9992}
storage_3 = {"ip":"18.223.120.174", "port":9993}
storage_4 = {"ip":"18.223.120.174", "port":9994}

storage_ip = {1:storage_1,2:storage_2,3:storage_3,4:storage_4}


# Update all the monitor node IP
monitor_1 = {"ip":"3.16.150.43", "port":12345}
monitor_2 = {"ip":"18.219.161.117", "port":12346}
monitor_ip = {"primary": monitor_1, "backup": monitor_2}