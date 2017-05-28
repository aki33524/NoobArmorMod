def replace_texture(lod_root, desc):
	primitiveGroups = lod_root.find('renderSet').find('geometry')
	for primitiveGroup in primitiveGroups.findall('primitiveGroup'):
		material = primitiveGroup.find('material')
		name = material.find('identifier').text
		# FIXME:
		# surveyingDevice
		if name not in desc:
			continue

		if desc[name][1]:
			png = 'sarmor/%d.png' % desc[name][0]
		else:
			png = 'armor/%d.png' % desc[name][0]
		for v in material.findall('property'):
			if v.find('Texture') is not None:
				v.find('Texture').text = png

def default_visual(lod_root, col_root, desc):
	l = ['renderSet', 'boundingBox', 'minUVDensity', 'geometrySize']
	for v in l:
		lod_root.remove(lod_root.find(v))
		lod_root.append(col_root.find(v))
	replace_texture(lod_root, desc)

def gun_visual(lod_root, col_root, desc):
	l = ['renderSet', 'boundingBox', 'minUVDensity', 'geometrySize']
	for v in l:
		lod_root.remove(lod_root.find(v))
		lod_root.append(col_root.find(v))
	node = lod_root.find('renderSet').find('node')
	node.text = 'Gun'
	replace_texture(lod_root, desc)

def walk(root, remove_list):
	for node in root.findall('node'):
		if node.find('identifier').text in remove_list:
			for c in node.find('transform')[:3]:
				c.text = '0.0 0.0 0.0'
		walk(node, remove_list)

def chassis_visual(lod_root, col_root, desc):
	l = ['boundingBox', 'minUVDensity', 'geometrySize']
	for v in l:
		lod_root.remove(lod_root.find(v))
		lod_root.append(col_root.find(v))

	remove_list = []
	for renderset in lod_root.findall('renderSet'):
		for c in renderset.findall('node'):
			remove_list.append(c.text)
	remove_list = sorted(set(remove_list))
	walk(lod_root, remove_list)
	lod_root.insert(0, col_root.find('renderSet'))
	
	replace_texture(lod_root, desc)

# def segment_visual(lod_root):
# 	print(lod_root.find('library_visual_scenes/visual_scene/node/matrix').text)
