import pickle

# class RW:
# 	def __init__(self):
# 		pass

def _send_msg(socket, msg):
	msg = pickle.dumps(msg)
	socket.send(msg)

def _recv_msg(socket, size):
<<<<<<< HEAD
	msg = socket.recv(1024)
	r_msg = pickle.loads(msg)
=======
	rec_packet = []
	i = 0
	print("Waiting packet..")
	while True:
		try :
			socket.settimeout(5)
			msg = socket.recv(MSG_SIZE)
			# socket.settimeout(None)
			print(".")
			
			if not msg:
				break

			rec_packet.append(msg)

		except :
			break
		
	
	print("Joining packet..")
	data = b"".join(rec_packet)

	if not data:
		return None
	
	r_msg = pickle.loads(data)
	# print(r_msg)

>>>>>>> main
	return r_msg
