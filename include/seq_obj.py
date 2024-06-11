class Probe:
	def __init__(self, probe_elem):
		self.pattern = probe_elem.attrib['pattern']
		self.spectrum = []
		for pattern in probe_elem:
			self.spectrum.append(pattern.text)

class SequencingProblem:
	def __init__(self, xmlroot):
		self.key = xmlroot.attrib['key']
		self.length = int(xmlroot.attrib['length'])
		self.start = xmlroot.attrib['start']
		self.probe_len = len(self.start)//2 + 1
		self.data = []
		for probe in xmlroot:
			self.data.append(Probe(probe))