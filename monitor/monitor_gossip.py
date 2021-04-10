import socket
import pickle
from transfer import _send_msg, _recv_msg
from info import mds_ip, monitor_ip, storage_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE

def __init__():

	#This will help us to know if the storage is alive or not
	for i in range(4):
		self.storage_node[i] = True


def recovery():
	#Will start the recovery protocol
	pass

def gossip(c, msg):
	node_ip = msg["ip"]

	i = 0
	for node in storage_ip:
		if node["ip"] == node_ip:
			self.storage_node[i] = False

			print(f"Need to start the recovery protocol for {node_ip} storage node number {i+1}")
			recovery()

			break

		i += 1

	res = {"type": "ACK"}
	_send_msg(c, res)


def heartbeat_protocol(soc):
	# Establish connection with client. 
	c, addr = s.accept()     
	c.settimeout(5)
	print ('Got connection from', addr )
	
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
		gossip(c, msg)
		
	c.close()



if __name__ == "__main__":
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
	print ("socket is listening")            
	  
	# a forever loop until we interrupt it or 
	# an error occurs 
	while True: 
	  
		heartbeat_protocol(s)
		
	s.close()
	# Close the connection with the client 
	#c.close()