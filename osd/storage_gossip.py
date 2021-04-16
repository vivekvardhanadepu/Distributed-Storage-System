import socket
import pickle
import multiprocessing
import time
from transfer import _send_msg, _recv_msg
from info import MONITOR_IPs, OSD_IPs, HEARTBEAT_PORT, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE

STORAGE_ID = 1


def recovery(node_ip, node_id):
	#Will call monitor to state about the down node
	soc = socket.socket()
	soc.settimeout(5)
	print ("Socket successfully created for Recovery: Primary")

	monitor_1 = MONITOR_IPs["primary"]
	
	try :
		soc.connect((monitor_1["ip"], monitor_1["port"]))	
		soc.timeout(None)

		print(f"Connecting Primary monitor...")
		
		res = {"type": "FAIL", "ip" : node_ip, "id" : node_id}
		_send_msg(soc, res)
		time.sleep(3)
		
		msg = _recv_msg(c, MSG_SIZE)
		if msg == None:
			pass
		elif msg["type"] == "ACK": 
			return

	except : 
		print("Didn't Connect! [Timeout] Primary Monitor is Down")

	soc.close()

	soc = socket.socket()
	soc.settimeout(5)
	print ("Socket successfully created for Recovery: Backup")
	

	monitor_2 = MONITOR_IPs["backup"]

	try : 
		soc.connect((monitor_2["ip"], monitor_2["port"]))	
		soc.settimeout(None)			
		print(f"Connecting Backup monitor...")
	
		res = {"type": "FAIL", "ip" : node_ip, "id" : node_id}
		_send_msg(soc, res)
		time.sleep(3)

		msg = _recv_msg(c, MSG_SIZE)
		if msg == None:
			pass
		elif msg["type"] == "ACK": 
			return

	except:
		print("MAY GOD HELP US!! WE ARE DOOMED\n\n")

	soc.close()



def gossip():

	while True:
		time.sleep(10)
		# Wait for 10 sec to  run this protocol

		i=0
		for i in range(4):
			if i+1 != STORAGE_ID:
				node_ip =  OSD_IPs[i+1]["ip"]
				port = OSD_IPs[i+1]["port"]

				soc = socket.socket()
				soc.settimeout(5)
				print ("Socket successfully created for Gossip")
			
				try :
					soc.connect((node_ip, port))
					soc.settimeout(None)

					print(f"Connecting {node_ip} storage node number {i+1}")
					
					msg = {"type": "ALIVE"}
					_send_msg(soc, msg)
					time.sleep(3)

					rec = _recv_msg(c, MSG_SIZE)
					if rec == None: 
						print(f"Didn't receive data to Storage {i+1} ip {node_ip}! [Timeout] ")
						recovery(node_ip, i+1)

					elif rec["type"] != "ALIVE": 
						recovery(node_ip, i+1)
					
				except :	
					print(f"Didn't Connect to Storage {i+1} ip {node_ip}! [Timeout]")
					recovery(node_ip, i+1)
			
				soc.close()	



def heartbeat_protocol():
	#This will check for incoming messages 
	#from other nodes and reply 

	s = socket.socket()         
	print ("Socket successfully created for Heartbeat")
	port =  HEARTBEAT_PORT
	s.bind(('', port))         
	print ("Socket binded to %s" %(port)) 
	  
	# put the socket into listening mode 
	s.listen(5)     
	print ("Socket is listening") 

	while True:
		# Establish connection with client. 
		c, addr = s.accept()     
		print ('Got connection from', addr )

		
		msg = _recv_msg(c, MSG_SIZE)	

		if msg == None:
			print(f"Didn't receive data from ip {addr}! [Timeout] ")
			recovery(addr, None)

		elif msg["type"] != "ALIVE": 
			res = {"type": "ACK"}
			_send_msg(c, res)

		c.close()


if __name__ == "__main__":

	p1 = multiprocessing.Process(name='p1', target=heartbeat_protocol)
	p2 = multiprocessing.Process(name='p2', target=gossip)
	p1.start()
	p2.start()