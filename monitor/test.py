import pickle

hashtable_file = open('hashtable', 'r+b')
hashtable_dump = hashtable_file.read()
hashtable = pickle.loads(hashtable_dump)

MDS_flags_file = open('MDS_flags', 'rb')
MDS_flags_dump = MDS_flags_file.read()
MDS_flags = pickle.loads(MDS_flags_dump)

cluster_topology_file = open('cluster_topology', 'r+b')
cluster_topology_dump = cluster_topology_file.read()
cluster_topology = pickle.loads(cluster_topology_dump)

cluster_topology[4]["status"] = 1

hashtable_dump = pickle.dumps(hashtable)
hashtable_file.write(hashtable_dump)

cluster_topology_dump = pickle.dumps(cluster_topology)
cluster_topology_file.write(cluster_topology_dump)

print(hashtable)
print(cluster_topology)

hashtable_file.close()
MDS_flags_file.close()
cluster_topology_file.close()