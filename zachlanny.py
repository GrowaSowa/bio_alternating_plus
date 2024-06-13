from include.seq_obj import SequencingProblem
from include.xml_parser import getXML, saveXML, loadXML
import xml.etree.ElementTree as ET
import sys

def compare(string1, string2):
    # assumes strings are of equal length
    for i in range(len(string1)):
        if string1[i] == string2[i] or string2[i] == 'X':
            continue
        if string1[i] < string2[i]:
            return -1
        if string1[i] > string2[i]:
            return 1
    return 0
        
def binary_search(pattern, items):
    l_i = 0
    r_i = len(items)-1
    while True:
        i = (l_i + r_i)//2
        val = compare(pattern, items[i][:-1])
        if val == 0:
            j = i+1
            while i>0 and compare(pattern, items[i-1][:-1])==0:
                i -= 1
            while j<len(items) and compare(pattern, items[j][:-1])==0:
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

def max_matching(nucleotides, current, verify_list):
	# use binary search to find potential matches
	matches = binary_search(current, nucleotides)
	if matches[0] == -1:
		# no matches found, rest in RIP
		return (-1,-1)
	else:
		# verify matches using 2nd spectrum
		for match in matches:
			next_bit = nucleotides[match][-1]
			pattern = current[1:] + next_bit
			verfs = binary_search_v(pattern, verify_list)
			if verfs[0] == -1:
				continue
			else:
				return (match, verfs[0])
		# verification failed
		return (-1,-1)

def greedy_main(xmlroot):
	obj = SequencingProblem(xmlroot)
	current_seq = obj.start
	nucleotides = obj.data[0].spectrum.copy()
	ctrl_spectrum = obj.data[1].spectrum.copy()

	while(len(current_seq) < obj.length):
		match_i = max_matching(nucleotides, current_seq[-((obj.probe_len-1)*2):], ctrl_spectrum)
		if match_i[0] == -1:
			return 'Stuck at local maximum, L BOZO'
		match_n = nucleotides.pop(match_i[0])
		ctrl_spectrum.pop(match_i[1])
		current_seq += match_n[-1:]
	return current_seq

xmlroot = getXML()
#saveXML(xmlroot, 'f.xml')
result = greedy_main(xmlroot)
print(result)