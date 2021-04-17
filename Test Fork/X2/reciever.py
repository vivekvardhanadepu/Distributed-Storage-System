import socket
import time

soc = socket.socket()
name = "Storage-X2"

#Give in the IP address and port
soc.settimeout(5)
try :
	soc.connect(('localhost', 2000))
	soc.settimeout(None)

	#Convert the packet into bytes and send it over the socket
	soc.send(bytes(name, 'utf-8'))

	#time.sleep(10)

	#We will listen t0 1024 Byte packet each time
	while True:
		reply = soc.recv(1024)

		if not reply:
			soc.close()
			break
		else:
			print(reply.decode())

except :
	print("FUCKED") 
