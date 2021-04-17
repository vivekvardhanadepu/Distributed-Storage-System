import pickle

def main():
    friends = {}
    friends_dump = pickle.dumps(friends)
    friends_file = open('hashtable', 'wb')
    friends_file.write(friends_dump)
    friends_file.close()

if __name__ == '__main__':
	main()