import socket
import pickle
import sys
sys.path.insert(1, '../utils/')

from transfer import _send_msg, _recv_msg, _wait_recv_msg
from info import RECV_PRIMARY_UPDATE_PORT, MSG_SIZE

hashtable = {}
MDS_flags = {}
cluster_topology = {}

def recv_primary_update():
    recv_primary_update_socket = socket.socket()
    print ("recv primary update socket successfully created")
    recv_primary_update_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # reserve a port on your computer
    port = RECV_PRIMARY_UPDATE_PORT

    # Next bind to the port
    # we have not entered any ip in the ip field
    # instead we have inputted an empty string
    # this makes the server listen to requests
    # coming from other computers on the network
    recv_primary_update_socket.bind(('', port))
    print ("primary update socket bound to %s" %(port))

    # put the socket into listening mode
    recv_primary_update_socket.listen(5)
    print ("primary update socket is listening")

    # a forever loop until we interrupt it or
    # an error occurs
    while True:

        # Establish connection with osd
        c, addr = recv_primary_update_socket.accept()
        print ('Got connection from', addr)

        # recv the update
        update = _recv_msg(c, 1024)
        print(update)

        if update["update_type"] == "hash_table":
            for i in range(len(update["pg_or_osd_ids_list"])):
                hashtable[update["pg_or_osd_ids_list"][i]] = update["osd_list"][i]
        else:
            for i in range(len(update["pg_or_osd_ids_list"])):
                cluster_topology[update["pg_or_osd_ids_list"][i]] = update["osd_list"][i]
        
        hashtable_file = open('hashtable', 'wb')
        hashtable_dump = pickle.dumps(hashtable)
        hashtable_file.write(hashtable_dump)
        hashtable_file.close()

        cluster_topology_file = open('cluster_topology', 'wb')
        cluster_topology_dump = pickle.dumps(cluster_topology)
        cluster_topology_file.write(cluster_topology_dump)
        cluster_topology_file.close()
        msg = {"status":"SUCCESS"}
        _send_msg(c, msg)
        # send the acknowledgement
        c.close()

    recv_primary_update_socket.close()

def main():
    global hashtable, cluster_topology, MDS_flags

    hashtable_file = open('hashtable', 'rb')
    hashtable_dump = hashtable_file.read()
    hashtable = pickle.loads(hashtable_dump)

    MDS_flags_file = open('MDS_flags', 'rb')
    MDS_flags_dump = MDS_flags_file.read()
    MDS_flags = pickle.loads(MDS_flags_dump)

    cluster_topology_file = open('cluster_topology', 'rb')
    cluster_topology_dump = cluster_topology_file.read()
    cluster_topology = pickle.loads(cluster_topology_dump)

    hashtable_file.close()
    MDS_flags_file.close()
    cluster_topology_file.close()
    recv_primary_update()

if __name__ == '__main__':
    main()