#!/usr/bin/python
import sys
import time
import socket
from uuid import getnode as get_mac


class dhcpClient:
	''' client requests methods for a connection to dhcp Server '''
	def __init__(self, mac):
		''' initilize the port and open a socket for other end of
			communication requesting a connection dhcp Server '''
		self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.clientPort = 6001
	 	self.hostname = socket.gethostname()
		self.clientSocket.connect((self.hostname, self.clientPort))
		self.mac = mac
	
	def clientDiscover(self):
		''' send the request for dhcp server for a connection '''
		self.clientSocket.send(self.mac)
		
		fullStatus = int(self.clientSocket.recv(1))

		if fullStatus:
			print "Subnet is full"
			return self.clientDiscover()

		self.clientOffer()

	def clientOffer(self):
		''' take the IP address sent by the dhcp Server '''

		# recieve Ip Address	
		assignedIp = ''	
		while not assignedIp:
			assignedIp = self.clientSocket.recv(100)
			self.clientSocket.send(str(1))
		self.ip =  assignedIp
		# recieve Network Address
		assignedNetworkAddress = ''
		while not assignedNetworkAddress:
			assignedNetworkAddress = self.clientSocket.recv(100)
			self.clientSocket.send(str(1))
		self.networkAddress = assignedNetworkAddress
		# recieve BroadCast Address
		assignedBroadCastAddress = ''
		while not assignedBroadCastAddress:
			assignedBroadCastAddress = self.clientSocket.recv(100)
			self.clientSocket.send(str(1))
		self.broadcastAddress = assignedBroadCastAddress
		# recieve DNS & Gateway Address
		assignedDNSGateway = ''
		while not assignedDNSGateway:
			assignedDNSGateway = self.clientSocket.recv(100)
			self.clientSocket.send(str(1))
		self.DNS = assignedDNSGateway
		self.gateWay = assignedDNSGateway
		self.clientRequest(assignedIp)

	def clientRequest(self, ip):
		''' send back the IP address sent by dhcp Server
			for verification of proper communication channel '''
		self.clientSocket.send(ip)
		self.clientAck(ip)

	def clientAck(self, ip):
		''' receive the acknowledgment sent by dhcp Server '''
		ack = self.clientSocket.recv(4)
		if ack == "ACK":
			print self.ip
			print self.networkAddress
			print self.broadcastAddress
			print self.DNS
			print self.gateWay
			if "Cannot" in str(self.ip): 
				print "cannot connect to this Network"
			else:
				leaseTime = int(self.clientSocket.recv(10))
				time.sleep(leaseTime)
				self.clientSocket.send(str(1))
		else:
			self.clientDiscover()


if __name__ == "__main__":
	
	
	if len(sys.argv) == 3:
		if sys.argv[0] == "./dhcpClient.py" and sys.argv[1] == "-m":
			client = dhcpClient(sys.argv[2])
			client.clientDiscover()
		else:
			print "Give proper number of argument ( eg: ./client.py -m MAC-ADDRESS )"
	else:
		mac = get_mac()
		mac = ':'.join(("%012X" % mac)[i:i+2] for i in range(0, 12, 2))
		client = dhcpClient(mac)
		client.clientDiscover()