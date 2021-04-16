import socket
import pickle
import os
from transfer import _send_msg, _recv_msg, _wait_recv_msg
from info import mds_ip, monitor_ip, storage_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE

from monitor_replicate import recovery


def gossip(c, msg, live_osd):
	node_ip = msg["ip"]
	crash_osd_id = msg["osd_id"]

	if live_osd[crash_osd_id] == False:
		return 
	
	print(f"Need to start the recovery protocol for {node_ip} {crash_osd_id}")

	hashtable = {"pg_id1":[("osd_id1", True), ("osd_id2", True), ("osd_id4", True)]}
	# Use this in maincode
	# hashtable_file = open('hashtable', 'rb')
	# hashtable_dump = hashtable_file.read()
	# hashtable = pickle.load(hashtable_dump)
	# hashtable_file.close()


	live_osd[crash_osd_id] = False
	rf = 3

	hastable = recovery(crash_osd_id, hashtable, live_osd, rf)
	print(hashtable)




def heartbeat_protocol(soc, live_osd):
	# Establish connection with client. 
	c, addr = soc.accept()  
	print(f"\nGot connection from {addr}")
	
	n = os.fork()

	if n == 0:
		print(F"Inside child process {os.getpid()}")
		msg = _recv_msg(c, MSG_SIZE)
		print(msg)

		if msg == None:
			print(f"Didn't receive data! [Timeout] {addr}")

		elif msg["type"] == "ALIVE":
			res = {"type": "ACK"}
			_send_msg(c, res)

		elif msg["type"] == "FAIL":
			res = {"type": "ACK"}
			_send_msg(c, res)
			gossip(c, msg, live_osd)
			
		c.close()

		print(f"Exiting from pid {os.getpid()} ..\n")
		os._exit(1)

	return



if __name__ == "__main__":
	# Make sure to maintain this 
	live_osd = {"osd_id1":True, "osd_id2":True, "osd_id3":True, "osd_id4":True}

	s = socket.socket()         
	print ("Socket successfully created")
	  
	# reserve a port on your computer in our 
	port =  monitor_ip["primary"]["port"]       
	  
	# Next bind to the port 
	# we have not typed any ip in the ip field 
	# instead we have inputted an empty string 
	# this makes the server listen to requests 
	# coming from other computers on the network 
	s.bind(('', port))         
	print ("Monitor socket binded to %s" %(port)) 
	  
	# put the socket into listening mode 
	s.listen(5)              
	  
	# a forever loop until we interrupt it or 
	# an error occurs 
	while True: 
	  
		heartbeat_protocol(s, live_osd)
		
	s.close()
	# Close the connection with the client 
	#c.close()