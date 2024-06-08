class Probe:
	def __init__(self, probe_elem):
		self.pattern = probe_elem.attrib['pattern']
		self.spectrum = []
		for pattern in probe_elem:
			self.spectrum.append(pattern.text)

class SequencingProblem:
	def __init__(self, xmltree):
		root = xmltree.getroot()
		self.key = root.attrib['key']
		self.length = root.attrib['length']
		self.start = root.attrib['start']
		self.data = []
		for probe in root:
			self.data.append(Probe(probe))