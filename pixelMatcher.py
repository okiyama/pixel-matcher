from PIL import Image
from os import listdir
from os.path import isfile, join
import numpy as np
import sys

def main():
	childFolder = "./images"
	im = Image.open("./BoYT0qQ8.jpg")
	distanceThreshold = int(sys.argv[1]) if len(sys.argv) > 1 else 75

	imageCompare(distanceThreshold, im, childFolder, "./output/out.bmp")


def imageCompare(distanceThreshold, parentImage, childFolder, outputFileName = None):
	childFiles = [f for f in listdir(childFolder) if isfile(join(childFolder, f))]
	w = parentImage.size[0]
	h = parentImage.size[1]

	finalImage = np.zeros((w, h, 3), dtype=np.uint8)

	close = 0
	total = 0
	for file in childFiles:
		childImage = Image.open(join(childFolder, file))
		childIterator = iter(childImage.getdata())
		parentIterator = iter(parentImage.getdata())

		for row in range(w):
			for col in range(h):
				pixel = np.array(next(parentIterator))
				childPixel = np.array(next(childIterator))
				dist = np.linalg.norm(pixel-childPixel)

				if dist < distanceThreshold:
					close += 1
					finalImage[row][col] = childPixel
				total += 1


	print("close: " + str(close) + ", total: " + str(total) + " percent: " + str(float(close)/float(total) * 100))

	img = Image.fromarray(finalImage, 'RGB')
	if outputFileName is not None:
		img.save(outputFileName)

if __name__ == "__main__":
	main()