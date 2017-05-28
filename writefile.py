import os
import shutil

def writefile(filepath, s):
	dir_path = os.path.dirname(filepath)
	try:
		os.makedirs(dir_path)
	except FileExistsError:
		pass

	with open(filepath, "wb") as f:
		f.write(s)

def copyfile(src, dst):
	dir_path = os.path.dirname(dst)
	try:
		os.makedirs(dir_path)
	except FileExistsError:
		pass
	shutil.copy(src, dst)
