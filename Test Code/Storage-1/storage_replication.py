import socket
import pickle
import os
from transfer import _send_msg, _recv_msg
from info import mds_ip, monitor_ip, storage_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE


def replicate_pg(soc):
	# This will be always true loop that will run in parallel

	c, addr = soc.accept() 
	print (f"Got connection from {addr} to do the replication")

	n = os.fork()

	if n==0:
		msg = _recv_msg(c, MSG_SIZE)
		print(msg)

		if msg == None:
			print(f"Didn't receive data! [Timeout] {addr}")
			msg = {"type":"SEND AGAIN"}
			_send_msg(c, msg)

		elif msg["type"] == "REPLICATE":		
			# Can do one thing here
			# call the func that act as access this pg_id for the client
			# then call other function that act as send this pg to osd to do a write
			pg_id = msg["pg_id"]
			osd_id = msg["osd_id"]

			file = open("./data/"+pg_id, 'rb')

			pg_b = file.read()
			pg = pickle.loads(pg_b)

			## Connect to this osd_id with new socket
			new_soc = socket.socket()
			print(f"Socket created to send request to SAVE data at OSD {osd_id}")

			ip_add = storage_ip[osd_id]["ip"]
			port = storage_ip[osd_id]["port"]

			try :
				new_soc.connect((ip_add, port))
				print(f"Connection made with {ip_add} on {port}")

				msg = {"type":"SAVE", "pg_id":pg_id, "pg": pg}
				_send_msg(new_soc, msg)
				print("Msg send to SAVE the data")

				msg = _wait_recv_msg(new_soc, MSG_SIZE)
				print("Msg received !")

			except Exception as e:
				print(e)

			if msg == None:
				res = {"type": "REPLICATION FAIL"}
				_send_msg(c, res)
				print("Fail Msg send to the monitor")

			elif msg["type"] == "ACK":
				res = {"type": "ACK"}
				_send_msg(c, res)
				print("Success Msg send to the monitor")

			
		elif msg["type"] == "SAVE":
			# This will take request from other osd to save some data
			# This is basic replication strategy 
			pg_id = msg["pg_id"]
			pg = msg["pg"]

			file = open("./data/"+ pg_id, 'wb')

			pg_dump = pickle.dump(pg)
			file.write(pg_dump)

			msg = {"type":"ACK"}
			_send_msg(msg)
			print("Write successful..send back Ack to the master osd")


		else:
			print("[ERROR] Check the code in replication")

		c.close()

		print(f"Exiting from pid os.getpid() ..")
		os._exit(1)
