import os
from xml.etree import ElementTree as ET

# BASE_DIR = 'data'

def get_model_path(model_path):
	# Hack
	if not os.path.exists(os.path.join('data', model_path)):
		if '\\' in model_path:
			model_path = model_path.replace('\\', '/')

		dirname, filename = os.path.split(model_path)
		
		if 'turret' in filename:
			filename = filename.replace('turret', 'Turret')
		model_path = os.path.join(dirname, filename)
					
		if not os.path.exists(model_path) and 'Track' in dirname:
			dirname = dirname.replace('Track', 'track')
		model_path = os.path.join(dirname, filename)

	open(os.path.join('data', model_path))
	root = ET.parse(os.path.join('data', model_path)).getroot()

	if root.find('nodefullVisual') is not None:
		return root.find('nodefullVisual').text
	if root.find('nodelessVisual') is not None:
		return root.find('nodelessVisual').text
	raise