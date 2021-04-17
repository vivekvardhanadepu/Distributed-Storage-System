import pickle
client1 = {
	"username":"client1",
	"client_id":"C1",
	"dir_tree":{
		"root":{},
		"dir1":{0:["text1.txt",["p0"]], 1:["vv.cpp", ["p2"]]}, # dir = {file_id:[file_name, [list of PG ids]]}
		"dir2":{}
	},
	"processing":{} # {"pg_id":["dir","file_id", filename, 0]} 0:waiting 1: writtens
}

client2 = {
	"username":"client2",
	"client_id":"C2",
	"dir_tree":{
		"root":{},
		"dir1":{}, # dir = {file_id:[list of PG ids]}
		"dir2":{}
	},
	"processing":{}
}

client3 = {
	"username":"client3",
	"client_id":"C3",
	"dir_tree":{
		"root":{},
		"dir1":{}, # dir = {file_id:[list of PG ids]}
		"dir2":{}
	},
	"processing":{}
}

client4 = {
	"username":"client4",
	"client_id":"C4",
	"dir_tree":{
		"root":{},
		"dir1":{}, # dir = {file_id:[list of PG ids]}
		"dir2":{}
	},
	"processing":{}
}

user_list = {
	"client1":"passwd1",
	"client2":"passwd2",
	"client3":"passwd3",
	"client4":"passwd4",
}

file = open("./tree/"+client1["username"], 'wb')

obj_b = pickle.dumps(client1)
file.write(obj_b)

file.close()

file = open("./tree/"+client2["username"], 'wb')

obj_b = pickle.dumps(client2)
file.write(obj_b)

file.close()

file = open("./tree/"+client3["username"], 'wb')

obj_b = pickle.dumps(client3)
file.write(obj_b)

file.close()

file = open("./tree/"+client4["username"], 'wb')

obj_b = pickle.dumps(client4)
file.write(obj_b)

file.close()

file = open("./user_list", 'wb')

obj_b = pickle.dumps(user_list)
file.write(obj_b)

file.close()

logged_in = []

file = open("./logged_in", 'wb')

obj_b = pickle.dumps(logged_in)
file.write(obj_b)

file.close()