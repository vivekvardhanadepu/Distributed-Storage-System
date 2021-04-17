import sys
sys.path.insert(1, '../utils/')
from info import MDS_IPs, MSG_SIZE
from transfer import _send_msg, _recv_msg, _wait_recv_msg

if len(sys.argv) < 2:
	print("$ recovery.py primary")
	exit(0)
ip = 0
port = 0
if sys.argv[1] == "primary":

	ip = MDS_IPs["backup"]["ip"]
	port = MDS_IPs["backup"]["port"]

else:
	ip = MDS_IPs["primary"]["ip"]
	port = MDS_IPs["primary"]["port"]


print("receiving data..")
s = socket.socket()         

try:
	s.connect((ip, port)) 
	
	msg = {"type":"RECOVERY"}
	# d_msg = pickle.dumps(msg)
	
	_send_msg(s, msg)
	#s.send(d_msg)
	response = _wait_recv_msg(s, 1024)

	if response["status"] == "SUCCESS":
		trees = response["trees"]
		logged_in = response["logged_in"]
		# user_list = response["user_list"]

		for tree in trees:
			file = open("./tree/"+tree["username"], 'wb')

			obj_b = pickle.dumps(tree)
			file.write(obj_b)

			file.close()

		file = open("./logged_in", 'wb')

		obj_b = pickle.dumps(logged_in)
		file.write(obj_b)

		file.close()

		print("Successfully recovered...")
	
	elif response["status"] == "ERROR":
		print(response["msg"])
		print("Couldn't recover")


except Exception as e:
	print(e)
	print("Couldn't recover")
	return -2

finally:
	s.close()
	print("...")