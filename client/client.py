import tkinter as tk 
from tkinter import filedialog
import socket
import sys
import pickle
import os
from functools import partial
import time
import threading

sys.path.insert(1, '../utils/')
from info import MDS_IPs, MONITOR_IPs, CLIENT_REQ_PORT, MSG_SIZE
from object_pg import DataObject, PlacementGroup 
from transfer import _send_msg, _recv_msg, _wait_recv_msg


class Client:
	client_id = None
	
	latest_file_id = 1
	dir_tree = {}
	curr_dir = "root"
	logged_in = False
	
	window_name = "Distributed Storage Service - "

	file_selected = None

	def __init__(self, tree):
		self.client_id = tree["client_id"]
		self.username = tree["username"]
		self.dir_tree = tree["dir_tree"]
		# self.latest_file_id = tree["last_file_id"]
		self.processing = tree["processing"]
		self.logged_in = True
		self.start_update_handler = False # True if some file is processing for upload
		self.update_interval = 2 # 2 sec interval for checking updates on file upload
		# self.write_update_recv = False

		self.gui()
		

	def update_handler(self):

		# if n == 0:
		print("update handler started..")
		if self.start_update_handler == True:

			while True:
				if len(self.processing) == 0:
					self.start_update_handler = False
					break

				msg = {"type":"WRITE_QUERY", "username":self.username, "processing":self.processing}

				s = socket.socket()         
				
				ip = MDS_IPs["primary"]["ip"]
				port = MDS_IPs["primary"]["port"]
				# print(s.gethostname())      
				s.bind(('', 9090))        
				  
				try:
					s.connect((ip, port)) 

					_send_msg(s, msg)
					
					response = _wait_recv_msg(s, MSG_SIZE)

					s.close()
					if response["status"] == "SUCCESS": # here check response from mds
						print(response["msg"])
						file_written = response["file_written"]
						
						for filename in file_written: #populate listbox again
							self.listbox.insert(END, filename)
							# listbox.insert(END, percent)
							self.listbox.update_idletasks()

						for file in file_written:
							self._popup("Update", str(file)+" UPLOADED SUCCESSFULLY")
						
						tree = response["tree"]
						self.dir_tree = tree["dir_tree"]
						self.processing = tree["processing"]
						# update on GUI

						# self._update_canvas()
<<<<<<< Updated upstream
						for filename in file_written: #populate listbox again
							self.listbox.insert(END, filename)
							# listbox.insert(END, percent)
							self.listbox.update_idletasks()
=======
						
>>>>>>> Stashed changes
						# tk.mainloop()
						# self.window.mainloop()
					elif response["status"] == "NO_UPD":
						print(response["msg"])
					time.sleep(self.update_interval)
				

				except Exception as e:
					s.close()
					print("Update (write) from MDS failed")
					print(e)
					time.sleep(self.update_interval)
				

				finally:
					
					time.sleep(self.update_interval)
				


	def upload(self, file_path):
		if not self.logged_in:
			self.gui._print("Not logged in")
			return 
		
		file_id, pg_list = self._chunker(file_path)

		if file_id < 0:
			return

		filename = os.path.basename(file_path)
		## send to OSD using sockets ; ask IP to monitor
		## using _write function
		pg_data = [self.curr_dir, file_id, filename, 0]
		res = -1
		for pg in pg_list:
			while res == -1:
				res = self._write(pg, pg_data)
				if res == -2:
					print("UPLOAD failed")
				elif res == 0:
					print("file sent - waiting for response")
			res = -1
		
		
		# self.dir_tree[self.curr_dir][file_id] = [file_name, [pg.pg_id for pg in pg_list]]
		
		# print(self.dir_tree)
		# self._print("[UPLOAD]", "Succesful")
	
	def download(self, file_id):
		file_name = self.dir_tree[self.curr_dir][file_id][0]
		pg_list = self.dir_tree[self.curr_dir][file_id][1]

		res = -1
		pg = ""
		for pg_id in pg_list:
			while res == -1:
				res, pg = self._read(pg_id)
				if res == -2:
					print("DOWNLOAD failed")

			res = -1
		print(pg.pg_id)
		print(len(pg.object_list))
		for obj in pg.object_list:
			print("pg received..")
			if file_id == obj.file_id:
				data = obj.data
				print("writing file in disk..")
				file = open("downloads/"+file_name, "wb")
				file.write(data)
				file.close()

		# print(self.dir_tree)
		self._popup("Update", "Download Succesful "+str(file_name))


	def _read(self, pg_id):
		s = socket.socket()         
		
		# send monitor to ask for OSD details
		ip = MONITOR_IPs["primary"]
		port = CLIENT_REQ_PORT               
		  
		
		s.connect((ip, port)) 
		
		msg = {"type":"READ", "pg_id":pg_id}
		# d_msg = pickle.dumps(msg)
		
		_send_msg(s, msg)
		#s.send(d_msg)
		response = _wait_recv_msg(s, 1024)
		
		osd_addr = response["addrs"][0]
		
		# print(osd_ips)
		s.close() 
		# print(osd_ips[0][0], osd_ips[0][1])
		# write on OSD
		s = socket.socket()
		s.connect(osd_addr)
		data_msg = {"type":"READ", "pg_id":pg_id}
		_send_msg(s, data_msg)
		
		osd_response = _wait_recv_msg(s, 1024)
		
		# print(osd_response)
		# print(osd_response["pg_id"] == pg_id)
		# print(osd_response["res"] == "SUCCESS")

		if osd_response["pg_id"] == pg_id and osd_response["res"] == "SUCCESS":
			s.close()
			print("PG received from OSD writing on disk")
			return 0, osd_response["pg"]
		
		else:
			s.close()
			print("Error - PG not received from OSD")
			return -2, None
	
	def _write(self, pg, pg_data):
		s = socket.socket()         
		
		# send monitor to ask for OSD details
		ip = MONITOR_IPs["primary"]
		port = CLIENT_REQ_PORT              
		  
		
		s.connect((ip, port)) 
		
		msg = {"type":"WRITE", "pg_id":pg.pg_id, "size":(sys.getsizeof(pg)/float(1<<20))}
		# d_msg = pickle.dumps(msg)
		
		_send_msg(s, msg)
		#s.send(d_msg)
		res = _wait_recv_msg(s, MSG_SIZE)
		osd_dict = {}

		if res["status"] == "SUCCESS":
			osd_dict = res["osd_dict"]

		else:
			print(res["msg"])
			s.close()
			return -2
		# osd_dict = response["osd_dict"]
		
		# print(osd_ips)
		s.close() 
		# print(osd_ips[0][0], osd_ips[0][1])
		# write on OSD
		osd_addr = osd_dict["addrs"][osd_dict["osd_ids"][0]]
		s = socket.socket()
		s.connect(osd_addr)
		data_msg = {"type":"CLIENT_WRITE", "pg":pg,"size":(sys.getsizeof(pg)/float(1<<20)), "client_id":self.username, "client_addr":"", "osd_dict":osd_dict}
		_send_msg(s, data_msg)
		print(len(pg.object_list))
		
		### Add server to receive response 
		osd_response = _wait_recv_msg(s, 1024)
		
		if osd_response["status"] == "RECEIVED":
			print("file sent to OSD")
			self.processing[pg.pg_id] = pg_data
			if self.start_update_handler == False:
				self.start_update_handler = True
				self.update_handler()
				# threading.Thread(target=self.update_handler())
			s.close()
			return 0
		
		else:
			s.close()
			print("Error - File not sent")
			return -2
	
	def _chunker(self, file_path):
		data = None
		try:
			file = open(file_path, 'rb')
			data = file.read()
			file.close()
		except Exception as e:
			print(e)
			return -1, None
		#size = sys.getsizeof(file)
		# print(data)
		file_ids = []
		for d in self.dir_tree.keys():
			for file_id in self.dir_tree[d].keys():
				file_ids.append(file_id)
		file_id = 0
		if len(file_ids) > 0:
			file_id = max(file_ids)+1
		
		object_id = self.client_id+"_"+str(file_id)+"_OBJ"+str(0)
		object_index = 0
		
		obj = DataObject(file_id, object_id, object_index)
		obj.write_data(data)
		
		pg_id = self.client_id+"_"+str(file_id)+"_PG"+str(0)
		pg = PlacementGroup(pg_id)
		
		pg.add_object(obj)
		
		pg_list = [pg]
		
		return file_id, pg_list
	
	def _aggregate(self, file):
		pass

	################### GUI ############################################################
	def gui(self):
		#creating main window and widgets
		self.window = tk.Tk() 
		self.window.configure(background = "grey")
		#getting screen width and height of display 
		self.window_width= self.window.winfo_screenwidth()  
		self.window_height= self.window.winfo_screenheight() 

		# img_w = int((self.window_width-40)/2) -10
		# img_h = self.window_height - 300

		#setting tkinter window size 
		self.window.geometry("%dx%d" % (self.window_width, self.window_height)) 
		self.window.title(self.window_name+self.username) 

		# 1st image path input
		tk.Label(self.window, text='Upload File').place(x = 10, y = 5)
		self.file_entry = tk.StringVar() 
		self.e1 = tk.Entry(self.window, textvariable=self.file_entry, width=60) 
		self.e1.place(x = 110, y = 5)
		
		self.b1 = tk.Button(self.window, text='Select File', width=10, command = self.browseFiles)
		self.b1.place(x = 790, y = 5)

		self.b2 = tk.Button(self.window, text='Upload File', width=10, command = self.upload_file)
		self.b2.place(x = 940, y = 5)

		self.b2 = tk.Button(self.window, text='Log out', width=10, command = self.logout)
		self.b2.place(x = 1200, y = 5)

		self.canvasG = tk.Canvas(self.window, width=self.window_width - 100, height=self.window_height - 300, bg="white") 
		self.canvasG.place(x = 90, y=100)
		self.canvasG.configure(scrollregion=self.canvasG.bbox("all"))
		# # self.canvasG.bind("<Button 1>",selectGlobalCanvas)

		scrollbar = tk.Scrollbar(self.canvasG)
		# scrollbar.place(y=50)
		scrollbar.pack( side = tk.RIGHT,
				fill = tk.Y )
		self.list_item = tk.StringVar()
		# self.canvasG.configure(yscrollcommand=scrollbar.set)
		self.listbox = tk.Listbox(self.canvasG, yscrollcommand = scrollbar.set, width=150, height=30,
							listvariable=self.list_item, selectmode = 'browse' )
		# mylist.place(x = 60, y=50)
		file_list = []
		self.file_id_map = {}
		for d in self.dir_tree.keys():
			for file_id in self.dir_tree[d].keys():
				f_name = self.dir_tree[d][file_id][0]
				file_list.append("/"+str(d)+"/"+str(f_name))
				self.file_id_map[f_name] = file_id

		for file in file_list:
			self.listbox.insert(tk.END, file)

		# mylist.place(x = 60, y=50)#, side = "left", fill = "both")
		self.listbox.pack()#side = tk.LEFT, fill = tk.BOTH )
		self.listbox.bind("<MouseWheel>", self.scrolllistbox)
		self.listbox.bind('<Double-1>', self.download_file)
		

		scrollbar.config( command = self.listbox.yview)


		self.window.mainloop()
	
<<<<<<< Updated upstream
=======
	def _update_gui(self):
		self.canvasG.delete('all')
		scrollbar = tk.Scrollbar(self.canvasG)
		# scrollbar.place(y=50)
		scrollbar.pack( side = tk.RIGHT,
				fill = tk.Y )
		self.list_item = tk.StringVar()
		# self.canvasG.configure(yscrollcommand=scrollbar.set)
		self.listbox = tk.Listbox(self.canvasG, yscrollcommand = scrollbar.set, width=150, height=30,
							listvariable=self.list_item, selectmode = 'browse' )
		# mylist.place(x = 60, y=50)
		file_list = []
		self.file_id_map = {}
		for d in self.dir_tree.keys():
			for file_id in self.dir_tree[d].keys():
				f_name = self.dir_tree[d][file_id][0]
				file_list.append("/"+str(d)+"/"+str(f_name))
				self.file_id_map[f_name] = file_id

		for file in file_list:
			self.listbox.insert(tk.END, file)

		# mylist.place(x = 60, y=50)#, side = "left", fill = "both")
		self.listbox.pack()#side = tk.LEFT, fill = tk.BOTH )
		self.listbox.bind("<MouseWheel>", self.scrolllistbox)
		self.listbox.bind('<Double-1>', self.download_file)
		

		scrollbar.config( command = self.listbox.yview)
>>>>>>> Stashed changes

	def browseFiles(self):
		filename = filedialog.askopenfilename(initialdir = "/",
											title = "Select a File",
											filetypes = (("Text files",
														"*.txt*"),
														("all files",
															"*.*")))
		self.file_entry.set(filename)

	def scrolllistbox(event):
		self.listbox.yview_scroll(int(-4*(event.delta/120)), "units")

	def download_file(self, event):
		selected_index = self.listbox.curselection()
		
		file_path = self.listbox.get(selected_index)
		print(file_path)
		file_name = os.path.basename(file_path)

		self.download(self.file_id_map[file_name])

	def upload_file(self):
		filename = self.file_entry.get()
		self.upload(filename)

	def logout(self):
		msg = {"type":"CLIENT_LOGOUT", "username":self.username}

		s = socket.socket()         
		s.bind(('', 9090))
		ip = MDS_IPs["primary"]["ip"]
		port = MDS_IPs["primary"]["port"]                
		  
		try:
			s.connect((ip, port)) 

			_send_msg(s, msg)
			
			response = _wait_recv_msg(s, MSG_SIZE)


			if response["status"] == "SUCCESS": # here check response from mds
				self.window.destroy()
				print(response["msg"])

			elif response["status"] == "ERROR":
				print(response["msg"])

		except Exception as e:

			print("[ERROR] login failed")
			print(e)

		finally:
			global LoginPage

			s.close()
			LoginPage()



	def _popup(self, title, msg):
		print(title, msg)
		popup = tk.Toplevel()
		popup.wm_title(title)
		label = tk.Label(popup, text=msg)
		label.pack(fill='x', padx=50, pady=5)
		B1 = tk.Button(popup, text="Okay", command = popup.destroy)
		B1.pack()
		popup.mainloop()
	
	
#w = window()

# client = Client("C200")
# client.login()
login_screen=None
user = None
passwd = None

def _popup(title, msg):
		print(title, msg)
		popup = tk.Toplevel()
		popup.wm_title(title)
		label = tk.Label(popup, text=msg)
		label.pack(fill='x', padx=50, pady=5)
		B1 = tk.Button(popup, text="Okay", command = popup.destroy)
		B1.pack()
		popup.mainloop()

def LoginPage():
	global user, passwd, login_screen
	login_screen=tk.Tk()
	user = tk.StringVar()
	passwd = tk.StringVar()
	login_screen.title("Login")

	width= login_screen.winfo_screenwidth()  
	height= login_screen.winfo_screenheight() 

	login_screen.geometry("%dx%d" % (width, height))
	tk.Label(login_screen, text="Please enter login details").pack()
	tk.Label(login_screen, text="").pack()
	tk.Label(login_screen, text="Username").pack()

	 
	
	# login = partial(login, user, passwd, login_screen)  
	username_login_entry = tk.Entry(login_screen, textvariable=user)#, textvariable="username")
	username_login_entry.pack()
	tk.Label(login_screen, text="").pack()
	tk.Label(login_screen, text="Password").pack()
	password__login_entry = tk.Entry(login_screen, textvariable=passwd, show= '*')
	password__login_entry.pack()
	tk.Label(login_screen, text="").pack()
	tk.Button(login_screen, text="Login", width=10, height=1, command=login).pack()
	login_screen.mainloop()

def login():
	global user, passwd, login_screen
	# send credentials to mds and wait for response

	client_id = "C200" # received from mds
	print("username:: ", user.get())
	# print("password:: ", passwd.get())

	msg = {"type":"CLIENT_LOGIN", "username":user.get(), "password":passwd.get()}

	s = socket.socket()         
	
	ip = MDS_IPs["primary"]["ip"]
	port = MDS_IPs["primary"]["port"]
	# print(s.gethostname())      
	s.bind(('', 9090))        
	  
	try:
		s.connect((ip, port)) 

		_send_msg(s, msg)
		
		response = _wait_recv_msg(s, MSG_SIZE)

		s.close()
		if response["status"] == "SUCCESS": # here check response from mds
			print(response["msg"])
			login_screen.destroy()
			client = Client(response["tree"])
			

		elif response["status"] == "ERROR":
			# print(response["msg"])
			_popup("Login Failed", response["msg"])

	except Exception as e:
		s.close()

		print("[ERROR] login failed")
		print(e)
		_popup("Login Failed", response["msg"])

	finally:
		print("Exiting login..")
		

if __name__ == '__main__':
	LoginPage()
