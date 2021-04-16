import pickle

def main():
    ## hashtable and cluster topology structure

    # write_status : 0(NOT WRITTEN), 1(WRITTEN)
    hashtable = {
                # "pg_id1":[("osd_id1", write_status), ("osd_id2", write_status), ("osd_id3", write_status)],
                # "pg_id2":[("osd_id4", write_status), ("osd_id5", write_status), ("osd_id6", write_status)]
                 }
    hashtable_dump = pickle.dumps(hashtable)
    hashtable_file = open('hashtable', 'wb')
    hashtable_file.write(hashtable_dump)
    hashtable_file.close()

    # status = 0(ALIVE), 1(DOWN), 2(OUT)
    cluster_topology = {
                        "osd_id1":
                        {
                            "ip":'blah',
                            "port":1020,
                            "free_space":100,
                            "status":0,
                            "friends_update":False,            
                            "friends":{}
                        },

                        "osd_id2":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "status":0,
                            "friends_update":False,
                            "friends":{}
                        },

                        "osd_id3":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "status":0,
                            "friends_update":False,
                            "friends":{}
                        },

                        "osd_id4":
                        {
                            "ip":'blah',
                            "port":1211,
                            "free_space":100,
                            "status":0,
                            "friends_update":False,
                            "friends":{}
                        }

                        # "osd_id5":
                        # {
                        #     "ip":'blah',
                        #     "port":1211,
                        #     "free_space":100,
                        #     "status":0,
                        #     "friends_update":False,
                        #     "friends":{}
                        # },

                        # "osd_id6":
                        # {
                        #     "ip":'blah',
                        #     "port":1211,
                        #     "free_space":100,
                        #     "status":0,
                        #     "friends_update":False,
                        #     "friends":{}
                        # },  
                    }
    cluster_topology_dump = pickle.dumps(cluster_topology)
    cluster_topology_file = open('cluster_topology', 'wb')
    cluster_topology_file.write(cluster_topology_dump)
    cluster_topology_file.close()

if __name__ == '__main__':
	main()