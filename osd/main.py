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
import shutil

sys.path.insert(1, '../utils/')
from transfer import _send_msg, _recv_msg
# from storage_gossip import heartbeat_protocol
from info import READ_WRITE_PORT, WRITE_ACK_PORT, MONITOR_IPs

MY_OSD_ID = 0
FREESPACE = 0
MONITOR_IP = MONITOR_IPs["primary"]

def heartbeat_protocol():
	pass

def recv_client_reqs():
	global MY_OSD_ID

	recv_client_reqs_socket = socket.socket()
	print("client reqs socket successfully created")
	recv_client_reqs_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	# reserve a port on your computer
	port = READ_WRITE_PORT

	# Next bind to the port
	# we have not entered any ip in the ip field
	# instead we have inputted an empty string
	# this makes the server listen to requests
	# coming from other computers on the network
	recv_client_reqs_socket.bind(('', port))
	print ("write ack socket bound to %s" %(port))

	# put the socket into listening mode
	recv_client_reqs_socket.listen(5)
	print ("socket is listening")

	# a forever loop until we interrupt it or
	# an error occurs
	while True:

		# Establish connection with client.
		c, addr = recv_client_reqs_socket.accept()
		print ('Got connection from', addr)

		# recv the acknowledgement
		req = _recv_msg(c, 1024)
		print(req)
			
		if(req["type"] == "CLIENT_WRITE"):
			res = {"status":"RECEIVED", "msg":"data received"}
			_send_msg(c,res)

			client_id = req["client_id"]
			# client_addr = req["client_addr"]

			osd_dict = req["osd_dict"]

			for osd_id in osd_dict["osd_ids"]:
				if osd_id == MY_OSD_ID:
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
			
			write_ack_socket.connect((MONITOR_IP, WRITE_ACK_PORT))
			ack = {}
			ack["client_id"] = client_id
			# ack["client_addr"] = client_addr # addr = (ip, port)
			ack["pg_id"] = pg.pg_id
			ack["free_space"] = FREESPACE - req["size"]
			ack["osd_id"] = MY_OSD_ID

			_send_msg(write_ack_socket, ack)

			write_ack_socket.close()
			
			# _send_msg(c, [pg.pg_id, "SUCCESS"])
		
		elif req["type"] == "OSD_WRITE":
			client_id = req["client_id"]
			# client_addr = req["client_addr"]

			pg = req["pg"]
			file = open("./data/"+pg.pg_id, 'wb')

			pg_dump = pickle.dumps(pg)
			file.write(pg_dump)

			file.close()

			# sending write ack to monitor
			write_ack_socket = socket.socket()
			print ("write forward socket successfully created")
			
			write_ack_socket.connect((MONITOR_IP, WRITE_ACK_PORT))
			ack = {}
			ack["client_id"] = client_id
			# ack["client_addr"] = client_addr # addr = (ip, port)
			ack["pg_id"] = pg.pg_id
			ack["free_space"] = FREESPACE - sys.getsizeof(pg_dump)
			ack["osd_id"] = MY_OSD_ID

			_send_msg(write_ack_socket, ack)

			write_ack_socket.close()
			
		elif req["type"] == "READ":
			pg_id = req["pg_id"]
			file = open("./data/"+pg_id, 'rb')

			pg_b = file.read()
			pg = pickle.loads(pg_b)

			file.close()
			# print(pg)
			print("sending pg to client "+str(pg_id))
			msg = {"pg_id": pg.pg_id, "res":"SUCCESS", "pg":pg}

			_send_msg(c, msg)

		c.close()

		# print(msg)

	recv_client_reqs_socket.close()

def main(argc, argv):
	if argc < 2:
		print("usage: python3 osd.py <osd_id>")
		exit(-1)

	global MY_OSD_ID, FREESPACE
	MY_OSD_ID = int(argv[1])
	_, _, FREESPACE = shutil.disk_usage('/')
	FREESPACE = FREESPACE // float(1<<20)
	print(FREESPACE)
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

	# starting the threads
	client_reqs_thread.start()
	heartbeat_thread.start()

	# closing the threads
	client_reqs_thread.join()
	heartbeat_thread.join()
	
if __name__ == '__main__':
	main(len(sys.argv), sys.argv)
