# import gui
from info import mds_ip, monitor_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE
from object_pg import DataObject, PlacementGroup 
from transfer import _send_msg, _recv_msg

import tkinter as tk 
from tkinter import filedialog
import socket
import sys
import pickle
import os
from functools import partial
#%%

class Client:
	client_id = None
	
	latest_file_id = 1
	dir_tree = {}
	curr_dir = "dir1"
	logged_in = False
	
	window_name = "Distributed Storage Service - "

	file_selected = None

	def __init__(self, tree):
		self.client_id = tree["client_id"]
		self.username = tree["username"]
		self.dir_tree = tree["root"]
		self.latest_file_id = tree["last_file_id"]
		self.logged_in = True
		self.gui()
		
	def upload(self, file_path):
		if not self.logged_in:
			self.gui._print("Not logged in")
			return 
		
		file_id, pg_list = self._chunker(file_path)
		
		## send to OSD using sockets ; ask IP to monitor
		## using _write function
		
		res = -1
		for pg in pg_list:
			while res == -1:
				res = self._write(pg)
				if res == -2:
					print("UPLOAD failed")
			res = -1
		
		file_name = os.path.basename(file_path)
		self.dir_tree[self.curr_dir][file_id] = [file_name, [pg.pg_id for pg in pg_list]]
		
		print(self.dir_tree)
		self._print("[UPLOAD]", "Succesful")
	
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

		for obj in pg.object_list:
			if file_id == obj.file_id:
				data = obj.data
				file = open("downloads/"+file_name, "wb")
				file.write(data)
				file.close()

		# print(self.dir_tree)
		self._print("[DOWNLOAD]", "Succesful")


	def _read(self, pg_id):
		s = socket.socket()         
		
		# send monitor to ask for OSD details
		ip = monitor_ip["primary"]["ip"]
		port = monitor_ip["primary"]["port"]                
		  
		
		s.connect((ip, port)) 
		
		msg = {"type":"DOWNLOAD", "PG_id":pg_id}
		# d_msg = pickle.dumps(msg)
		
		_send_msg(s, msg)
		#s.send(d_msg)
		response = _recv_msg(s, 1024)
		
		osd_ips = response["osd_ip"]
		
		# print(osd_ips)
		s.close() 
		# print(osd_ips[0][0], osd_ips[0][1])
		# write on OSD
		s = socket.socket()
		s.connect((osd_ips[0][0], osd_ips[0][1]))
		data_msg = {"type":"READ", "PG_id":pg_id}
		_send_msg(s, data_msg)
		
		osd_response = _recv_msg(s, 1024)
		
		# print(osd_response)
		# print(osd_response["pg_id"] == pg_id)
		# print(osd_response["res"] == "SUCCESS")

		if osd_response["pg_id"] == pg_id and osd_response["res"] == "SUCCESS":
			return 0, osd_response["PG"]
		
		else:
			return -2, None
	
	def _write(self, pg):
		s = socket.socket()         
		
		# send monitor to ask for OSD details
		ip = monitor_ip["primary"]["ip"]
		port = monitor_ip["primary"]["port"]                
		  
		
		s.connect((ip, port)) 
		
		msg = {"type":"UPLOAD", "PG_id":pg.pg_id, "size":size(pg)}
		# d_msg = pickle.dumps(msg)
		
		_send_msg(s, msg)
		#s.send(d_msg)
		response = _recv_msg(s, MSG_SIZE)
		
		osd_ips = response["osd_ip"]
		
		# print(osd_ips)
		s.close() 
		# print(osd_ips[0][0], osd_ips[0][1])
		# write on OSD
		s = socket.socket()
		s.connect((osd_ips[0][0], osd_ips[0][1]))
		data_msg = {"type":"WRITE", "PG":pg}
		_send_msg(s, data_msg)
		
		osd_response = _recv_msg(s, 1024)
		
		if osd_response[0] == pg.pg_id and osd_response[1] == "SUCCESS":
			return 0
		
		else:
			return -2
	
	def _chunker(self, file_path):
		file = open(file_path, 'rb')
		data = file.read()
		#size = sys.getsizeof(file)
		# print(data)

		file_id = self.latest_file_id+1
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

		# self.download(self.file_id_map[file_name])

	def upload_file():
		filename = self.file_entry.get()
		self.upload(filename)

	def logout(self):
		msg = {"type":"CLIENT_LOGOUT", "username":self.username}

		s = socket.socket()         
		
		ip = mds_ip["primary"]["ip"]
		port = mds_ip["primary"]["port"]                
		  
		try:
			s.connect((ip, port)) 

			_send_msg(s, msg)
			
			response = _recv_msg(s, MSG_SIZE)


			if response["status"] == "SUCCESS": # here check response from mds
				self.window.destroy()

			elif response["status"] == "ERROR":
				print(response["msg"])

		except Exception as e:

			print("[ERROR] login failed")
			print(e)

		finally:
			global LoginPage

			s.close()
			LoginPage()



	def _print(self, title, msg):
		print(title, msg)
	
	
#w = window()

# client = Client("C200")
# client.login()
login_screen=None
user = None
passwd = None

def LoginPage():
	global user, passwd, login_screen
	login_screen=tk.Tk()
	user = tk.StringVar()
	passwd = tk.StringVar()
	login_screen.title("Login")
	login_screen.geometry("300x250")
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
	
	ip = mds_ip["primary"]["ip"]
	port = mds_ip["primary"]["port"]                
	  
	try:
		s.connect((ip, port)) 

		_send_msg(s, msg)
		
		response = _recv_msg(s, MSG_SIZE)


		if response["status"] == "SUCCESS": # here check response from mds
			print(response["msg"])
			login_screen.destroy()
			client = Client(response["tree"])
			

		elif response["status"] == "ERROR":
			print(response["msg"])

	except Exception as e:

		print("[ERROR] login failed")
		print(e)

	finally:
		print("Exiting login..")
		s.close()

if __name__ == '__main__':
	LoginPage()
