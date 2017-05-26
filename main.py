import os
import shutil

from xml.etree import ElementTree as ET
import lxml.etree as etree

from visual import gun_visual, chassis_visual, default_visual, segment_visual
from primitives import merge_primitives
from model import get_model_path
from writefile import writefile

BASE_DIR = 'data'
DESC_DIR = 'data/xmls'
OUTPUT_DIR = 'output/res'

DEBUG = True

def load_desc(country, name):
	root = ET.parse(os.path.join(DESC_DIR, country, name+'.xml')).getroot()

	desc = {}

	# Hull
	d = {}
	hull = root.find('hull')
	for armor in hull.find('armor'):
		if armor.find('vehicleDamageFactor') is not None:
			d[armor.tag] = (int(float(armor.text)), True)
		else:
			d[armor.tag] = (int(float(armor.text)), False)
	normal_path = get_model_path(hull.find('models').find('undamaged').text)
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
		normal_path = get_model_path(turret.find('models').find('undamaged').text)
		collision_path = get_model_path(turret.find('hitTester').find('collisionModelClient').text)
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
			normal_path = get_model_path(gun.find('models').find('undamaged').text)
			collision_path = get_model_path(gun.find('hitTester').find('collisionModelClient').text)
			# Hack
			model_name = normal_path.split('/')[-1]
			desc[model_name] = {'armor':d, 'normal':normal_path, 'collision':collision_path, 'type':'gun'}

	# Chassis
	for chassis in root.find('chassis'):
		d = {}
		for armor in chassis.find('armor'):
			d[armor.tag] = (int(float(armor.text)), True)
		normal_path = get_model_path(chassis.find('models').find('undamaged').text)
		collision_path = get_model_path(chassis.find('hitTester').find('collisionModelClient').text)
		# Hack
		model_name = normal_path.split('/')[-1]
		desc[model_name] = {'armor':d, 'normal':normal_path, 'collision':collision_path, 'type':'chassis'}

		if chassis.find('splineDesc') is not None:
			normal_path = get_model_path(chassis.find('splineDesc').find('segmentModelLeft').text)
			model_name = normal_path.split('/')[-1]
			d = {'normal':normal_path, 'type':'segment'}
			desc[model_name] = d

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
	
	for k, v in desc.items():
		flag = True
		l1 = ['.visual_processed', '.primitives_processed']
		l2 = ['normal', 'collision']
		for x in l1:
			for y in l2:
				if y in v:
					model_path = os.path.join(BASE_DIR, v[y]+x)
					if '\\' in model_path:
						model_path = model_path.replace('\\', '/')
					
					dirname, filename = os.path.split(model_path)
					
					if 'turret' in filename:
						filename = filename.replace('turret', 'Turret')
					model_path = os.path.join(dirname, filename)
				
					if not os.path.exists(model_path):
						if 'Track' in dirname:
							dirname = dirname.replace('Track', 'track')
						elif 'track' in dirname:
							dirname = dirname.replace('track', 'Track')
					model_path = os.path.join(dirname, filename)

					flag &= os.path.exists(model_path)
		assert(flag)

	for v in desc.values():
		"""
		FIXME
		Should it rewrite model paths and copy models?.
		"""
		# model_path = os.path.join(BASE_PATH, v['collision'], c)
		# mroot = ET.parse(model_path).getroot()

		# nv = mroot.find('nodelessVisual').text
		# mroot.find('nodelessVisual').text = nv.replace('/collision_client', '/normal/lod0')
		# mroot.append(ET.fromstring('<tank>true</tank>'))

		# emroot = etree.fromstring(ET.tostring(mroot))
		# s = etree.tostring(emroot, encoding='utf-8', pretty_print=True)

		# model_path = os.path.join(OUTPUT_PATH, 'normal', 'lod0', c)

		# if not DEBUG:
		# 	with open(model_path, 'wb') as f:
		# 		f.write(s)

		"""
		visual_processed
		"""
		lod_path = os.path.join(BASE_DIR, v['normal']+'.visual_processed')
		lod_root = ET.parse(lod_path).getroot()
			
		model_name = v['normal'].split('/')[-1]

		if v['type'] == 'segment':
			segment_visual(lod_root)
		else:
			# print(model_name)
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

		model_path = os.path.join(OUTPUT_DIR, v['normal']+'.visual_processed')
		if not DEBUG:
			writefile(model_path, s)

		"""
		primitives_processed
		"""
		lod_path = os.path.join(BASE_DIR, v['normal']+'.primitives_processed')
		model_path = os.path.join(OUTPUT_DIR, v['normal']+'.primitives_processed')
		model_name = v['normal'].split('/')[-1]
		
		if v['type'] == 'segment':
			col_path = 	lod_path
		else:		
			col_path = os.path.join(BASE_DIR, v['collision']+'.primitives_processed')
		
		if 'Chassis' in model_name:
			s = merge_primitives(lod_path, col_path)
			if not DEBUG:
				writefile(model_path, s)
		else:
			if not DEBUG:
				# OK?
				shutil.copy(col_path, model_path)

		"""
		model
		"""
		sdir = os.path.join(BASE_DIR, v['normal']+'.model')
		ddir = os.path.join(OUTPUT_DIR, v['normal']+'.model')
		if not DEBUG:
			shutil.copy(sdir, ddir)
				

if __name__ == '__main__':
	black_list = [
		'Ch01_Type59_Gold',
		'Ch03_WZ_111_A',
	]

	for country in os.listdir(DESC_DIR):
		if country == 'common':	
			continue

		if DEBUG and country != 'japan':
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

		# 	shutil.make_archive('NoobArmorMod.wotmod', 'zip', 'output')
