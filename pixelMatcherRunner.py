from PIL import Image
from os import listdir
from os.path import join
import os
import numpy as np
import sys
import cProfile
import math
import argparse
import time

#TODO either fix min or drop support
class PixelMatcherRunner:
	def __init__(self, childFolder, parentImagePath):
		self.parentImage = Image.open(parentImagePath)
		self.parentImageData = np.asarray(self.parentImage)
		self.imageWidth = self.parentImage.size[0]
		self.imageHeight = self.parentImage.size[1]

		self.childImages = [Image.open(join(childFolder, f)).convert("RGB") for f in listdir(childFolder) if os.path.isfile(join(childFolder, f))]
		self.childImageData = [np.asarray(c) for c in self.childImages]
		#Only works for up to 65,536 children. Probably a good limit
		self.currentDiffIndicies = np.zeros((self.imageHeight, self.imageWidth), dtype=np.int16)
		self.childSortedIndicies = None

		self.diffMap = self.initDiffMap()

	def initDiffMap(self):
		diffMap = np.zeros((self.imageHeight, self.imageWidth, len(self.childImageData)), dtype=np.float64)
		for i in range(len(self.childImages)):
			childImage = self.childImages[i]
			childImageData = self.childImageData[i]

			#diffMap[childImage.filename] = np.zeros((self.imageHeight, self.imageWidth, 1), dtype=np.float64)

			for row in range(self.imageHeight):
				for col in range(self.imageWidth):
					pixel = self.parentImageData[row][col]
					childPixel = childImageData[row][col]
					#First element in the array at a particular pixel is the current child index, which starts at 0
					diffMap[row][col][i] = self.distance(pixel, childPixel)

		#sort diffMap
		#TODO sort opposite for min
		self.childSortedIndicies = np.argsort(diffMap)
		#print(self.childSortedIndicies)
		#print(diffMap)
		
		return diffMap

	def makeCompareImages(self, outputFolder, start, stop, step=1, maxMin="max"):
		self.ensureWidthDivisibleByTwo()

		for i in range(start, stop, step):
			print("starting image " + str(i) + " of " + str(stop) + " (" + str(float(i-start)/float(stop-start)*100) + "%)")
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

	def compareImage(self, distanceThreshold, outputFileName):
		# finalImage = np.zeros((self.imageWidth, self.imageHeight, 3), dtype=np.uint8)
		finalImage = np.copy(self.parentImage)

		close = 0
		total = 0
		for row in range(self.imageHeight):
			for col in range(self.imageWidth):
				#Since we've sorted diffMap by the distances, we can check first to see if the last child we used was the correct one or not
				#If it's not, then we'll continue on down the line
				currentDiffIndex = self.currentDiffIndicies[row][col]
				currentChildIndex = self.childSortedIndicies[row][col][currentDiffIndex]
				currentDistance = self.diffMap[row][col][currentChildIndex]
				
				if currentDistance < distanceThreshold:
					# close += 1
					finalImage[row][col] = self.childImageData[currentChildIndex][row][col]

					if currentDiffIndex + 1 < len(self.childImages):
						nextDiffIndex = currentDiffIndex + 1
						nextChildIndex = self.childSortedIndicies[row][col][nextDiffIndex]
						nextDistance = self.diffMap[row][col][nextChildIndex]

						if nextDistance < distanceThreshold:
							self.currentDiffIndicies[row][col] += 1
				# total += 1

		# print("max of max: " + str(max(distancesArray.flatten('F').tolist())))
		# print("close: " + str(close) + ", total: " + str(total) + " percent: " + str(float(close)/float(total) * 100))

		Image.fromarray(finalImage, 'RGB').save(outputFileName)

	def maxCompareImage(self, distanceThreshold, outputFileName):
		return self.compareImage(distanceThreshold, outputFileName)
		
	def minCompareImage(self, distanceThreshold, outputFileName):
		print("MIN NOT WORKING")
		exit()
		return self.compareImage(distanceThreshold, outputFileName)

	def distance(self, t1, t2):
		#print("pix 1: " + str(t1) + ", pix 2: " + str(t2))
		return np.linalg.norm(t1-t2)
		#return math.sqrt( ((t1[0] - t2[0])**2) + ((t1[1] - t2[1])**2) + ((t1[2] - t2[2])**2) )


#Note: 441.673 is the max distance between two pixels
def main(start, stop, outputFolder, childFolder, parentImagePath, maxMin="max", step=1):
	# print("start" + str(start) + str(type(start)))
	# print("stop" + str(stop) + str(type(stop)))
	# print("outputFolder" + str(outputFolder) + str(type(outputFolder)))
	# print("childFolder" + str(childFolder) + str(type(childFolder)))
	# print("parentImagePath" + str(parentImagePath) + str(type(parentImagePath)))
	# print("maxMin" + str(maxMin) + str(type(maxMin)))
	# print("step" + str(step) + str(type(step)))
	
	now = time.time()
	runner = PixelMatcherRunner(childFolder, parentImagePath)
	runner.makeCompareImages(outputFolder, start, stop, step=step, maxMin=maxMin)
	later = time.time()
	print("Took this child " + str(later - now) + " seconds to do " + str(stop - start) + " from " + str(start) + " to " + str(stop))

if __name__ == '__main__':
	main(0, 100, "./output/", "./abstract - resized/", "./glitch_girl_small.jpg")