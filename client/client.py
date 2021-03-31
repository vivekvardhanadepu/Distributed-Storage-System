import gui
from info import mds_ip, monitor_ip, num_objects_per_file, max_num_objects_per_pg, MSG_SIZE, HEADERSIZE
from object_pg import DataObject, PlacementGroup 
from transfer import _send_msg, _recv_msg

import socket
import sys
import pickle

#%%

class Client:
    client_id = None
    
    latest_file_id = 1
    dir_tree = {}
    curr_dir = "dir1"
    logged_in = False
    
    def __init__(self, client_id):
        self.client_id = client_id
        self.gui = gui.GUI()
    
    def login(self):
        #self.client_id = "C200"
        self.latest_file_id = 0
        self.dir_tree = {
            "dir1":{0:["C200_0_PG0"]},
            "dir2":{}
            }
        
        self.logged_in = True
    
    def upload(self, file_name):
        if not self.logged_in:
            self.gui._print("Not logged in")
            return 
        
        file_id, pg_list = self._chunker(file_name)
        
        ## send to OSD using sockets ; ask IP to monitor
        ## using _write function
        
        res = -1
        for pg in pg_list:
            while res == -1:
                res = self._write(pg)
                if res == -2:
                	print("UPLOAD failed")
            res = -1
        
        self.dir_tree[self.curr_dir][file_id] = [file_name, [pg.pg_id for pg in pg_list]]
        
        print(self.dir_tree)
        self.gui._print("[UPLOAD]", "Succesful")
    
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
        self.gui._print("[DOWNLOAD]", "Succesful")


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
        
        msg = {"type":"UPLOAD", "PG_id":pg.pg_id}
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
        data_msg = {"type":"WRITE", "PG":pg}
        _send_msg(s, data_msg)
        
        osd_response = _recv_msg(s, 1024)
        
        if osd_response[0] == pg.pg_id and osd_response[1] == "SUCCESS":
            return 0
        
        else:
            return -2
    
    def _chunker(self, file_name):
        file = open(file_name, 'rb')
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
    
    
#w = window()

client = Client("C200")
client.login()

# client.upload("myFile.txt")
client.upload("kS.png")

client.download(1)
# #%%
# msg = {"foriio":1223,"hjsdfj":556}
# msg = pickle.dumps(msg)
# s = f"{len(msg):<{HEADERSIZE}}"

# print(len(s))

# print(s)