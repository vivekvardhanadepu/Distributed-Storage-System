"""
@author: Kartik Saini
@author: Harshit Soora
@author: Vivek Vardhan Adepu
@author: Shivang Gupta
@author: Deepak Imandi

"""
# MDS
MDS_IPs = {"primary":{"ip":"", "port":0}, "backup":{"ip":"", "port":0}}

num_objects_per_file = 1

max_num_objects_per_pg = 1

MDS_PORT = 1201

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

# OSD
OSD_IPs = {1:"1.5.6.3", 2:"1.5.6.8", 3:"1.2.35.53", 4:"1.5.6.8"}

READ_WRITE_PORT = 1207
HEARTBEAT_PORT = 1213


# MONITOR
MONITORS = {"primary": "10.0.2.3", "backup": "1.2.3.4"}

CLIENT_REQ_PORT = 1217
WRITE_ACK_PORT = 1223
OSD_INACTIVE_STATUS_PORT = 1231