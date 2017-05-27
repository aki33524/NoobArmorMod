import os
from xml.etree import ElementTree as ET
import lxml.etree as etree
from shutil import copyfile

OUTPUT_DIR_TEMPLATE = 'output/%s/res'
BASE_DIR = 'data'
DESC_DIR = 'data/xmls'

def make_path(d):
	output_dir = OUTPUT_DIR_TEMPLATE % ('level_%d'%(d['level']))
	return os.path.join(output_dir, 'vehicles', d['country'], d['name'])

if __name__ == '__main__':
	vehicles = {}
	for country in os.listdir(DESC_DIR):
		if country == 'common':	
			continue

		root = ET.parse(os.path.join(DESC_DIR, country, 'list.xml')).getroot()
		for vehicle in root:
			vid = vehicle.tag.split('_')[0]

			if vid not in vehicles:
				vehicles[vid] = []

			trans = {
				'china':'chinese',
				'czech':'czech',
				'france':'french',
				'germany':'german',
				'japan':'japan',
				'sweden':'sweden',
				'uk':'british',
				'usa':'american',
				'ussr':'russian'
			}
			d = {
				'level':int(vehicle.find('level').text),
				'country':trans[country],
				'name':vehicle.tag,
			}
			vehicles[vid].append(d)

	for k, v in vehicles.items():
		if len(v) == 1:
			continue
		
		primary = []
		imprimary = []
		for vv in v:
			path = os.path.join(BASE_DIR, 'vehicles', vv['country'], vv['name'])
			if os.path.exists(path):
				primary.append(vv)
			else:
				imprimary.append(vv)
		
		assert(len(primary) != 0)

		for p in primary:
			path = make_path(p)
			fileset = set()
			for root, dirs, files in os.walk(path):
				for file in files:
					fileset.add(os.path.join(root[len(path):], file))

			for ip in imprimary:
				path = make_path(ip)
				for root, dirs, files in os.walk(path):
					for file in files:
						rpath = os.path.join(root[len(path):], file)
						if rpath not in fileset:
							src = make_path(ip) + rpath
							dst = make_path(p) + rpath

							print(src, dst)
							copyfile(src, dst)