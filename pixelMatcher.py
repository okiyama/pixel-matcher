from PIL import Image
from os import listdir
from os.path import join
import os
import numpy as np
import sys
import cProfile
import math
import subprocess
import time
import shutil
# from joblib import Parallel, delayed
import multiprocessing


class PixelMatcher:
	def __init__(self, childFolder, parentImagePath, customDiffThreshold=None):
		self.parentImage = Image.open(parentImagePath)
		self.parentImageData = np.asarray(self.parentImage)
		print(self.parentImageData)

		self.childImages = [Image.open(join(childFolder, f)) for f in listdir(childFolder) if os.path.isfile(join(childFolder, f))]
		self.childImageData = [np.asarray(c) for c in self.childImages]

		self.customDiffThreshold = customDiffThreshold
		self.imageWidth = self.parentImage.size[0]
		self.imageHeight = self.parentImage.size[1]
		self.diffMap = self.initDiffMap()

	def initDiffMap(self):
		diffMap = {}
		for i in range(len(self.childImages)):
			childImage = self.childImages[i]
			childImageData = self.childImageData[i]

			diffMap[childImage.filename] = np.zeros((self.imageWidth, self.imageHeight, 1), dtype=np.uint8)

			for row in range(self.imageWidth):
				for col in range(self.imageHeight):
					pixel = self.parentImageData[row][col]
					childPixel = childImageData[row][col]
					diffMap[childImage.filename][row][col] = self.distance(pixel, childPixel)

		return diffMap

	def clearOutputFolder(self, outputFolder):
		text = input("Clear contents of folder " + outputFolder + " ? ")
		if(text.lower() == "y"):
			shutil.rmtree(outputFolder)
			os.makedirs(outputFolder)
		else:
			sys.exit()


	def makeCompareGif(self, outputFolder, maxMin="max", loops=300, stepSize=1, gifOutputFolder="./gifs"):
		self.clearOutputFolder(outputFolder)

		num_cores = multiprocessing.cpu_count()

		for i in range(1, loops, stepSize):
			outputFileName = outputFolder + "/" + maxMin + "out" + format(i, '05') + ".png"
			if maxMin == "max":
				self.maxCompareImage(i, outputFileName)
			elif maxMin == "min":
				self.minCompareImage(i, outputFileName)
			else:
				raise ValueError()

		self.makeGif(outputFolder, gifOutputFolder)

	def makeGif(self, pngFolder, gifFolder):
		gifOutputFile = gifFolder + "/animation" + str(int(time.time())) + ".gif"
		open(gifOutputFile, "w")
		os.path.dirname(os.path.realpath(__file__))
		subprocess.call("convert -layers OptimizePlus -coalesce -duplicate 1,-2-1 -delay 0 -loop 0 " + pngFolder + "*.png " + gifOutputFile, shell=True)

	def compareImage(self, distanceThreshold, outputFileName, distancesArray, eligiblityFunction):
		finalImage = np.zeros((self.imageWidth, self.imageHeight, 3), dtype=np.uint8)

		close = 0
		total = 0
		for i in range(len(self.childImages)):
			childImage = self.childImages[i]
			childImageData = self.childImageData[i]

			childIterator = iter(childImage.getdata())

			for row in range(self.imageWidth):
				for col in range(self.imageHeight):
					childPixel = childImageData[row][col]
					dist = self.diffMap[childImage.filename][row][col]

					if eligiblityFunction(dist, distanceThreshold, distancesArray, row, col):
						distancesArray[row][col] = dist
						close += 1
						finalImage[row][col] = childPixel
					total += 1

		print("close: " + str(close) + ", total: " + str(total) + " percent: " + str(float(close)/float(total) * 100))

		Image.fromarray(finalImage, 'RGB').save(outputFileName)

	def maxElibilityFunction(self, distance, distanceThreshold, maxDistances, row, col):
		return distance < distanceThreshold and distance > maxDistances[row][col]

	def maxCompareImage(self, distanceThreshold, outputFileName):
		maxDistances = np.zeros((self.imageWidth, self.imageHeight, 1), dtype=np.uint16)

		return self.compareImage(distanceThreshold, outputFileName, maxDistances, self.maxElibilityFunction)
		
	def minEligibilityFunction(self, distance, distanceThreshold, minDistances, row, col):
		return distance < distanceThreshold and distance < minDistances[row][col]

	def minCompareImage(self, distanceThreshold, outputFileName):
		minDistances = np.full((self.imageWidth, self.imageHeight, 1), 9999999, dtype=np.uint16)
	
		return self.compareImage(distanceThreshold, outputFileName, minDistances, self.minElibilityFunction)

	def distance(self, t1, t2):
		return math.sqrt( ((t1[0] - t2[0])**2) + ((t1[1] - t2[1])**2) + ((t1[2] - t2[2])**2) )


#Note: 441.673 is the max distance between two pixels
def main():
	customDiffThreshold = None
	if len(sys.argv) > 1:
		customDiffThreshold = int(sys.argv[1])

	# parentFolder = "./parents/"
	childFolder = "./abstract/"
	outputFolder = "./output/"
	parentImagePath = "./parents/abstract-colorsdd3a-marilyn-sq.jpg"
	matcher = PixelMatcher(childFolder, parentImagePath, customDiffThreshold=customDiffThreshold)

	# matcher.minCompareImage(1000, outputFolder + "outTest.png")
	matcher.makeCompareGif(outputFolder, loops=20, maxMin="max", )
	# matcher.maxCompareImage(100, "")

if __name__ == "__main__":
	main()