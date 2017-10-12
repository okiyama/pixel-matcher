from PIL import Image
from os import listdir
from os.path import isfile, join
import numpy as np
import sys

def main():
	childFolder = "./images"
	outputFolder = "./girl/"
	im = Image.open("./ff26454c6a2a626a12085b3b6c61e96d--dry-skin-your-skin.jpg")

	if len(sys.argv) > 1:
		imageCompare(int(sys.argv[1]), im, childFolder, outputFolder + "outCustom" + sys.argv[1] + ".png", False, True)
	else:
		for i in range(1,300):
			imageCompare(i, im, childFolder, outputFolder + "out" + str(i) + ".png", True)


def imageCompare(distanceThreshold, parentImage, childFolder, outputFileName = None, maxDistance = False, minDistance = False):
	childFiles = [f for f in listdir(childFolder) if isfile(join(childFolder, f))]
	w = parentImage.size[0]
	h = parentImage.size[1]

	finalImage = np.zeros((w, h, 3), dtype=np.uint8)
	maxDistances = np.zeros((w, h, 1), dtype=np.uint8)
	minDistances = np.full((w, h, 1), 999999999, dtype=np.uint8)

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

				if dist < distanceThreshold or (maxDistance and dist > maxDistances[row][col]) or (minDistance and dist < minDistances[row][col]):
					if(maxDistance):
						maxDistances[row][col] = dist
					if minDistance:
						minDistances[row][col] = dist
					close += 1
					finalImage[row][col] = childPixel
				total += 1


	print("close: " + str(close) + ", total: " + str(total) + " percent: " + str(float(close)/float(total) * 100))

	img = Image.fromarray(finalImage, 'RGB')
	if outputFileName is not None:
		img.save(outputFileName)

if __name__ == "__main__":
	main()