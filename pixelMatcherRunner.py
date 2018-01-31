from PIL import Image
from os import listdir
from os.path import join
import os
import numpy as np
import sys
import cProfile
import math
import argparse


class PixelMatcherRunner:
	def __init__(self, childFolder, parentImagePath):
		self.parentImage = Image.open(parentImagePath)
		self.parentImageData = np.asarray(self.parentImage)

		self.childImages = [Image.open(join(childFolder, f)) for f in listdir(childFolder) if os.path.isfile(join(childFolder, f))]
		self.childImageData = [np.asarray(c) for c in self.childImages]

		self.imageWidth = self.parentImage.size[0]
		self.imageHeight = self.parentImage.size[1]
		self.diffMap = self.initDiffMap()

	def initDiffMap(self):
		diffMap = {}
		for i in range(len(self.childImages)):
			childImage = self.childImages[i]
			childImageData = self.childImageData[i]

			diffMap[childImage.filename] = np.zeros((self.imageWidth, self.imageHeight, 1), dtype=np.float64)

			for row in range(self.imageHeight):
				for col in range(self.imageWidth):
					pixel = self.parentImageData[row][col]
					childPixel = childImageData[row][col]
					diffMap[childImage.filename][row][col] = self.distance(pixel, childPixel)

		return diffMap

	def makeCompareImages(self, outputFolder, start, stop, step=1, maxMin="max"):
		self.ensureWidthDivisibleByTwo()

		for i in range(start, stop, step):
			outputFileName = outputFolder + "/" + "out" + format(i, '05') + ".png"
			if maxMin == "max":
				self.maxCompareImage(i, outputFileName)
			elif maxMin == "min":
				self.minCompareImage(i, outputFileName)
			else:
				raise ValueError("Invalid argument for maxMin")

	# We can only make an MP4 if they width of the images is divisible by 2
	def ensureWidthDivisibleByTwo(self):
		if self.parentImage.width % 2 != 0:
			print("Width of images must be divisible by 2 to make an mp4")
			sys.exit()

	def compareImage(self, distanceThreshold, outputFileName, distancesArray, eligiblityFunction):
		# finalImage = np.zeros((self.imageWidth, self.imageHeight, 3), dtype=np.uint8)
		finalImage = np.copy(self.parentImage)

		close = 0
		total = 0
		for i in range(len(self.childImages)):
			childImage = self.childImages[i]
			childImageData = self.childImageData[i]
			childDiffMap = self.diffMap[childImage.filename]

			for row in range(self.imageHeight):
				for col in range(self.imageWidth):
					childPixel = childImageData[row][col]
					dist = childDiffMap[row][col]

					if eligiblityFunction(dist, distanceThreshold, distancesArray, row, col):
						distancesArray[row][col] = dist
						# close += 1
						finalImage[row][col] = childPixel
					# total += 1

		# print("max of max: " + str(max(distancesArray.flatten('F').tolist())))
		# print("close: " + str(close) + ", total: " + str(total) + " percent: " + str(float(close)/float(total) * 100))

		Image.fromarray(finalImage, 'RGB').save(outputFileName)

	def maxEligibilityFunction(self, distance, distanceThreshold, maxDistances, row, col):
		return distance < distanceThreshold and distance > maxDistances[row][col]

	def maxCompareImage(self, distanceThreshold, outputFileName):
		maxDistances = np.zeros((self.imageWidth, self.imageHeight, 1), dtype=np.float64)

		return self.compareImage(distanceThreshold, outputFileName, maxDistances, self.maxEligibilityFunction)
		
	def minEligibilityFunction(self, distance, distanceThreshold, minDistances, row, col):
		return distance < distanceThreshold and distance < minDistances[row][col]

	def minCompareImage(self, distanceThreshold, outputFileName):
		minDistances = np.full((self.imageWidth, self.imageHeight, 1), 9999999, dtype=np.float64)
	
		return self.compareImage(distanceThreshold, outputFileName, minDistances, self.minEligibilityFunction)

	def distance(self, t1, t2):
		return math.sqrt( ((t1[0] - t2[0])**2) + ((t1[1] - t2[1])**2) + ((t1[2] - t2[2])**2) )


#Note: 441.673 is the max distance between two pixels
def main(start, stop, outputFolder, childFolder, parentImagePath, maxMin="max", step=1):
	# print("start" + str(start) + str(type(start)))
	# print("stop" + str(stop) + str(type(stop)))
	# print("outputFolder" + str(outputFolder) + str(type(outputFolder)))
	# print("childFolder" + str(childFolder) + str(type(childFolder)))
	# print("parentImagePath" + str(parentImagePath) + str(type(parentImagePath)))
	# print("maxMin" + str(maxMin) + str(type(maxMin)))
	# print("step" + str(step) + str(type(step)))
	
	runner = PixelMatcherRunner(childFolder, parentImagePath)
	runner.makeCompareImages(outputFolder, start, stop, step=step, maxMin=maxMin)

if __name__ == '__main__':
	main(0, 100, "./output/", "./abstract - resized/", "./glitch_girl_small.jpg")