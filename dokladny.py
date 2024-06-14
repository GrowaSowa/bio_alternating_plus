from include.seq_obj import SequencingProblem
from include.xml_parser import getXML, saveXML, loadXML
import xml.etree.ElementTree as ET
import time
import copy

def compare(string1, string2):
    # assumes strings are of equal length (or at least that s1 is not shorter than s2)
    for i in range(len(string1)):
        if string1[i] == string2[i] or string1[i] == 'X' or string2[i] == 'X':
            continue
        if string1[i] < string2[i]:
            return -1
        if string1[i] > string2[i]:
            return 1
    return 0
        
def binary_search(pattern, items, rtrim):
    l_i = 0
    r_i = len(items)-1
    while True:
        i = (l_i + r_i)//2
        val = compare(pattern, items[i][:-rtrim])
        if val == 0:
            j = i+1
            while i>0 and compare(pattern, items[i-1][:-rtrim])==0:
                i -= 1
            while j<len(items) and compare(pattern, items[j][:-rtrim])==0:
                j += 1
            return list(range(i, j))
        elif l_i == r_i: # no match found
            return [-1]
        elif val < 0:
            r_i = i-1
            if r_i < l_i:
                r_i = l_i
        elif val > 0:
            l_i = i+1
            if l_i > r_i:
                l_i = r_i

# a binary search that doesn't splice the items in list 
def binary_search_v(pattern, items):
    l_i = 0
    r_i = len(items)-1
    while True:
        i = (l_i + r_i)//2
        val = compare(pattern, items[i])
        if val == 0:
            j = i+1
            while i>0 and compare(pattern, items[i-1])==0:
                i -= 1
            while j<len(items) and compare(pattern, items[j])==0:
                j += 1
            return list(range(i, j))
        elif l_i == r_i: # no match found
            return [-1]
        elif val < 0:
            r_i = i-1
            if r_i < l_i:
                r_i = l_i
        elif val > 0:
            l_i = i+1
            if l_i > r_i:
                l_i = r_i

def getCurrExecTime(s_time):
	now = time.time()
	return now - s_time

class AlgorithmState():
	def __init__(self):
		self.odd_path = []
		self.even_path = []
		#self.visited_vertices = []
		self.used_verifiers = []

	def clear():
		self.odd_path.clear()
		self.even_path.clear()
		self.used_verifiers.clear()

class PreciseAlgorithm(SequencingProblem):
	def __init__(self, xmlroot, time_limit):
		super().__init__(xmlroot)
		self.max_time = time_limit # seconds
		self.max_steps = self.length - self.probe_len*2 + 1
		self.graph = {}
		self.state = AlgorithmState()
		self.state_snapshots = []
		self.found_sequences = []

	def buildGraph(self):
		self.graph.clear()
		for i, pattern in enumerate(self.data[0].spectrum):
			out_verts = binary_search(pattern[2:], self.data[0].spectrum, 2)
			# delete arcs that start and end in the same vertex
			if i in out_verts:
				out_verts.remove(i)
			self.graph[i] = out_verts
	
	def rebuildDNA(self, path_odd, path_even):
		result = []
		for i in range(len(path_odd[0])+1):
			if i%2 == 0:
				result.append(path_odd[0][i])
			else:
				result.append(path_even[0][i-1])
		i = j = 1
		while i<len(path_odd) and j<len(path_even):
			if i<len(path_odd):
				result.append(path_odd[i][-1])
				i += 1
			if j<len(path_even):
				result.append(path_even[j][-1])
				j += 1
		self.found_sequences.append(''.join(result))
	
	def snapshotState(self):
		self.state_snapshots.append(copy.deepcopy(self.state))

	def restoreLastState(self):
		self.state = self.state_snapshots.pop()

	def searchSpaceEmpty(self):
		steps = len(self.state.odd_path) + len(self.state.even_path) + self.probe_len*2 - 1
		# check whether we ran out of paths to follow through the graph
		return  steps == self.max_steps and not self.found_sequences

	def run(self):
		self.state.clear()
		self.state_snapshots.clear()
		
		start_time = time.time()
		buildGraph()
		# find odd path's first vertex
		f_v = binary_search_v(self.start, self.data[0].spectrum)
		self.state.odd_path.append(f_v[0])
		#self.state.visited_vertices.append(f_v[0])

		#find even path's first vertex
		f_v = binary_search(self.start[1:], self.data[0].spectrum, 1)
		self.state.even_path.append(f_v[0])
		#self.state.visited_vertices.append(f_v[0])
		for i in range(1, len(f_v)): # if multiple candidates found
			snapshotState()
			self.state.even_path[0] = f_v[i]

		while getCurrExecTime(start_time) < self.max_time and not self.searchSpaceEmpty():
			if len(self.state.odd_path) > len(self.state.even_path):
				#TODO: find next vertex in even graph
				pass
			else:
				#TODO: find next vertex in odd graph
				pass

xmlroot = getXML()
#saveXML(xmlroot, 'f.xml')
obj = PreciseAlgorithm(xmlroot, 300)
obj.run()

for sequence in obj.found_sequences:
	print(sequence)