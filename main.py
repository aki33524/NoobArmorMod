import os
import shutil

from xml.etree import ElementTree as ET
import lxml.etree as etree

from visual import gun_visual, chassis_visual, default_visual
from primitives import merge_primitives
from model import get_model_path

DESC_DIR = 'data/vehicles'
MODEL_DIR = 'data/vehicles_level_01/vehicles'
OUTPUT_DIR = 'output/res/vehicles'

DEBUG = False

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
	hull_model_name = hull.find('models').find('undamaged').text.split('/')[-1].split('.')[0]
	desc[hull_model_name] = d

	# Turrets
	for turret in root.find('turrets0'):
		d = {}
		for armor in turret.find('armor'):
			if armor.find('vehicleDamageFactor') is not None:
				d[armor.tag] = (int(float(armor.text)), True)
			else:
				d[armor.tag] = (int(float(armor.text)), False)
		turret_model_name = turret.find('models').find('undamaged').text.split('/')[-1].split('.')[0]
		desc[turret_model_name] = d

		# Guns
		for gun in turret.find('guns'):
			d = {}
			for armor in gun.find('armor'):
				if armor.tag == 'gun' or armor.find('vehicleDamageFactor') is not None:
					d[armor.tag] = (int(float(armor.text)), True)
				else:
					d[armor.tag] = (int(float(armor.text)), False)
			gun_model_name = gun.find('models').find('undamaged').text.split('/')[-1].split('.')[0]
			desc[gun_model_name] = d

	# Chassis
	for chassis in root.find('chassis'):
		d = {}
		for armor in chassis.find('armor'):
			d[armor.tag] = (int(float(armor.text)), True)
		chassis_model_name = chassis.find('models').find('undamaged').text.split('/')[-1].split('.')[0]
		desc[chassis_model_name] = d

		if chassis.find('splineDesc'):
			segment_model_path = chassis.find('splineDesc').find('segmentModelLeft').text
			get_model_path(segment_model_path)

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
	
	BASE_PATH = os.path.join(MODEL_DIR, country, name)
	OUTPUT_PATH = os.path.join(OUTPUT_DIR, country, name)

	# FIXME:
	if not os.path.exists(os.path.join(BASE_PATH, 'normal')):
		return

	for c in os.listdir(os.path.join(BASE_PATH, 'normal')):
		# FIXME: It should use lod4 for memory
		if c == 'lod0':
			sdir = os.path.join(BASE_PATH, 'normal', c)
			ddir = os.path.join(OUTPUT_PATH, 'normal', c)
			try:
				os.makedirs(sdir)
			except FileExistsError:
				pass
			shutil.copytree(sdir, ddir)

	for c in os.listdir(os.path.join(BASE_PATH, 'collision_client')):
		if '.model' in c:
			"""
			FIXME
			It should rewrite model paths and copy models.
			"""
			model_path = os.path.join(BASE_PATH, 'collision_client', c)
			mroot = ET.parse(model_path).getroot()

			nv = mroot.find('nodelessVisual').text
			mroot.find('nodelessVisual').text = nv.replace('/collision_client', '/normal/lod0')
			mroot.append(ET.fromstring('<tank>true</tank>'))

			emroot = etree.fromstring(ET.tostring(mroot))
			s = etree.tostring(emroot, encoding='utf-8', pretty_print=True)

			model_path = os.path.join(OUTPUT_PATH, 'normal', 'lod0', c)

			if not DEBUG:
				with open(model_path, 'wb') as f:
					f.write(s)
					
		if '.visual_processed' in c:
			lod_path = os.path.join(BASE_PATH, 'normal', 'lod0', c)
			col_path = os.path.join(BASE_PATH, 'collision_client', c)

			# FIXME:
			if not os.path.exists(lod_path):
				continue

			lod_root = ET.parse(lod_path).getroot()
			col_root = ET.parse(col_path).getroot()
			model_name = c.split('.')[0]
			
			# FIXME:
			if model_name not in desc:
				continue

			if "Gun" in model_name:
				gun_visual(lod_root, col_root, desc[model_name])
			elif "Chassis" in model_name:
				chassis_visual(lod_root, col_root, desc[model_name])
			else:
				default_visual(lod_root, col_root, desc[model_name])

			lod_root = etree.fromstring(ET.tostring(lod_root))
			s = etree.tostring(lod_root, encoding='utf-8', pretty_print=True)

			model_path = os.path.join(OUTPUT_PATH, 'normal', 'lod0', c)
			if not DEBUG:
				with open(model_path, "wb") as f:
					f.write(s)

		if '.primitives_processed' in c:
			lod_path = os.path.join(BASE_PATH, 'normal', 'lod0', c)
			col_path = os.path.join(BASE_PATH, 'collision_client', c)

			# FIXME:
			if not os.path.exists(lod_path):
				continue

			model_path = os.path.join(OUTPUT_PATH, 'normal', 'lod0', c)
			if 'Chassis' in c:
				s = merge_primitives(lod_path, col_path)
				if not DEBUG:
					with open(model_path, "wb") as f:
						f.write(s)
			else:
				if not DEBUG:
					shutil.copy(col_path, model_path)

for country in os.listdir(DESC_DIR):
	if country == 'common':	
		continue

	root = ET.parse(os.path.join(DESC_DIR, country, 'list.xml')).getroot()
	for vehicle in root:
		level = int(vehicle.find('level').text)

		if level != 1:
			continue

		print(vehicle.tag)
		
		desc = load_desc(country, vehicle.tag)

		making_model(country, vehicle.tag, desc)

		shutil.make_archive('NoobArmorMod.wotmod', 'zip', 'output')
