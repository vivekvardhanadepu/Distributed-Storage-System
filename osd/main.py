"""
@author: Kartik Saini
@author: Harshit Soora
@author: Vivek Vardhan Adepu
@author: Shivang Gupta
@author: Deepak Imandi

"""

import socket
import pickle
import sys
import threading
sys.path.insert('../utils/')
from transfer import _send_msg, _recv_msg
from storage_gossip import heartbeat_protocol

def recv_client_reqs():
	s = socket.socket()
    print ("write ack socket successfully created")

    # reserve a port on your computer in our
    # case it is 1234 but it can be anything
    port = 1250

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
        req = _recv_msg(c, 1024)
        print(req)

		# IP, PORT FROM CLIENT
			
		if(msg["type"] == "WRITE"):
			pg = msg["PG"]
			file = open("./data/"+pg.pg_id, 'wb')

			pg_b = pickle.dumps(pg)
			file.write(pg_b)

			# pickle.dump(pg, file)
			file.close()

			_send_msg(c, [pg.pg_id, "SUCCESS"])

		elif msg["type"] == "READ":
			pg_id = msg["PG_id"]
			file = open("./data/"+pg_id, 'rb')

			pg_b = file.read()
			pg = pickle.loads(pg_b)

			file.close()
			# print(pg)
			msg = {"pg_id": pg.pg_id, "res":"SUCCESS", "PG":pg}

			_send_msg(c, msg)

		c.close()

		print("RECV")
		print(msg)

	s.close()

def main():
	# friends structure
	# friends = {
	# 			 "osd_id1" : {
	# 							"addr" : (ip, port, status),
							  	# "status" : 0
							#  }
	# 			 "osd_id2" : {
	# 							"addr" : (ip, port, status),
							  	# "status" : 0
							#  }
	# 			}

	## THREADS
	# client_reqs_thread	: recv write and read reqs from the client and 
	#						  send success in case of write
	#						  send objects in case of read
	# heartbeat_thread		: runs the heartbeat protocol
	client_reqs_thread = threading.Thread(target=recv_client_reqs)
    heartbeat_thread = threading.Thread(target=heartbeat_protocol)
	



if __name__ == '__main__':
	main()
