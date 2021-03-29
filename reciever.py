import socket

soc = socket.socket()

#Give in the IP address and port
soc.connect(('localhost', 2001))

name = "Storage-1"

#Convert the packet into bytes and send it over the socket
soc.send(bytes(name, 'utf-8'))

#We will listen t0 1024 Byte packet each time
while True:
	reply = soc.recv(1024)

	if not reply:
		break
	else:
		print(reply.decode())

soc.close()