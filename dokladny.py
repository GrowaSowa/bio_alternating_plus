from include.seq_obj import SequencingProblem
from include.xml_parser import getXML, saveXML, loadXML
import xml.etree.ElementTree as ET
import time

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

def buildGraph(spectrum):
	graph = {}
	for i, pattern in enumerate(spectrum):
		out_verts = binary_search(pattern[2:], spectrum, 2)
		# delete arcs that start and end in the same vertex
		if i in out_verts:
			out_verts.remove(i)
		graph[i] = out_verts
	return graph

def rebuildDNA(path_odd, path_even):
	result = []
	for i in range(len(path_odd[0])+1):
		if i%2 == 0:
			result.append(path_odd[0][i])
		else:
			result.append(path_even[0][i-1])
	i=1
	j=1
	while i<len(path_odd) and j<len(path_even):
		if i<len(path_odd):
			result.append(path_odd[i][-1])
			i += 1
		if j<len(path_even):
			result.append(path_even[j][-1])
			j += 1
	return ''.join(result)

def getCurrExecTime(s_time):
	now = time.time()
	return now - s_time

xmlroot = getXML()
#saveXML(xmlroot, 'f.xml')
obj = SequencingProblem(xmlroot)

found_sequences = []
odd_path = []
even_path = []
visited_vertices = []
used_verifiers = []
state_snapshots = []

max_time = 300 # seconds
max_steps = obj.length - obj.probe_len*2 + 1
graph = buildGraph(obj.data[0].spectrum)
start = time.time()
# find odd path's first vertex
f_v = binary_search_v(obj.start, obj.data[0].spectrum)
odd_path.append(f_v[0])
#find even path's first vertex
f_v = binary_search(obj.start[1:], obj.data[0].spectrum, 1)
#TODO: handle the case that multiple candidates are found
even_path.append(f_v[0])
while getCurrExecTime(start) < max_time: #TODO?: add searchspace condition?
	if len(odd_path) > len(even_path):
		#TODO: find next vertex in even graph
	else:
		#TODO: find next vertex in odd graph
for sequence in found_sequences:
	print(sequence)