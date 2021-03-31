import pickle

# class RW:
# 	def __init__(self):
# 		pass

def _send_msg(socket, msg):
	msg = pickle.dumps(msg)
	socket.send(msg)

def _recv_msg(socket, size):
	msg = socket.recv(1024)
	r_msg = pickle.loads(msg)
	return r_msg