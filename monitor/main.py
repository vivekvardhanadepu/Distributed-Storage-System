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
    pass

def recv_osd_inactive_status():
    pass

def recv_client_reqs():
    pass

def main():
    hashtable = {
                "pg_id1":["osd_id1", "osd_id2", "osd_id3"],
                "pg_id2":["osd_id4", "osd_id5", "osd_id6"]
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
                            "friends":['osd_id2', 'osd_id3']
                        },

                        "osd_id2":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "friends":['osd_id1', 'osd_id6']
                        },

                        "osd_id3":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "friends":['osd_id1']
                        },

                        "osd_id4":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "friends":[]
                        },

                        "osd_id5":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "friends":[]
                        },

                        "osd_id6":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "friends":['osd_id2']
                        },  
                    }
    cluster_topology_dump = pickle.dumps(cluster_topology)
    cluster_topology_file = open('cluster_topology', 'wb')
    cluster_topology_file.write(cluster_topology_dump)
    cluster_topology_file.close()

    write_acks_thread = threading.Thread(target=recv_write_acks)
    client_reqs_thread = threading.Thread(target=recv_client_reqs)
    osd_inactive_status_thread = threading.Thread(target=recv_osd_inactive_status)

    write_acks_thread.start()
    client_reqs_thread.start()
    osd_inactive_status_thread.start()

    write_acks_thread.join()
    client_reqs_thread.join()
    osd_inactive_status_thread.join()
    #HEADERSIZE = 10

    # s = socket.socket()
    # print ("Socket successfully created")

    # # reserve a port on your computer in our
    # # case it is 12345 but it can be anything
    # port = 1234

    # # Next bind to the port
    # # we have not typed any ip in the ip field
    # # instead we have inputted an empty string
    # # this makes the server listen to requests
    # # coming from other computers on the network
    # s.bind(('', port))
    # print ("socket binded to %s" %(port))

    # # put the socket into listening mode
    # s.listen(5)
    # print ("socket is listening")

    # # a forever loop until we interrupt it or
    # # an error occurs
    # while True:

    #     # Establish connection with client.
    #     c, addr = s.accept()
    #     print ('Got connection from', addr )

    #     # send a thank you message to the client.
    #     msg = _recv_msg(c, 1024)

    #     print(msg)

    #     res = {"osd_ip":[["127.0.0.1", 12346], ["127.0.0.1", 8090]]}

    #     _send_msg(c, res)

    #     c.close()

    # s.close()
    # # Close the connection with the client
    # #c.close()


if __name__ == '__main__':
	main()