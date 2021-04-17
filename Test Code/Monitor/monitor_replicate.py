import socket
import pickle
import time
from transfer import _send_msg, _recv_msg, _wait_recv_msg
from info import mds_ip, monitor_ip, storage_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE


def send_replicate_request(pg_id, master_osd, clone_osd):
	soc = socket.socket() 
	soc.settimeout(5)        
	print(f"Socket successfully created for replicating {pg_id} from master {master_osd} to clone {clone_osd}")
	  
	# reserve a port on your computer in our 
	ip_add = storage_ip[master_osd]["ip"] 
	port =  storage_ip[master_osd]["port"] + 10    
	
	flag = -1
	try :
		soc.connect((ip_add, port))	
		soc.settimeout(None)

		print(f"Connecting with {master_osd} on port {port}...")
		
		res = {"type": "REPLICATE", "pg_id" : pg_id, "osd_id" : clone_osd}
		_send_msg(soc, res)
		print("Message send for replication ")

		# time.sleep(5)
		
		msg = _wait_recv_msg(soc, MSG_SIZE)
		print(msg)
		if msg == None:
			flag = 0
		elif msg["type"] == "ACK": 
			flag = 1

	except Exception as e: 
		print(e)
		print(f"Didn't Connect! [Timeout] master {master_osd} is down,  port {port}")

	soc.close()
	return flag

	# flag = -1 : didn't connected with the master osd
	# flag = 0 : didn't recieve ack for replication
	# flag = 1 : sucessfully replicated



def replicate(pg_id, osd_id_master_list, osd_id_clone_dict):
	add_entry = []
	for clone in osd_id_clone_dict:
		if osd_id_clone_dict[clone] == True:

			for master in osd_id_master_list:
				ret = send_replicate_request(pg_id, master, clone)

				if ret == 1:
					# Update the hashtable 
					add_entry.append([clone, True])
					break
				elif ret == -1:
					print("may try send_replicate_request again or continue to next master")
					# may try send_replicate_request again
					# or continue to next master
					continue
				elif ret == 0:
					print("eans master osd server break before sending the ack")
					# means master osd server break before sending the ack
					continue
				else:
					print("Some other shit happened in send_replicate_request()")

	return add_entry
	# This add entry we have to append to the hashtable along side the current pg_id


'''
osd_id : will be the osd that is down currently
hashtable : Monitor's dict() from pg_id ---> (replicated osd, write_status)
live_osd :  dict() osd_id --> status (True for live and False for not)
replication_factor : how many replicas does the pg_id is replicated to 
					 this will typically have how many entries 
					 hastable[any_pg_id] does have
''' 
def recovery(crash_osd_id, hashtable, live_osd, replication_factor):
	#Will start the recovery protocol
	rf = replication_factor
	
	# Check the hashtable for pg_id dependency 
	new_hashtable = hashtable
	for pg_id in hashtable.keys():
		list_of_replicated_osds = hashtable[pg_id]
		list_of_master = []
		clone_osd = live_osd

		flag = 0
		for i in range(0, rf):
			osd = list_of_replicated_osds[i][0]
			status = list_of_replicated_osds[i][1]
			if crash_osd_id == osd and status == True:
				flag = 1
			else:
				list_of_master.append(osd)
				clone_osd[osd] = False 
				# As it has the pg_id so no need to clone here


		if flag == 1:
			new_entries = replicate(pg_id, list_of_master, clone_osd)
			# As we set most of the osd that has the pg_id as False
			# Thus clone_osd dict() will only have the osd that are live and 
			# don't have that pg_id which was there is crashed node "crash_osd_id"

			for entry in new_entries:
				new_hashtable[pg_id].append(entry)


	return new_hashtable