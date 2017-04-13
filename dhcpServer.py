#!/usr/bin/python
import math
import socket
import operator
from thread import *

class dhcpServer:
	''' functionalities of dhcp Server '''
	def __init__(self):
		''' initialize the port and open a new socket for connection '''
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.port = 6001
		self.hostname = socket.gethostname()
		self.socket.bind((self.hostname, self.port))
		self.socket.listen(1000)
		self.leaseTime = 165
		self.labs = {}
		self.macs = {}
		# information to be sent back
		self.Ips = {}
		self.Subnet = {}
		self.netAddress = {}
		self.broadAddress = {}
		self.DNSGateway  = {}
		self.setData()
		self.allocateIpsToLabs()
	
	def setData(self):
		''' read the subnet.conf file and configure appropriate mac's 
			& corresponding labs list for Ip Allocations'''

		with open('subnets.conf','r') as subnet_file:
		
			line_number = 1

			for line in subnet_file:
				if line_number == 1:
					IpDetails = line.split('/')
					self.startIp = IpDetails[0]
					self.numberOfIps = 2**(32 - int(IpDetails[1]))			
				elif line_number == 2:
					self.numberOfLabs = int(line)
				elif line_number >= 3 and line_number <= 3 + self.numberOfLabs - 1:
					labDetails = line.split(':')
					self.labs[labDetails[0]] = int(labDetails[1])
				else:
					macDetails = line.split()
					self.macs[macDetails[0]] = macDetails[1]
				line_number += 1

	def allocateIpsToLabs(self):
		''' check for allocation possibility of total available Ips & 
			the hosts present in each subnet '''
		hosts = 0
		currentIp = self.startIp
		labs = sorted(self.labs.items(), key=operator.itemgetter(0))

		for lab in labs:
			self.Ips[lab[0]] = []
			# Subnet mask
			maxHosts = int(math.ceil(math.log(lab[1], 2)))
			bits = 32 - maxHosts
			self.Subnet[lab[0]] = bits
			# check if hosts exceed Ips available
			hosts += self.labs[lab[0]]
			if hosts > self.numberOfIps:
				# dont allocate IP for this subnet go for allocation in next lab
				self.Ips[lab[0]].append([str("Cannot Allocate Ips for " + str(lab[0])), 0])
				self.Subnet[lab[0]] = str("Cannot Allocate Subnet for " + str(lab[0]))
 				self.netAddress[lab[0]] = str("Cannot Allocate Network Address for " + str(lab[0]))
 				self.broadAddress[lab[0]] = str("Cannot Allocate Broadcast Address for " + str(lab[0]))
 				self.DNSGateway[lab[0]] = str("Cannot Allocate DNS & GateWay Address for " + str(lab[0]))
				hosts -= self.labs[lab[0]]
				continue

			for i in range(0, 2**maxHosts):
				if i == 1:
					# Network Address
					self.Ips[lab[0]].append([currentIp, 1])
				else:
					# Host Address
					self.Ips[lab[0]].append([currentIp, 0])
					currentIpParts = currentIp.split('.')
					currentIpParts = [int(i) for i in currentIpParts]
					for j in range(3, -1, -1):
						currentIpParts[j] += 1
						if currentIpParts[j] <= 255:
							break
						else:
							currentIpParts[j] = 0
					currentIp = '.'.join(str(part) for part in currentIpParts)

			# Network Address
			networkAddress = self.Ips[lab[0]]
			self.netAddress[lab[0]] = networkAddress[0][0]
		
			# Broadcast Address
			BroadCast = self.Ips[lab[0]]
			self.broadAddress[lab[0]] = BroadCast[len(BroadCast)-1][0]
		
			# Same DNS, Gateway Address
			DNSGateWay = self.Ips[lab[0]]
			self.DNSGateway[lab[0]] = DNSGateWay[int(len(DNSGateWay)/2)][0]

		self.Ips["unallocated"] = []
		
		if hosts < self.numberOfIps:
			# allocated remaining Ips for an unregistered subnet
			remainingHosts = self.numberOfIps - hosts
			maxHosts = int(math.ceil(math.log(remainingHosts, 2)))
			for i in range(0, 2**maxHosts):
				if i == 1:
					# Network Address
					self.Ips["unallocated"].append([currentIp, 1])
				else:
					# Host Address
					self.Ips["unallocated"].append([currentIp, 0])
					currentIpParts = currentIp.split('.')
					currentIpParts = [int(i) for i in currentIpParts]
					for j in range(3, -1, -1):
						currentIpParts[j] += 1
						if currentIpParts[j] <= 255:
							break
						else:
							currentIpParts[j] = 0
					currentIp = '.'.join(str(part) for part in currentIpParts)

			# Network Address
			networkAddress = self.Ips["unallocated"]
			self.netAddress["unallocated"] = networkAddress[0][0]
		
			# Broadcast Address
			BroadCast = self.Ips["unallocated"]
			self.broadAddress["unallocated"] = BroadCast[len(BroadCast)-1][0]
		
			# Same DNS, Gateway Address
			DNSGateWay = self.Ips["unallocated"]
			self.DNSGateway["unallocated"] = DNSGateWay[int(len(DNSGateWay)/2)][0]

		else:
			self.Ips["unallocated"].append([str("Cannot Allocate Ips for unallocated user"), 0])
 			self.Subnet["unallocated"] = str("Cannot Allocate Subnet for unallocated user")
 			self.netAddress["unallocated"] = str("Cannot Allocate Network Address for unallocated user")
 			self.broadAddress["unallocated"] = str("Cannot Allocate Broadcast Address for unallocated user")
 			self.DNSGateway["unallocated"] = str("Cannot Allocate DNS & GateWay Address for unallocated user")
	
	def dhcpDiscover(self, conn):
		''' receive the request from client for connection '''
		mac_address = conn.recv(50)
		# allot lab based on the MAC Address if not allocate a new subnet
		try:
			lab = self.macs[mac_address]
		except KeyError:
			lab = "unallocated"

		if lab == "unallocated":
			ipToAssign = self.Ips[lab][0][0]
		else:
			i = 0
			while i < len(self.Ips[lab]) and self.Ips[lab][i][1] == 1:
				i += 1
			print "fdyhrtgh", i
			if i >= len(self.Ips[lab]):
				fullStatus = 1
				print "subnet is full"
				conn.send(str(fullStatus))
				return self.dhcpDiscover(conn)
			else:
				fullStatus = 0
				conn.send(str(fullStatus))
			

			ipToAssign = self.Ips[lab][i][0]
			self.Ips[lab][i][1] = 1
			subnet = self.Subnet[lab]
			ipToAssign = '/'.join([str(ipToAssign), str(subnet)])
		# offer assigned Ip to the requested client
		self.dhcpOffer(ipToAssign, lab, conn)

	def dhcpOffer(self, ip, lab, conn):
		''' send the ipAddress assigned to the client '''
		# Send Ip Address
		Ack = 0
		while not Ack:
			conn.send(ip)
			Ack = int(conn.recv(1))
		# Send Network Address
		Ack = 0
		while not Ack:
			conn.send(str(self.netAddress[lab]))
			Ack = int(conn.recv(1))
		# Send broadAddress
		Ack = 0
		while not Ack:	
			conn.send(str(self.broadAddress[lab]))
			Ack = int(conn.recv(1))
		# Send DNS & Gateway Address
		Ack = 0
		while not Ack:
			conn.send(str(self.DNSGateway[lab]))
			Ack = int(conn.recv(10))

		self.dhcpRequest(ip, lab, conn)

	def dhcpRequest(self, ip, lab, conn):
		''' receive the IP addresses sent by dhcpOffer() from 
			client to verify proper addresses is received '''
		assignedIp = conn.recv(100)
		if assignedIp == ip:
			self.dhcpAck(1, lab, ip, conn)

		else:
			self.dhcpAck(0, lab, ip, conn)

	def dhcpAck(self, ack, lab, ip, conn):
		''' send an acknowledgement to client if an dhcpRequest() 
			verification is passed otherwise send an not an acknowledgement '''
		if ack:
			conn.send('ACK')
			if "Cannot" in str(ip):
				print "cannot allocate Ip to this client"
			else:
				ip = ip.split('/')
				for i in range(0, len(self.Ips[lab])):
					if self.Ips[lab][i][0] == ip[0]:
						break
				
				print "serving " + str(lab) + " " + str(self.Ips[lab][i][0]) + " !"
				conn.send(str(self.leaseTime))
				print self.Ips[lab][i]
				timeout = int(conn.recv(10))
				if timeout:
					print "sdfdss"
					self.Ips[lab][i][1] = 0
					print str(lab) + " " + str(self.Ips[lab][i][0]) + " connection closed !"
		else:
			conn.send('NACK')
			self.Ips[lab][i][1] = 0
			self.dhcpDiscover(conn)


if __name__ == "__main__":
	
	server = dhcpServer()

	while True:
		conn, addr = server.socket.accept()
		start_new_thread(server.dhcpDiscover,(conn,))	