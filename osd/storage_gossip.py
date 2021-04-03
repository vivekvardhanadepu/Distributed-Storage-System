import socket
import pickle
import multiprocessing
import time
from transfer import _send_msg, _recv_msg
from info import mds_ip, monitor_ip, storage_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE

STORAGE_ID = 1


def recovery(node_ip, node_id):
	#Will call monitor to state about the down node
	soc = socket.socket()
	soc.settimeout(3)

	monitor_1 = monitor_ip["primary"]
	
	try :
		soc.connect(monitor_1["ip"], monitor_1["port"])	
		soc.timeout(None)

		print(f"Connecting Primary monitor...")
		
		res = {"type": "FAIL", "ip" : node_ip, "id" : node_id}
		_send_msg(soc, res)

		try:
			msg = _recv_msg(c, 1024)
			if msg["type"] == "ACK": 
				return
			else:
				pass

		except soc.timeout: # fail after 1 second of no activity
			print("Didn't receive data! [Timeout] Primary Monitor is Down")

	except : 
		print("Didn't receive data! [Timeout] Primary Monitor is Down")

	soc.close()

	soc = socket.socket()
	soc.settimeout(3)

	monitor_2 = monitor_ip["backup"]

	try : 
		soc.connect(monitor_2["ip"], monitor_2["port"])	
		soc.settimeout(None)			
		print(f"Connecting Backup monitor...")
	
		res = {"type": "FAIL", "ip" : node_ip, "id" : node_id}
		_send_msg(soc, res)

		try:
			msg = _recv_msg(c, 1024)
			if msg["type"] == "ACK": 
				return
			else:
				pass

		except soc.timeout: # fail after 1 second of no activity
			print("Didn't receive data! [Timeout] Primary Monitor is Down")

	except:
		print("MAY GOD HELP US!! WE ARE DOOMED")
	
	soc.close()



def gossip():

	while True:
		time.sleep(10)
		# Wait for 10 sec to  run this protocol

		i=0
		for i in range(4):
			node_ip =  storage_ip[i+1]["ip"]
			port = storage_ip[i+1]["port"]

			soc.settimeout(3)
			soc = socket.socket()
			soc.settimeout(None)
			print ("Socket successfully created for Gossip")
		
			try :
				soc.connect((node_ip, port))
				soc.timeout(None)

				print(f"Connecting {node_ip} storage node number {i+1}")
				
				msg = {"type": "ALIVE"}
				_send_msg(soc, msg)

				try:
					rec = _recv_msg(c, 1024)
					if rec["type"] != "ALIVE": 
						recovery(node_ip, i+1)

				except socket.timeout: # fail after 1 second of no activity
					print("Didn't receive data! [Timeout]")
					recovery(node_ip, i+1)
				
			except :	
				print("Didn't receive data! [Timeout]")
				recovery(node_ip, i+1)
			
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