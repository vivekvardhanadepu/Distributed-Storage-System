import socket
import pickle
import threading
import time
import os
from transfer import _send_msg, _recv_msg, _wait_recv_msg
from info import mds_ip, monitor_ip, storage_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE

from storage_replication import replicate_pg

STORAGE_ID = "osd_id3"


def report_monitor(node_ip, osd_id):
	flag = 0
	#Will call monitor to state about the down node
	soc = socket.socket()
	soc.settimeout(5)
	print ("Socket successfully created for Recovery: Primary")

	monitor_1 = monitor_ip["primary"]
	
	try :
		soc.connect((monitor_1["ip"], monitor_1["port"]))	
		# soc.timeout(None)

		print(f"Connecting Primary monitor...")
		
		res = {"type": "FAIL", "ip" : node_ip, "osd_id" : osd_id}
		_send_msg(soc, res)
		
		msg = _wait_recv_msg(soc, MSG_SIZE)
		print(msg)
		if msg == None:
			pass
		elif msg["type"] == "ACK": 

			soc.close()
			return

	except Exception as e: 
		print(e)
		print("Didn't Connect! [Timeout] Primary Monitor is Down")

	soc.close()

	soc = socket.socket()
	soc.settimeout(5)
	print ("Socket successfully created for Recovery: Backup")
	

	monitor_2 = monitor_ip["backup"]

	try : 
		soc.connect((monitor_2["ip"], monitor_2["port"]))	
		soc.settimeout(None)			
		print(f"Connecting Backup monitor...")
	
		res = {"type": "FAIL", "ip" : node_ip, "osd_id" : osd_id}
		_send_msg(soc, res)

		msg = _wait_recv_msg(soc, MSG_SIZE)
		print(msg)
		if msg == None:
			pass
		elif msg["type"] == "ACK": 
			return

	except:
		print("MAY GOD HELP US!! WE ARE DOOMED\n\n")

	soc.close()



def recv_gossip():

	while True:
		time.sleep(10)
		# Wait for 10 sec to  run this protocol

		i=0
		for i in range(4):
			curr_osd = "osd_id" + str(i+1)
			if curr_osd != STORAGE_ID:
				node_ip =  storage_ip[curr_osd]["ip"]
				port = storage_ip[curr_osd]["port"]

				soc = socket.socket()
				soc.settimeout(5)
				print(f"\n\nSocket successfully created for Gossip with osd {curr_osd}")
			
				try :
					soc.connect((node_ip, port))
					soc.settimeout(None)

					print(f"Connecting {node_ip} storage node number {curr_osd} port {port}")
					
					msg = {"type": "ALIVE"}
					_send_msg(soc, msg)

					rec = _wait_recv_msg(soc, MSG_SIZE)
					print(msg)
					if rec == None: 
						print(f"Didn't receive data to Storage {curr_osd} ip {node_ip}! [Timeout] ")
						report_monitor(node_ip, curr_osd)

					elif rec["type"] != "ACK": 
						report_monitor(node_ip, curr_osd)
					
				except :	
					print(f"Didn't Connect to Storage {curr_osd} ip {node_ip}! [Timeout]")
					report_monitor(node_ip, curr_osd)
			
				soc.close()	

			time.sleep(3)



def send_heartbeat():
	#This will check for incoming messages 
	#from other nodes and reply 

	s = socket.socket()         
	print ("Socket successfully created for Heartbeat")
	port =  storage_ip[STORAGE_ID]["port"] 
	s.bind(('', port))         
	print ("Socket binded to %s" %(port)) 
	  
	# put the socket into listening mode 
	s.listen(5)     

	while True:
		# Establish connection with client. 
		c, addr = s.accept()     
		print(f"\nGot connection from {addr}")

		n = os.fork()
		if n == 0:
			print(F"Inside child process {os.getpid()}")
			msg = _recv_msg(c, MSG_SIZE)	
			print(msg)

			if msg == None:
				print(f"Didn't receive data from ip {addr}! [Timeout] ")
				report_monitor(addr, None)

			elif msg["type"] == "ALIVE": 
				res = {"type": "ACK"}
				_send_msg(c, res)

			c.close()

			print(f"Exiting from pid {os.getpid()} ..\n\n")
			os._exit(1)


def read_write_pg_replication():
	#This will check for incoming messages 
	#from other nodes to replicate certain data 

	s = socket.socket()         
	print ("Socket successfully created for Read-Write only for replication")
	# As mentioned in the info file 
	# Read/write request will be send on "port + 10"
	port =  storage_ip[STORAGE_ID]["port"] + 10
	s.bind(('', port))         
	print ("Socket binded to %s" %(port)) 
	  
	# put the socket into listening mode 
	s.listen(5)     
	
	while True:
		replicate_pg(s)


if __name__ == "__main__":

	p1 = threading.Thread(target=send_heartbeat)
	p2 = threading.Thread(target=recv_gossip)
	p3 = threading.Thread(target=read_write_pg_replication)
	p1.start()
	p2.start()
	p3.start()