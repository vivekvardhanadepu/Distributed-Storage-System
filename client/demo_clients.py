import pickle
client1 = {
	"username":"client1",
	"client_id":"C1",
	"last_file_id":0,
	"root":{
		"dir1":{0:["text1.txt",["p1"]], 1:["vv.cpp", ["p2"]]}, # dir = {file_id:[file_name, [list of PG ids]]}
		"dir2":{}
	}
}

client2 = {
	"username":"client2",
	"client_id":"C2",
	"last_file_id":0,
	"root":{
		"dir1":{}, # dir = {file_id:[list of PG ids]}
		"dir2":{}
	}
}

client3 = {
	"username":"client3",
	"client_id":"C3",
	"last_file_id":0,
	"root":{
		"dir1":{}, # dir = {file_id:[list of PG ids]}
		"dir2":{}
	}
}

client4 = {
	"username":"client4",
	"client_id":"C4",
	"last_file_id":0,
	"root":{
		"dir1":{}, # dir = {file_id:[list of PG ids]}
		"dir2":{}
	}
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