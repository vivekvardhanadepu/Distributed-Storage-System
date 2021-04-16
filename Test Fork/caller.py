import socket
import time
import os

soc = socket.socket()
print("Socket Created")

#We will bing the server to this port to listen
soc.bind(('', 2000))
'''
    Use a port number larger than 1024 (recommended)
    Or run the script as a privileged user
'''

#It will listen to atmost 3 connected connections (outstanding connections) at a time
soc.listen(3)
print("Waiting for the connections:")



while True:
	conn, addr  = soc.accept()

	n = os.fork()

	if n == 0:
		print(f"Inside the child handler for the current request pid {os.getpid()}") 

		name = conn.recv(1024).decode()

		print(f"Connected with {addr}, {name}")

		time.sleep(20)

		conn.send(bytes("Welcome to Monitor-1","utf-8"))

		conn.close()

		print(f"Exiting from pid {os.getpid()} ..")
		os._exit(1)


soc.close()


