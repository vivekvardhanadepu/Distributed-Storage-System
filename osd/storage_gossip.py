import socket
import pickle
import multiprocessing
import time
from transfer import _send_msg, _recv_msg
from info import mds_ip, monitor_ip, storage_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE

STORAGE_ID = 1


def recovery(node_ip, node_id):
	#Will call monitor to state about the down node
	monitor_1 = monitor_ip["primary"]
	soc.connect(monitor_1["ip"], monitor_1["port"])	
	print(f"Connecting Primary monitor...")
	
	res = {"type": "FAIL", "ip" : node_ip, "id" : node_id}
	_send_msg(soc, res)

	try:
		msg = _recv_msg(c, 1024)
		if msg["type"] == "ACK": 
			return
		else:
			pass

	except socket.timeout: # fail after 1 second of no activity
		print("Didn't receive data! [Timeout] Primary Monitor is Down")
		pass

	finally:
		soc.close()


	monitor_2 = monitor_ip["backup"]
	soc.connect(monitor_2["ip"], monitor_2["port"])				
	print(f"Connecting Backup monitor...")
	
	res = {"type": "FAIL", "ip" : node_ip, "id" : node_id}
	_send_msg(soc, res)

	try:
		msg = _recv_msg(c, 1024)
		if msg["type"] == "ACK": 
			return
		else:
			pass

	except socket.timeout: # fail after 1 second of no activity
		print("Didn't receive data! [Timeout] Primary Monitor is Down")
		pass

	finally:
		soc.close()

	print("MAY GOD HELP US!! WE ARE DOOMED")



def gossip():
	soc = socket.socket()
	print ("Socket successfully created for Gossip")

	while True:
		time.sleep(1)
		# Wait for 1/2 min to  run this protocol

		i=0
		for i in range(4):
			node_ip =  storage_ip[i+1]["ip"]
			port = storage_ip[i+1]["port"]
	
			soc.connect((node_ip, port))				
			print(f"Connecting {node_ip} storage node number {i+1}")
			
			res = {"type": "ALIVE"}
			_send_msg(soc, res)

			try:
				msg = _recv_msg(c, 1024)
				if msg["type"] != "ALIVE": 
					recovery(node_ip, i+1)

			except socket.timeout: # fail after 1 second of no activity
				print("Didn't receive data! [Timeout]")
				recovery(node_ip, i+1)

			finally:
				soc.close()
			



def heartbeat_protocol():
	#This will check for incoming messages 
	#from other nodes and reply 

	s = socket.socket()         
	print ("Socket successfully created for Heartbeat")
	port =  storage_ip[STORAGE_ID]["port"] 
	s.bind(('', port))         
	print ("socket binded to %s" %(port)) 
	  
	# put the socket into listening mode 
	s.listen(5)     
	print ("socket is listening") 

	while True:
		# Establish connection with client. 
		c, addr = s.accept()     
		print ('Got connection from', addr )
		  
		# send a thank you message to the client. 
		msg = _recv_msg(c, 1024)
		print(msg)

		if msg["type"] == "ALIVE":
			res = {"type": "ACK"}
			_send_msg(c, res)

		c.close()



if __name__ == "__main__":

	p1 = multiprocessing.Process(name='p1', target=heartbeat_protocol)
	p2 = multiprocessing.Process(name='p2', target=gossip)
	p1.start()
	p2.start()