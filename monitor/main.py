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
from object_pg import DataObject, PlacementGroup
from monitor.monitor_gossip import heartbeat_protocol

def recv_write_acks():
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

        # Establish connection with client.
        c, addr = s.accept()
        print ('Got connection from', addr)

        # recv the acknowledgement
        ack = _recv_msg(c, 1024)
        print(ack)

        pg_id = ack["pg_id"]
        free_space = ack["free_space"]
        osd_id = ack["osd_id"]
        
        hashtable_file = open('hashtable', 'r+b')
        hashtable_dump = hashtable_file.read()
        hashtable = pickle.loads(hashtable_dump)

        cluster_topology_file = open('cluster_topology', 'r+b')
        cluster_topology_dump = cluster_topology_file.read()
        cluster_topology = pickle.loads(cluster_topology_dump)

        hashtable[pg_id][1] = 1

        for osd in hashtable[pg_id]:
            if osd[0] != osd_id:
                if osd[1] == 1:
                    cluster_topology[osd_id]["friends"].add(osd[0])
                    cluster_topology[osd[0]]["friends"].add(osd_id)

        cluster_topology[osd_id]["free_space"] = free_space

        hashtable_dump = pickle.dumps(hashtable)
        hashtable_file.write(hashtable_dump)
        hashtable_file.close()

        cluster_topology_dump = pickle.dumps(cluster_topology)
        cluster_topology_file.write(cluster_topology_dump)
        cluster_topology_file.close()

        # send to the MDS
        c.send("SUCCESS")

        c.close()

    s.close()
    # Close the connection with the client
    #c.close()


def recv_inactive_osd():
    s = socket.socket()
    print ("inactive osd listener socket successfully created")

    # reserve a port on your computer in our
    # case it is 1234 but it can be anything
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
        # recovery(osd)


def recv_client_reqs():
    s = socket.socket()
    print ("client req listener socket successfully created")

    # reserve a port on your computer in our
    # case it is 1234 but it can be anything
    port = 1236

    # Next bind to the port
    # we have not entered any ip in the ip field
    # instead we have inputted an empty string
    # this makes the server listen to requests
    # coming from other computers on the network
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
        
        # recv the inactive osd
        req_msg = _recv_msg(c, 1024)
        req = pickle.loads(req_msg)

        hashtable_file = open('hashtable', 'r+b')
        hashtable_dump = hashtable_file.read()
        hashtable = pickle.loads(hashtable_dump)

        cluster_topology_file = open('cluster_topology', 'r+b')
        cluster_topology_dump = cluster_topology_file.read()
        cluster_topology = pickle.loads(cluster_topology_dump)

        if(req["type"] == "WRITE"):
            pg_id = req["pg_id"]
            size = req["size"]
            hashtable[pg_id] = []

            i = 0
            for osd_id in cluster_topology:
                if(i>2):
                    break
                if cluster_topology[osd_id]["free_space"] > size:
                    hashtable[pg_id].append((osd_id, 0))
                    i = i+1
            
            osd_ids = [hashtable[pg_id][i][0] for i in range(3)]
            addrs = [(cluster_topology[osd_id]["ip"], cluster_topology[osd_id]["port"]) \
                            for osd_id in osd_ids]
            osds_dict = {"osd_ids": osd_ids, "addrs": addrs}
            _send_msg(c, osds_dict)

            hashtable_dump = pickle.dumps(hashtable)
            hashtable_file.write(hashtable_dump)

        elif req["type"] == "READ":
            pg_id = req["pg_id"]
            osd_ids = [hashtable[pg_id][i][0] for i in range(3)]
            addrs = [(cluster_topology[osd_id]["ip"], cluster_topology[osd_id]["port"]) \
                            for osd_id in osd_ids]
            osds_dict = {"osd_ids": osd_ids, "addrs": addrs}
            _send_msg(c, osds_dict)

        c.close()
        hashtable_file.close()
        cluster_topology_file.close()
            

def main():
    hashtable = {
                # "pg_id1":[("osd_id1", 0), ("osd_id2", 0), ("osd_id3", 0)],
                # "pg_id2":[("osd_id4", 0), ("osd_id5", 0), ("osd_id6", 0)]
                 }
    hashtable_dump = pickle.dumps(hashtable)
    hashtable_file = open('hashtable', 'wb')
    hashtable_file.write(hashtable_dump)
    hashtable_file.close()

    cluster_topology = {
                        "osd_id1":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "status":0,
                            "friends":{}
                        },

                        "osd_id2":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "status":0,
                            "friends":{}
                        },

                        "osd_id3":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "status":0,
                            "friends":{}
                        },

                        "osd_id4":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "status":0,
                            "friends":{}
                        },

                        "osd_id5":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "status":0,
                            "friends":{}
                        },

                        "osd_id6":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "status":0,
                            "friends":{}
                        },  
                    }
    cluster_topology_dump = pickle.dumps(cluster_topology)
    cluster_topology_file = open('cluster_topology', 'wb')
    cluster_topology_file.write(cluster_topology_dump)
    cluster_topology_file.close()

    write_acks_thread = threading.Thread(target=recv_write_acks)
    client_reqs_thread = threading.Thread(target=recv_client_reqs)
    osd_inactive_status_thread = threading.Thread(target=recv_inactive_osd)

    write_acks_thread.start()
    client_reqs_thread.start()
    osd_inactive_status_thread.start()

    write_acks_thread.join()
    client_reqs_thread.join()
    osd_inactive_status_thread.join()
    #HEADERSIZE = 10


if __name__ == '__main__':
	main()