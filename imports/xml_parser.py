import requests
import xml.etree.ElementTree as ET

def getXML(n=500, k=10, sqpe=100):
	# n - długość sekwencji (16-65535)
	n = clamp(n, 16, 65535)
	# k - długość sondy (4-10)
	k = clamp(k, 4, 10)
	# sqpe - liczba błędów pozytywnych (max n/4)
	sqpe = clamp(sqpe, 0, n/4)
	url = 'https://www.cs.put.poznan.pl/pwawrzyniak/bio/bio.php?n={}&k={}&mode=alternating&intensity=0&position=0&sqpe={}&sqne=0&pose=0'.format(n, k, sqpe)

	response = requests.get(url)
	return ET.fromstring(response.content)

def saveXML(xml, fname):
	b_xml = ET.tostring(xml)
	with open(fname, 'wb') as f:
		f.write(b_xml)

def loadXML(fname):
	return ET.parse(fname)

def clamp(val, minval, maxval):
	if val < minval:
		return minval
	elif val > maxval:
		return maxval
	return val


# example leftover code
'''
from seq_obj import SequencingProblem
xmlf = getXML()
saveXML(xmlf, 'file.xml')
xmlf2 = loadXML('file.xml')
obj = SequencingProblem(xmlf2)
print('{}, {}, {}'.format(obj.key, obj.length, obj.start))
for i in obj.data:
	print('Probe: {} {}'.format(i.pattern, i.spectrum[0]))
'''