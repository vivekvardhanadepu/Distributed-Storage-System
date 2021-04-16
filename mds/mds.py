from info import mds_ip, monitor_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE
from object_pg import DataObject, PlacementGroup 
from transfer import _send_msg, _recv_msg

from threading import Thread
import socket
import sys
import pickle

class MetadataServ:
	mds_socket = None
	# cluster_socket = None
	# client_socket = None

	mds_port = None
	# cluster_port = mds_ip["primary"]["cluster_req_port"]
	# client_port = mds_ip["primary"]["client_req_port"]

	user_list = None
	logged_in = []
	is_primary = True

	def __init__(self):
		# mds_port = 0
		if self.is_primary == True:
			self.mds_port = mds_ip["primary"]["port"]
		else:
			self.mds_port = mds_ip["backup"]["port"]

		self.mds_socket = socket.socket()
		self.mds_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		self.mds_socket.bind(('', self.mds_port))         
		self.mds_socket.listen(5)

		# self.cluster_socket = socket.socket()
		# self.cluster_socket.bind(('', self.cluster_port))         
		# self.cluster_socket.listen(5)

		# self.client_socket = socket.socket()
		# self.client_socket.bind(('', self.client_port))         
		# self.client_socket.listen(5)

		self.user_list = self._read_user_list()
		self.logged_in = self._read_logged_in()
		# Thread(target=self.login_handle).start()
		# Thread(target=self.update_handle).start()
		# Thread(target=self.client_handle).start()
		

		if self.is_primary == True:
			print("Metadata Server Running (Primary)... ")
			self.dispatch_primary()

		else:
			print("Metadata Server Running (Backup)... ")
			self.dispatch_backup()

	def register_new_client(self):
		pass

	def dispatch_primary(self):
		while True: 
			# Establish connection with client. 
			print("waiting for messages..")
			c, addr = self.mds_socket.accept()

			print ('Got connection from', addr )
			 
			msg = {}

			try:
				msg = _recv_msg(c, MSG_SIZE)
			except Exception as e:
				print(e)
				c.close()
				continue
			
			res = {}
			print(msg)
			
			if msg["type"] == "CLIENT_LOGIN":
				res = self._login_handle(msg)
				print(res["msg"])

			elif msg["type"] == "CLIENT_LOGOUT":
				res = self._logout_handle(msg)
				print(res["msg"])
			
			try:
				_send_msg(c, res)
			except Exception as e:
				print(e)
			finally:
				c.close()

	def dispatch_backup(self):
		while True: 
			# Establish connection with client. 
			print("waiting for messages..")
			c, addr = self.mds_socket.accept()

			print ('Got connection from', addr )
			 
			msg = {}

			try:
				msg = _recv_msg(c, MSG_SIZE)
			except Exception as e:
				print(e)
				c.close()
				continue

			res = {"status":"", "msg":""}
			print(msg)
			
			if msg["type"] == "UPD":
				if msg["update_type"] == "ADD_LOGIN_USER":
					self.logged_in.append(msg["update"]["user"])
					self._write_logged_in()
					res["status"] = "SUCCESS"

				elif msg["update_type"] == "REMOVE_LOGIN_USER":
					self.logged_in.remove(msg["update"]["user"])
					self._write_logged_in()
					res["status"] = "SUCCESS"

			else:
				res["status"] = "ERROR"
				res["msg"] = "msg type not define !"
			
			try:
				_send_msg(c, res)
			except Exception as e:
				print(e)
			finally:
				c.close()

	def update_handle(self): # update will come from Monitor in cluster
		pass

	def client_handle(self): # handle for logged in clients
		# while True: 
		# 	# Establish connection with client. 
		# 	c, addr = self.client_socket.accept()     
		# 	print ('Got Msg from Client ', addr )
			  
		# 	msg = _recv_msg(c, MSG_SIZE)
			
		# 	print(msg)
			
				
			
		# 	_send_msg(c, res)
		# 	c.close()
		pass
	def _login_handle(self, msg):
		res = {"status":"", "tree": "", "msg": ""}

		if msg["username"] == None or msg["password"] == None:
			res["status"] = "ERROR"
			res["msg"] = "Username or password not provided !"
			

		else:
			username = msg["username"]
			passwd = msg["password"]
			if username in self.user_list.keys():
				if self.user_list[username] == passwd:
					tree = self._read_tree(username)
					
					if username not in self.logged_in:
						# self.logged_in.append(username)
						update = {"user":username}
						r = self._update_primary("ADD_LOGIN_USER", update)
						if r == 0:
							res["status"] = "SUCCESS"
							res["tree"] = tree
							res["msg"] = "logged in successfull"
							# print("Successfully updated on Backup")

						else:
							self.logged_in.append(update["user"])
							self._write_logged_in()
							res["status"] = "SUCCESS"
							res["tree"] = tree
							res["msg"] = "logged in successfull"
							# print("Couldn't update on Backup")
					else:
						res["status"] = "SUCCESS"
						res["tree"] = tree
						res["msg"] = "Already logged in"
					# print(tree, "ONNN")

				else:
					res["status"] = "ERROR"
					res["tree"] = None
					res["msg"] = "Incorrect Password"

			else:
				res["status"] = "ERROR"
				res["tree"] = None
				res["msg"] = "Incorrect Username"

		return res

	def _logout_handle(self, msg):
		res = {"status":"", "tree": "", "msg": ""}

		# self.logged_in.remove(msg["username"])
		update = {"user":msg["username"]}
		r = self._update_primary("REMOVE_LOGIN_USER", update)
		if r != 0:
			self.logged_in.remove(msg["username"])
			self._write_logged_in()
		# print("Logout successfull")
		res["status"] = "SUCCESS"
		res["msg"] = "log out successfull"

		return res

	def _update_primary(self, update_type, update):
		print("writing to backup..")
		s = socket.socket()         
		
		# send backup mds to make data consistent
		ip = mds_ip["backup"]["ip"]
		port = mds_ip["backup"]["port"]                
		 
		try:
			s.connect((ip, port)) 
			
			msg = {"type":"UPD", "update_type":update_type, "update":update}
			# d_msg = pickle.dumps(msg)
			
			_send_msg(s, msg)
			#s.send(d_msg)
			response = _recv_msg(s, 1024)

			if response["status"] == "SUCCESS":
				if update_type == "ADD_LOGIN_USER":
					self.logged_in.append(update["user"])
					self._write_logged_in()
					

				elif update_type == "REMOVE_LOGIN_USER":
					self.logged_in.remove(update["user"])
					self._write_logged_in()
					

				print("Successfully updated on Backup")
				return 0
			elif response["status"] == "ERROR":
				print(response["msg"])
				print("Couldn't update on Backup")
				return -1

		except Exception as e:
			print(e)
			print("Couldn't update on Backup")
			return -2

		finally:
			s.close()
			print("writing to backup completed.")



	def _read_tree(self, username):
		file = open("./tree/"+username, 'rb')

		tree_b = file.read()
		tree = pickle.loads(tree_b)

		file.close()

		return tree

	def _delete_tree(self, client_id):
		pass

	def _read_user_list(self):
		file = open("./user_list", 'rb')

		obj_b = file.read()
		user_list = pickle.loads(obj_b)

		file.close()

		return user_list

	def _read_logged_in(self):
		file = open("./logged_in", 'rb')

		obj_b = file.read()
		logged_in = pickle.loads(obj_b)

		file.close()

		return logged_in

	def _write_logged_in(self):
		file = open("./logged_in", 'wb')

		obj_b = pickle.dumps(self.logged_in)
		file.write(obj_b)

		file.close()


if __name__ == "__main__":
	mds = MetadataServ()