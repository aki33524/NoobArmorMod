import os
import shutil

from xml.etree import ElementTree as ET
import lxml.etree as etree

from visual import gun_visual, chassis_visual, default_visual
from primitives import merge_primitives
from model import get_model_path
from writefile import writefile, copyfile

BASE_DIR = 'data'
DESC_DIR = 'data/xmls'
OUTPUT_DIR = 'output/res'

DEBUG = False

def load_desc(country, name):
	xml_path = os.path.join(DESC_DIR, country, name+'.xml')
	root = ET.parse(xml_path).getroot()

	desc = {}

	# Hull
	d = {}
	hull = root.find('hull')
	for armor in hull.find('armor'):
		if armor.find('vehicleDamageFactor') is not None:
			d[armor.tag] = (int(float(armor.text)), True)
		else:
			d[armor.tag] = (int(float(armor.text)), False)
	normal_path = get_model_path(hull.find('models/undamaged').text)
	l = normal_path.split('/')
	l[2] = name
	hull.find('models/undamaged').text = os.path.join(*l)+'.model'
	
	collision_path = get_model_path(hull.find('hitTester').find('collisionModelClient').text)
	# Hack
	model_name = normal_path.split('/')[-1]
	desc[model_name] = {'armor':d, 'normal':normal_path, 'collision':collision_path, 'type':'hull'}

	# Turrets
	for turret in root.find('turrets0'):
		d = {}
		for armor in turret.find('armor'):
			if armor.find('vehicleDamageFactor') is not None:
				d[armor.tag] = (int(float(armor.text)), True)
			else:
				d[armor.tag] = (int(float(armor.text)), False)
		normal_path = get_model_path(turret.find('models/undamaged').text)
		l = normal_path.split('/')
		l[2] = name
		turret.find('models/undamaged').text = os.path.join(*l)+'.model'

		collision_path = get_model_path(turret.find('hitTester/collisionModelClient').text)
		# Hack
		model_name = normal_path.split('/')[-1]
		desc[model_name] = {'armor':d, 'normal':normal_path, 'collision':collision_path, 'type':'turret'}

		# Guns
		for gun in turret.find('guns'):
			d = {}
			for armor in gun.find('armor'):
				if armor.tag == 'gun' or armor.find('vehicleDamageFactor') is not None:
					d[armor.tag] = (int(float(armor.text)), True)
				else:
					d[armor.tag] = (int(float(armor.text)), False)
			normal_path = get_model_path(gun.find('models/undamaged').text)
			l = normal_path.split('/')
			l[2] = name
			gun.find('models/undamaged').text = os.path.join(*l)+'.model'

			collision_path = get_model_path(gun.find('hitTester/collisionModelClient').text)
			# Hack
			model_name = normal_path.split('/')[-1]
			desc[model_name] = {'armor':d, 'normal':normal_path, 'collision':collision_path, 'type':'gun'}

	# Chassis
	for chassis in root.find('chassis'):
		d = {}
		for armor in chassis.find('armor'):
			d[armor.tag] = (int(float(armor.text)), True)
		normal_path = get_model_path(chassis.find('models/undamaged').text)
		l = normal_path.split('/')
		l[2] = name
		chassis.find('models/undamaged').text = os.path.join(*l)+'.model'

		collision_path = get_model_path(chassis.find('hitTester/collisionModelClient').text)
		# Hack
		model_name = normal_path.split('/')[-1]
		desc[model_name] = {'armor':d, 'normal':normal_path, 'collision':collision_path, 'type':'chassis'}

		if chassis.find('splineDesc') is not None:
			chassis.find('splineDesc/segmentLength').text = '0'
			eroot = etree.fromstring(ET.tostring(root))
			s = etree.tostring(eroot, encoding='utf-8', pretty_print=True)
			outpath = os.path.join(OUTPUT_DIR, 'scripts/item_defs/vehicles/', country, name+'.xml')
			writefile(outpath, s)

	return desc

def making_model(country, name, desc):
	d = {
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
	country = d[country]

	OUTPUT_BASE = os.path.join(OUTPUT_DIR, 'vehicles', country, name)
	
	for v in desc.values():
		opath = os.path.join(OUTPUT_BASE, *v['normal'].split('/')[-3:])
		
		"""
		model
		"""
		lod_path = os.path.join(BASE_DIR, v['normal']+'.model')
		lod_root = ET.parse(lod_path).getroot()

		if lod_root.find('parent') is not None:
			lod_root.remove(lod_root.find('parent'))
			lod_root.remove(lod_root.find('extent'))
		
		if lod_root.find('nodelessVisual') is not None:
			lod_root.find('nodelessVisual').text = os.path.join(*opath.split('/')[2:])
		if lod_root.find('nodefullVisual') is not None:
			lod_root.find('nodefullVisual').text = os.path.join(*opath.split('/')[2:])
		
		lod_root = etree.fromstring(ET.tostring(lod_root))
		s = etree.tostring(lod_root, encoding='utf-8', pretty_print=True)

		writefile(opath+'.model', s)

		"""
		visual_processed
		"""
		lod_path = os.path.join(BASE_DIR, v['normal']+'.visual_processed')
		lod_root = ET.parse(lod_path).getroot()
			
		model_name = v['normal'].split('/')[-1]

		col_path = os.path.join(BASE_DIR, v['collision']+'.visual_processed')
		col_root = ET.parse(col_path).getroot()

		if "Gun" in model_name:
			gun_visual(lod_root, col_root, desc[model_name]['armor'])
		elif "Chassis" in model_name:
			chassis_visual(lod_root, col_root, desc[model_name]['armor'])
		else:
			default_visual(lod_root, col_root, desc[model_name]['armor'])

		lod_root = etree.fromstring(ET.tostring(lod_root))
		s = etree.tostring(lod_root, encoding='utf-8', pretty_print=True)

		writefile(opath+'.visual_processed', s)

		"""
		primitives_processed
		"""
		lod_path = os.path.join(BASE_DIR, v['normal']+'.primitives_processed')
		model_name = v['normal'].split('/')[-1]
		
		col_path = os.path.join(BASE_DIR, v['collision']+'.primitives_processed')
		
		if v['type'] == 'chassis':
			s = merge_primitives(lod_path, col_path)
			writefile(opath+'.primitives_processed', s)
		else:
			copyfile(col_path, opath+'.primitives_processed')

if __name__ == '__main__':
	black_list = [
		'Ch01_Type59_Gold',
		'Ch03_WZ_111_A',
	]

	for country in os.listdir(DESC_DIR):
		if country == 'common':	
			continue

		root = ET.parse(os.path.join(DESC_DIR, country, 'list.xml')).getroot()
		for vehicle in root:
			if vehicle.tag in black_list:
				continue

			print(vehicle.tag)
			
			desc = load_desc(country, vehicle.tag)
			# for k, v in desc.items():
			# 	print(k)
			# 	print(v)
			making_model(country, vehicle.tag, desc)
