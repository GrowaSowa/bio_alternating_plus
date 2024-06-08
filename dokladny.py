from include.seq_obj import SequencingProblem
from include.xml_parser import getXML, saveXML, loadXML
import xml.etree.ElementTree as ET

xmlroot = getXML()
#saveXML(xmlroot, 'f.xml')
obj = SequencingProblem(xmlroot)
#print('{}, {}, {}'.format(obj.key, obj.length, obj.start))
#for i in obj.data:
#	print('Probe: {} {}'.format(i.pattern, i.spectrum[0]))