"""
@author: Kartik Saini
@author: Harshit Soora
@author: Vivek Vardhan Adepu
@author: Shivang Gupta
@author: Deepak Imandi

"""
# MDS
MDS_PORT = 1201
MDS_IPs = {"primary":{"ip":"127.0.0.1", "port":MDS_PORT}, "backup":{"ip":"127.0.0.1", "port":MDS_PORT+1}}

num_objects_per_file = 1

max_num_objects_per_pg = 1



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

OSD_IPs = {1:"127.0.0.1", 2:"127.0.0.1", 3:"127.0.0.1", 4:"1.5.6.8"}

READ_WRITE_PORT = 1207
HEARTBEAT_PORT = 1213


# MONITOR
MONITOR_IPs = {"primary": "127.0.0.1", "backup": "1.2.3.4"}

CLIENT_REQ_PORT = 1217
WRITE_ACK_PORT = 1223
OSD_INACTIVE_STATUS_PORT = 1231
RECV_PRIMARY_UPDATE_PORT = 1238
