def replace_texture(lod_root, desc):
	primitiveGroups = lod_root.find('renderSet').find('geometry')
	for primitiveGroup in primitiveGroups.findall('primitiveGroup'):
		material = primitiveGroup.find('material')
		name = material.find('identifier').text
		# FIXME:
		if name not in desc:
			continue

		if desc[name][1]:
			dds = 'vehicles/sarmor/%d.dds' % desc[name][0]
		else:
			dds = 'vehicles/armor/%d.dds' % desc[name][0]
		material.find('property').find('Texture').text = dds

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


