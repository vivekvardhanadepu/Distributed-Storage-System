import socket
import pickle
from transfer import _send_msg, _recv_msg
from info import mds_ip, monitor_ip, storage_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE


def replicate_pg(soc):
	# This will be always true loop that will run in parallel

	c, addr = soc.accept() 
	print ('Got connection from', addr )
	
	msg = _recv_msg(c, MSG_SIZE)
	print(msg)

	if msg == None:
		print(f"Didn't receive data! [Timeout] {addr}")

	elif msg["type"] == "REPLICATE":
		res = {"type": "ACK"}
		_send_msg(c, res)

		# Can do one thing here
		# call the func that act as access this pg_id for the client
		# then call other function that act as send this pg to osd to do a write
		pg_id = msg["pg_id"]
		osd_id = msg["osd_id"]

		'''
		Let me look into Vivek's code and figure out these 
		Or you can just write those functions and I will do the rest
		'''
		
	c.close()
