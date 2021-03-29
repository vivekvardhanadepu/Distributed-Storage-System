import socket

soc = socket.socket()
print("Socket Created")

#We will bing the server to this port to listen
soc.bind(('localhost', 2001))
'''
    Use a port number larger than 1024 (recommended)
    Or run the script as a privileged user
'''

#It will listen to atmost 3 connected connections (outstanding connections) at a time
soc.listen(3)
print("Waiting for the connections:")

while True:
	conn, addr  = soc.accept()
	name = conn.recv(1024).decode()

	print(f"Connected with {addr}, {name}")

	conn.send(bytes("Welcome to Monitor-1","utf-8"))

	for i in range(10):
		conn.send(bytes(f"Hello - {i}","utf-8"))

	conn.close()

soc.close()


