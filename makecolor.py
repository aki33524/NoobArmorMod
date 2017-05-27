from PIL import Image
import os

OUTPUT_DIR = 'output/colors/res'
LU = 32
L = 128

D = 256*2//L

# RGB
def get_color1(x):
	A = 256
	if x < LU:
		return (0, 255, 0, A)

	x -= LU
	if x < L//2:
		color = (min(255, x*D), 255, 0, A)
	elif x <= L:
		color = (255, max(0, 255-D*(x-L//2)), 0, A)
	else:
		color = (255, 0, 0, A)

	return color

def get_color2(x):
	A = 128
	if x < LU:
		return (0, 255, 255, A)

	x -= LU
	if x < L//2:
		color = (0, max(0, 255-D*x), 255, A)
	elif x <= L:
		color = (min(255, (x-L//2)*D), 0, 255, A)
	else:
		color = (255, 0, 255)

	return color

if __name__ == '__main__':
	img1 = Image.new("RGBA", (1, 1))
	img2 = Image.new("RGBA", (1, 1))

	for i in range(400):
		img1.putpixel((0, 0), get_color1(i))
		img2.putpixel((0, 0), get_color2(i))

		img1.save(os.path.join(OUTPUT_DIR, 'armor', '%d.png' %i))
		img2.save(os.path.join(OUTPUT_DIR, 'sarmor', '%d.png' %i))
