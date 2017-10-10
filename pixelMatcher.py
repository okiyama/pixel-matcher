from PIL import Image
from os import listdir
from os.path import isfile, join
import numpy as np

childFolder = "./images"
childFiles = [f for f in listdir(childFolder) if isfile(join(childFolder, f))]
im = Image.open("./BoYT0qQ8.jpg")
w = im.size[0]
h = im.size[1]

resultantImageFlat = []

distanceThreshold = 500
close = 0
total = 0
for file in childFiles:
	childImage = Image.open(join(childFolder, file))
	childIterator = iter(childImage.getdata())
	for pixel in iter(im.getdata()):
		pixel = np.array(pixel)
		try:
			childPixel = np.array(next(childIterator))
			dist = np.linalg.norm(pixel-childPixel)

			if dist < distanceThreshold:
				close += 1
			total += 1
			if dist < distanceThreshold:
				resultantImageFlat.append(list(pixel))
			else:
				resultantImageFlat.append([255, 255, 255])
		except (StopIteration, ValueError) as error:
			print(pixel)
			print(childPixel)
			print(file)
			break

print("close: " + str(close) + ", total: " + str(total) + " percent: " + str(float(close)/float(total) * 100))

finalImage = np.zeros((h, w, 3), dtype=np.uint8)

flatCounter = 0
for row in range(im.size[1]):
	currRow = []
	for col in range(im.size[0]):
		finalImage[row, col] = resultantImageFlat[flatCounter]
		flatCounter += 1

# print(finalImage)

img = Image.fromarray(finalImage, 'RGB')
img.show()