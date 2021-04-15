"""
@author: Kartik Saini
@author: Harshit Soora
@author: Vivek Vardhan Adepu
@author: Shivang Gupta
@author: Deepak Imandi

"""

import threading
import socket
import pickle
import sys

sys.path.insert('../utils/')
from transfer import _send_msg, _recv_msg
from monitor.monitor_gossip import heartbeat_protocol

hashtable = {}
cluster_topology = {}

def recv_write_acks():
    global hashtable, cluster_topology

    s = socket.socket()
    print ("write ack socket successfully created")

    # reserve a port on your computer in our
    # case it is 1234 but it can be anything
    port = 1234

    # Next bind to the port
    # we have not entered any ip in the ip field
    # instead we have inputted an empty string
    # this makes the server listen to requests
    # coming from other computers on the network
    s.bind(('', port))
    print ("write ack socket bound to %s" %(port))

    # put the socket into listening mode
    s.listen(5)
    print ("socket is listening")

    # a forever loop until we interrupt it or
    # an error occurs
    while True:

        # Establish connection with osd
        c, addr = s.accept()
        print ('Got connection from', addr)

        # recv the acknowledgement
        ack = _recv_msg(c, 1024)
        print(ack)

        # extracting the written pd_id, free_space, osd_id of that osd
        client_id = ack["client_id"]
        client_addr = ack["client_addr"]    # addr = (ip, port)
        pg_id = ack["pg_id"]
        free_space = ack["free_space"]
        osd_id = ack["osd_id"]

        # if the osd is down or out, make it up again
        # [need to check this]
        if cluster_topology[osd_id]["status"] != 0:
            cluster_topology[osd_id]["status"] = 0
        
        # updating the write status of the osd to 1
        for i in range(len(hashtable[pg_id])):
            if hashtable[pg_id][i][0] == osd_id:
                hashtable[pg_id][i][1] = 1
        
        replication_factor = 0
        # adding the new friend
        for osd in hashtable[pg_id]:
            if osd[0] != osd_id:
                if osd[1] == 1:
                    replication_factor += 1
                    cluster_topology[osd_id]["friends"].add(osd[0])
                    cluster_topology[osd[0]]["friends"].add(osd_id)

        cluster_topology[osd_id]["free_space"] = free_space

        # updating the backup        
        update_backup_monitor("hash_table", [pg_id], [hashtable[pg_id]])
        update_backup_monitor("cluster_topology", [osd[0] for osd in hashtable[pg_id]], \
                            [cluster_topology[osd] for osd in hashtable])

        hashtable_file = open('hashtable', 'wb')
        cluster_topology_file = open('cluster_topology', 'wb')
        
        hashtable_dump = pickle.dumps(hashtable)
        hashtable_file.write(hashtable_dump)
        hashtable_file.close()

        cluster_topology_dump = pickle.dumps(cluster_topology)
        cluster_topology_file.write(cluster_topology_dump)
        cluster_topology_file.close()

        if replication_factor > 1:
            # sending write update to client
            client_update = socket.socket()
            print ("client write ack socket successfully created")
            
            client_update.connect(client_addr)

            msg = {"type": "WRITE_RESPONSE", "PG_ID": pg_id, \
                   "status": "SUCCESS", "message": "write successful",\
                   "client_id": client_id} 

            _send_msg(client_update, msg)

            client_update.close()

            # sending write update to MDS
            MDS_update = socket.socket()
            print ("MDS write ack socket successfully created")

            MDS_update.connect(MDS_addr)

            msg = {"type": "WRITE_RESPONSE", "PG_ID": pg_id, \
                   "status": "SUCCESS", "message": "write successful",\
                   "client_id": client_id} 

            _send_msg(MDS_update, msg)

            MDS_update.close()

        error = ""
        status = "SUCCESS"

        # send success
        _send_msg(c, {"error":error, "status":status})

        c.close()

    s.close()


def recv_inactive_osd():
    s = socket.socket()
    print ("inactive osd listener socket successfully created")

    # reserve a port on your computer in our
    # case it is 1235 but it can be anything
    port = 1235

    # Next bind to the port
    # we have not entered any ip in the ip field
    # instead we have inputted an empty string
    # this makes the server listen to requests
    # coming from other computers on the network
    s.bind(('', port))
    print ("inactive osd listener socket bound to %s" %(port))

    # put the socket into listening mode
    s.listen(5)
    print ("inactive osd listener socket is listening")

    # a forever loop until we interrupt it or
    # an error occurs
    while True:

        # Establish connection with client.
        c, addr = s.accept()
        print ('Got connection from', addr)

        # recv the inactive osd
        osd = _recv_msg(c, 1024)

        # START THE RECOVERY


def recv_client_reqs():
    global cluster_topology, hashtable

    s = socket.socket()
    print ("client req listener socket successfully created")

    # reserve a port on your computer in our
    # case it is 1236 but it can be anything
    port = 1236

    # Next bind to the port
    # we have not entered any ip in the ip field
    # instead we have inputted an empty string
    # this makes the server listen to requests
    # coming from other computers on the network
    reuse socket code
    s.bind(('', port))
    print ("client req listener socket bound to %s" %(port))

    # put the socket into listening mode
    s.listen(5)
    print ("client req listener socket is listening")

    # a forever loop until we interrupt it or
    # an error occurs
    while True:

        # Establish connection with client.
        c, addr = s.accept()
        print ('Got connection from', addr)
        
        # recv the pg_id, size
        req = _recv_msg(c, 1024)

        if(req["type"] == "WRITE"):
            pg_id = req["pg_id"]
            size = req["size"]
            hashtable[pg_id] = []

            i = 0
            for osd_id in cluster_topology:
                if cluster_topology[osd_id]["free_space"] > size:
                    hashtable[pg_id].append((osd_id, 0))
                    i = i+1

                if(i>2):
                    break

            osd_ids = [hashtable[pg_id][i][0] for i in range(3)]

            for osd_id in osd_ids
                addrs = {osd_id:(cluster_topology[osd_id]["ip"], cluster_topology[osd_id]["port"])}
            osds_dict = {"osd_ids": osd_ids, "addrs": addrs}

            # updating the backup(only hash_table)
            # update_backup_monitor("hash_table", [pg_id], [hashtable[pg_id]])

            hashtable_dump = pickle.dumps(hashtable)
            hashtable_file.write(hashtable_dump)
            hashtable_file.close()

            _send_msg(c, osds_dict)

        elif req["type"] == "READ":
            pg_id = req["pg_id"]
            osd_ids = [hashtable[pg_id][i][0] for i in range(3)]
            addrs = [(cluster_topology[osd_id]["ip"], cluster_topology[osd_id]["port"]) \
                            for osd_id in osd_ids]
            osds_dict = {"osd_ids": osd_ids, "addrs": addrs}
            _send_msg(c, osds_dict)

        c.close()

    s.close()
            

def main():
    ### hashtable and cluster topology structure

    ## write_status : 0(NOT WRITTEN), 1(WRITTEN)
    # hashtable = {
    #             # "pg_id1":[("osd_id1", write_status), ("osd_id2", write_status), ("osd_id3", write_status)],
    #             # "pg_id2":[("osd_id4", write_status), ("osd_id5", write_status), ("osd_id6", write_status)]
    #              }

    ## status = 0(ALIVE), 1(DOWN), 2(OUT)
    # cluster_topology = {
    #                     "osd_id1":
    #                     {
    #                         "ip":'blah',
    #                         "port":1211,
    #                         "free_space":100,
    #                         "status":0,               
    #                         "friends":{}
    #                     },

    #                     "osd_id2":
    #                     {
    #                         "ip":'blah',
    #                         "port":1211,
    #                         "free_space":100,
    #                         "status":0,
    #                         "friends":{}
    #                     },

    #                     "osd_id3":
    #                     {
    #                         "ip":'blah',
    #                         "port":1211,
    #                         "free_space":100,
    #                         "status":0,
    #                         "friends":{}
    #                     } 
    #                 }

    global hashtable, cluster_topology

    hashtable_file = open('hashtable', 'r+b')
    hashtable_dump = hashtable_file.read()
    hashtable = pickle.loads(hashtable_dump)

    cluster_topology_file = open('cluster_topology', 'r+b')
    cluster_topology_dump = cluster_topology_file.read()
    cluster_topology = pickle.loads(cluster_topology_dump)

    hashtable_file.close()
    cluster_topology_file.close()


    ## THREADS
    # write_acks_thread             : receives write acks from osds
    # client_reqs_thread            : receives client reqs from the client and
    #                                 sends back the osds' addresses
    # osd_inactive_status_thread    : receives the osd_ids which are inactive

    write_acks_thread = threading.Thread(target=recv_write_acks)
    client_reqs_thread = threading.Thread(target=recv_client_reqs)
    osd_inactive_status_thread = threading.Thread(target=recv_inactive_osd)

    # starting the threads
    write_acks_thread.start()
    client_reqs_thread.start()
    osd_inactive_status_thread.start()

    # closing the threads
    write_acks_thread.join()
    client_reqs_thread.join()
    osd_inactive_status_thread.join()

if __name__ == '__main__':
	main()