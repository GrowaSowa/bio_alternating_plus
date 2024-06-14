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
		self.used_verifiers = []

	def clear(self):
		self.odd_path.clear()
		self.even_path.clear()
		self.used_verifiers.clear()

class PreciseAlgorithm(SequencingProblem):
	def __init__(self, xmlroot, time_limit):
		super().__init__(xmlroot)
		self.max_time = time_limit # seconds
		self.max_steps = self.length - self.probe_len*2 + 2
		self.graph = {}
		self.state = AlgorithmState()
		self.state_snapshots = []
		self.failed_state_rollback = False
		self.found_sequences = []

	def buildGraph(self):
		self.graph.clear()
		for i, pattern in enumerate(self.data[0].spectrum):
			out_verts = binary_search(pattern[2:], self.data[0].spectrum, 2)
			# delete arcs that start and end in the same vertex
			if i in out_verts:
				out_verts.remove(i)
			self.graph[i] = out_verts
	
	def rebuildDNA(self):
		result = []
		for i in range(len(self.data[0].spectrum[self.state.odd_path[0]])+1):
			if i%2 == 0:
				result.append(self.data[0].spectrum[self.state.odd_path[0]][i])
			else:
				result.append(self.data[0].spectrum[self.state.even_path[0]][i-1])
		i = j = 1
		while i<len(self.state.odd_path) or j<len(self.state.even_path):
			if i<len(self.state.odd_path):
				result.append(self.data[0].spectrum[self.state.odd_path[i]][-1])
				i += 1
			if j<len(self.state.even_path):
				result.append(self.data[0].spectrum[self.state.even_path[j]][-1])
				j += 1
		self.found_sequences.append(''.join(result))
	
	def snapshotState(self):
		self.state_snapshots.append(copy.deepcopy(self.state))

	def restoreLastState(self):
		if self.state_snapshots:
			self.state = self.state_snapshots.pop()
		else:
			self.failed_state_rollback = True

	def getSteps(self):
		return len(self.state.odd_path) + len(self.state.even_path)

	def searchSpaceEmpty(self):
		# check whether we ran out of paths to follow through the graph
		return self.failed_state_rollback #or (self.getSteps() == self.max_steps and not self.state_snapshots)

	def findOutgoingVertices(self, prev_vertex_in_path):
		candidates = []
		for el in self.graph[prev_vertex_in_path]:
			# remove vertices that were already used
			if el not in self.state.odd_path and el not in self.state.even_path:
				candidates.append(el)
		return candidates
	
	def verifyCandidates(self, candidates, curr_vertex):
		verdicts = []
		for candidate in candidates:
			# merge current vertex and candidate to get pattern to verify against
			pattern = list(self.data[0].spectrum[curr_vertex][2:])
			pattern.append(self.data[0].spectrum[candidate][-1])
			# should return a 1-element list, as pattern should exactly match
			# one element from the verifier spectrum, if it exists
			verifier_id = binary_search_v(pattern, self.data[1].spectrum)
			# if no verifier found, or verifier matched, but already used
			if verifier_id[0] != -1 and verifier_id[0] not in self.state.used_verifiers:
				verdicts.append((candidate, verifier_id[0]))
		return verdicts

	def run(self):
		self.state.clear()
		self.state_snapshots.clear()

		start_time = time.time()
		self.buildGraph()
		# find odd path's first vertex
		f_v = binary_search_v(self.start, self.data[0].spectrum)
		self.state.odd_path.append(f_v[0])

		#find even path's first vertex
		f_v = binary_search(self.start[1:], self.data[0].spectrum, 1)
		# verify
		for el in f_v:
			p = list(self.start[2:])
			p.append(self.data[0].spectrum[el][-1])
			f_v_ver = binary_search_v(p, self.data[1].spectrum)
			if f_v_ver[0] != -1:
				self.state.even_path.append(el)
				self.state.used_verifiers.append(f_v_ver[0])
				self.snapshotState()
				self.state.even_path.pop(-1)
				self.state.used_verifiers.pop(-1)
		self.restoreLastState()

		while getCurrExecTime(start_time) < self.max_time and not self.searchSpaceEmpty():
			if self.getSteps() == self.max_steps:
				# if found a full sequence, output it
				self.rebuildDNA()
				# and look through the rest of the search space
				self.restoreLastState()

			if len(self.state.odd_path) > len(self.state.even_path):
				# find next vertex in even path
				candidates = self.findOutgoingVertices(self.state.even_path[-1])
				verdicts = self.verifyCandidates(candidates, self.state.odd_path[-1])
				# if no candidates left
				if not verdicts:
					self.restoreLastState()
					continue
				# state shenanigans lmao
				for candidate, verifier in verdicts:
					# make state snapshots for all possibilities
					self.state.even_path.append(candidate)
					self.state.used_verifiers.append(verifier)
					self.snapshotState()
					self.state.even_path.pop(-1)
					self.state.used_verifiers.pop(-1)
				# then grab the last one
				self.restoreLastState()

			else:
				# find next vertex in odd path
				candidates = self.findOutgoingVertices(self.state.odd_path[-1])
				verdicts = self.verifyCandidates(candidates, self.state.even_path[-1])
				# if no candidates left
				if not verdicts:
					self.restoreLastState()
					continue
				# state shenanigans lmao
				for candidate, verifier in verdicts:
					# make state snapshots for all possibilities
					self.state.odd_path.append(candidate)
					self.state.used_verifiers.append(verifier)
					self.snapshotState()
					self.state.odd_path.pop(-1)
					self.state.used_verifiers.pop(-1)
				# then grab the last one
				self.restoreLastState()

xmlroot = getXML()
#xmlroot = loadXML('f.xml')
#saveXML(xmlroot, 'f.xml')
obj = PreciseAlgorithm(xmlroot, 300)
obj.run()

for sequence in obj.found_sequences:
	print(sequence)