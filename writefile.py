import os

def writefile(filepath, s):
	dir_path = os.path.dirname(filepath)
	try:
		os.makedirs(dir_path)
	except FileExistsError:
		pass

	with open(filepath, "wb") as f:
		f.write(s)