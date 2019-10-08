#!/usr/bin/python

import sys
import re # For regex

import ryu_ofctl
from ryu_ofctl import *

def main(macHostA, macHostB):
    print "Installing flows for %s <==> %s" % (macHostA, macHostB)

    ##### FEEL FREE TO MODIFY ANYTHING HERE #####
    try:
        pathA2B = dijkstras(macHostA, macHostB)
        installPathFlows(macHostA, macHostB, pathA2B)
    except:
        raise


    return 0

# Installs end-to-end bi-directional flows in all switches
def installPathFlows(macHostA, macHostB, pathA2B):
    ##### YOUR CODE HERE #####
	#flow=ryu_ofctl.FlowEntry()
	for x in range (0,len(pathA2B)):
		flow=ryu_ofctl.FlowEntry()
		act = ryu_ofctl.OutputAction(pathA2B[x]['out_port'])
		flow.in_port =pathA2B[x]['in_port']
		flow.addAction(act)
		dpid=pathA2B[x]['dpid']
		#print dpid
		#print pathA2B[x]['in_port']
		#print pathA2B[x]['out_port'] 
		ryu_ofctl.insertFlow(dpid,flow)	

	for x in reversed(range (0,len(pathA2B))):
		flow=ryu_ofctl.FlowEntry()
		act = ryu_ofctl.OutputAction(pathA2B[x]['in_port'])
		flow.in_port =pathA2B[x]['out_port']
		flow.addAction(act)
		dpid=pathA2B[x]['dpid']
		ryu_ofctl.insertFlow(dpid,flow)	

	print "installed"

	return

# Returns List of neighbouring DPIDs
def findNeighbours(dpid):
	if type(dpid) not in (int, long) or dpid < 0:
		raise TypeError("DPID should be a positive integer value")

	#print "find"

	neighbours = []

    ##### YOUR CODE HERE #####

	allLinks = ryu_ofctl.listSwitchLinks(dpid)
	#print allLinks
	if len(allLinks) != 0:
		linkvalA = allLinks.values()
		linkendA = linkvalA.pop()
	
		for x in range(0, len(linkendA)):
			linkendB = linkendA.pop()
			linkvalB = linkendB.values()
			linkendC = linkvalB.pop()
			linkvalC = linkendC.values()
			if linkvalC[1] != dpid:
				neighbours.append(linkvalC[1])
	return neighbours

# Calculates least distance path between A and B
# Returns detailed path (switch ID, input port, output port)
#   - Suggested data format is a List of Dictionaries
#       e.g.    [   {'dpid': 3, 'in_port': 1, 'out_port': 3},
#                   {'dpid': 2, 'in_port': 1, 'out_port': 2},
#                   {'dpid': 4, 'in_port': 3, 'out_port': 1},
#               ]
# Raises exception if either ingress or egress ports for the MACs can't be found
def dijkstras(macHostA, macHostB):

    # Optional helper function if you use suggested return format
	def nodeDict(dpid, in_port, out_port):
		assert type(dpid) in (int, long)
		assert type(in_port) is int
		assert type(out_port) is int
		return {'dpid': dpid, 'in_port': in_port, 'out_port': out_port}

    # Optional variables and data structures
	INFINITY = float('inf')
	distanceFromA = {} # Key = node, value = distance
	leastDistNeighbour = {} # Key = node, value = neighbour node with least distance from A
	pathAtoB = [] # Holds path information

    ##### YOUR CODE HERE #####

    # Some debugging output
    #print "leastDistNeighbour = %s" % leastDistNeighbour
    #print "distanceFromA = %s" % distanceFromA
    #print "pathAtoB = %s" % pathAtoB

	allSwitches = ryu_ofctl.listSwitches()
	switches = allSwitches.values() 
	dist = []
	prev = []
	visited = []
	unvisited = [1,2,3,4,5,6]
	
	for i in range(0,6):
		dist.append(INFINITY)
		prev.append(0)
		visited.append(0)

	start = ryu_ofctl.getMacIngressPort(macHostA)
	startnum = start['dpid']
	end = ryu_ofctl.getMacIngressPort(macHostB)
	endnum = end['dpid']
	dist[startnum-1] = 0
	
	while len(unvisited) != 0:
		u = 0
		#print dist
		for i in range(0,len(unvisited)):
			#print unvisited[i]
			if u == 0:
				u = unvisited[i]
			if dist[unvisited[i]-1] < dist[u-1]:
				u = unvisited[i]
		unvisited.remove(u)
		#print u	

		neighbours = findNeighbours(u)
		#print neighbours
		for v in range(0,len(neighbours)):
			weight = dist[u-1] + 1
			#print weight
			#print neighbours[v]
			if weight < dist[neighbours[v]-1]:
				dist[neighbours[v]-1] = weight
				prev[neighbours[v]-1] = u
				
	#print dist
	#print prev
	#print unvisited

	next = endnum
	tempPath = []
	tempPath.append(endnum)
	while prev[next-1] != 0:
		tempPath.append(prev[next-1])
		next = prev[next-1]
	tempPath.reverse()

	print tempPath

	if len(tempPath) == 3:
		node1 = {}
		node1['in_port'] = start['port']
		links = ryu_ofctl.listSwitchLinks(tempPath[0])
		linklen = links.values().pop()
		for x in range(0, len(linklen)):
			if linklen[x]['endpoint1']['dpid'] == tempPath[0] and linklen[x]['endpoint2']['dpid'] == tempPath[1]:
				node1['out_port'] = linklen[x]['endpoint1']['port']
				
		node1['dpid'] = tempPath[0]
		pathAtoB.append(node1)
	
		node2 = {}
		links = ryu_ofctl.listSwitchLinks(tempPath[1])
		linklen = links.values().pop()
		for x in range(0, len(linklen)):
			if linklen[x]['endpoint1']['dpid'] == tempPath[0] and linklen[x]['endpoint2']['dpid'] == tempPath[1]:
				node2['in_port'] = linklen[x]['endpoint1']['port']
		links = ryu_ofctl.listSwitchLinks(tempPath[1])
		linklen = links.values().pop()
		for x in range(0, len(linklen)):
			if linklen[x]['endpoint1']['dpid'] == tempPath[1] and linklen[x]['endpoint2']['dpid'] == tempPath[2]:
				node2['out_port'] = linklen[x]['endpoint1']['port']
		node2['dpid'] = tempPath[1]
		pathAtoB.append(node2)

		node3 = {}
		node3['out_port'] = end['port']
		links = ryu_ofctl.listSwitchLinks(tempPath[2])
		linklen = links.values().pop()
		for x in range(0, len(linklen)):
			if linklen[x]['endpoint1']['dpid'] == tempPath[1] and linklen[x]['endpoint2']['dpid'] == tempPath[2]:
				node3['in_port'] = linklen[x]['endpoint1']['port']
		node3['dpid'] = tempPath[2]
		pathAtoB.append(node3)

	if len(tempPath) == 2:
		node1 = {}
		node1['in_port'] = start['port']
		links = ryu_ofctl.listSwitchLinks(tempPath[0])
		linklen = links.values().pop()
		for x in range(0, len(linklen)):
			if linklen[x]['endpoint1']['dpid'] == tempPath[0] and linklen[x]['endpoint2']['dpid'] == tempPath[1]:
				node1['out_port'] = linklen[x]['endpoint1']['port']
				
		node1['dpid'] = tempPath[0]
		pathAtoB.append(node1)
	
		node2 = {}
		node2['out_port'] = end['port']
		links = ryu_ofctl.listSwitchLinks(tempPath[1])
		linklen = links.values().pop()
		for x in range(0, len(linklen)):
			if linklen[x]['endpoint1']['dpid'] == tempPath[0] and linklen[x]['endpoint2']['dpid'] == tempPath[1]:
				node2['in_port'] = linklen[x]['endpoint1']['port']
		node2['dpid'] = tempPath[1]
		pathAtoB.append(node2)

	if len(tempPath) == 1:
		node = {}
		node['in_port'] = start['port']
		node['out_port'] = end['port']
		node['dpid'] = tempPath[0]
		pathAtoB.append(node)
		
	print pathAtoB

	return pathAtoB


# Validates the MAC address format and returns a lowercase version of it
def validateMAC(mac):
    invalidMAC = re.findall('[^0-9a-f:]', mac.lower()) or len(mac) != 17
    if invalidMAC:
        raise ValueError("MAC address %s has an invalid format" % mac)

    return mac.lower()

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print "This script installs bi-directional flows between two hosts"
        print "Expected usage: install_path.py <hostA's MAC> <hostB's MAC>"
    else:
        macHostA = validateMAC(sys.argv[1])
        macHostB = validateMAC(sys.argv[2])

        sys.exit( main(macHostA, macHostB) )
