import pickle
MSG_SIZE = 4096
# class RW:
# 	def __init__(self):
# 		pass

def _send_msg(socket, msg):
	msg = pickle.dumps(msg)
	socket.send(msg)

def _wait_recv_msg(socket, size):
	rec_packet = []
	i = 0
	print("Waiting packet..")
	while True:
		try :
			socket.settimeout(8)
			msg = socket.recv(MSG_SIZE)
			# socket.settimeout(None)
			print(".")
			
			if not msg:
				break

			rec_packet.append(msg)

		except Exception as e:
			print(e)
			break

	print("Joining packet..")
	data = b"".join(rec_packet)

	if not data:
		return None
	
	r_msg = pickle.loads(data)
	# print(r_msg)

	return r_msg

def _recv_msg(socket, size):
	rec_packet = []
	i = 0
	print("Waiting packet..")
	while True:
		try :
			socket.settimeout(1)
			msg = socket.recv(MSG_SIZE)
			# socket.settimeout(None)
			print(".")
			
			if not msg:
				break

			rec_packet.append(msg)

		except Exception as e:
			print(e)
			break
		
	
	print("Joining packet..")
	data = b"".join(rec_packet)

	if not data:
		return None
	
	r_msg = pickle.loads(data)
	# print(r_msg)

	return r_msg
