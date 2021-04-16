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

my_osd_id = 0
freespace = 

def recv_client_reqs():
	global my_osd_id
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
			
		if(req["type"] == "CLIENT_WRITE"):
			
			client_id = req["client_id"]
			client_addr = req["client_addr"]

			osd_dict = req["osd_dict"]

			for osd_id in osd_dict["osd_ids"]:
				if osd_id == my_osd_id:
					continue

				# sending write update to client
				write_forward_socket = socket.socket()
				print ("write forward socket successfully created")
				
				write_forward_socket.connect(osd_dict["addrs"][osd_id])

				req["type"] = "OSD_WRITE"

				_send_msg(write_forward_socket, req)

				write_forward_socket.close()

			pg = req["pg"]
			file = open("./data/"+pg.pg_id, 'wb')

			pg_dump = pickle.dumps(pg)
			file.write(pg_dump)

			file.close()

			# sending write ack to monitor
			write_ack_socket = socket.socket()
			print ("write forward socket successfully created")
			
			write_ack_socket.connect(monitor_addr)
			ack = {}
			ack["client_id"] = client_id
			ack["client_addr"] = client_addr # addr = (ip, port)
			ack["pg_id"] = pg.pg_id
			ack["free_space"] = freespace - sys.getsizeof(pg_dump)
			ack["osd_id"] = my_osd_id

			_send_msg(write_ack_socket, ack)

			write_ack_socket.close()
			
			# _send_msg(c, [pg.pg_id, "SUCCESS"])
		
		elif msg["type"] == "OSD_WRITE":
			client_id = req["client_id"]
			client_addr = req["client_addr"]

			pg = req["pg"]
			file = open("./data/"+pg.pg_id, 'wb')

			pg_dump = pickle.dumps(pg)
			file.write(pg_dump)

			file.close()

			# sending write ack to monitor
			write_ack_socket = socket.socket()
			print ("write forward socket successfully created")
			
			write_ack_socket.connect(monitor_addr)
			ack = {}
			ack["client_id"] = client_id
			ack["client_addr"] = client_addr # addr = (ip, port)
			ack["pg_id"] = pg.pg_id
			ack["free_space"] = freespace - sys.getsizeof(pg_dump)
			ack["osd_id"] = my_osd_id

			_send_msg(write_ack_socket, ack)

			write_ack_socket.close()
			
		elif msg["type"] == "READ":
			pg_id = msg["pg_id"]
			file = open("./data/"+pg_id, 'rb')

			pg_b = file.read()
			pg = pickle.loads(pg_b)

			file.close()
			# print(pg)
			msg = {"pg_id": pg.pg_id, "res":"SUCCESS", "pg":pg}

			_send_msg(c, msg)

		c.close()

		print(msg)

	s.close()

def main(argc, argv):
	if argc < 2:
		print("error: python3 <filename> <osd_id>")

	global osd_id
	my_osd_id = argv[1]

	# friends structure
	# friends = {
	# 			 "osd_id1" : {
	# 							"addr" : (ip, port),
							  	# "status" : 0
							#  }
	# 			 "osd_id2" : {
	# 							"addr" : (ip, port),
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
	main(len(sys.argv), sys.argv)
