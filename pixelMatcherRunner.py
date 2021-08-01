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

		self.childImages = [Image.open(join(childFolder, f)).convert("RGB") for f in listdir(childFolder) if os.path.isfile(join(childFolder, f))]
		self.childImageData = [np.asarray(c) for c in self.childImages]
		#print(self.childImageData)

		self.imageWidth = self.parentImage.size[0]
		self.imageHeight = self.parentImage.size[1]
		self.diffMap = self.initDiffMap()

	def initDiffMap(self):
		#diffMap = np.zeros((self.imageHeight, self.imageWidth, 2), dtype=np.float64)
		diffMap = [ [0]*self.imageHeight for _ in range(self.imageWidth) ]
		for i in range(len(self.childImages)):
			childImage = self.childImages[i]
			childImageData = self.childImageData[i]

			#diffMap[childImage.filename] = np.zeros((self.imageHeight, self.imageWidth, 1), dtype=np.float64)

			for row in range(self.imageHeight):
				for col in range(self.imageWidth):
					pixel = self.parentImageData[row][col]
					childPixel = childImageData[row][col]
					if diffMap[row][col] == 0:
						#0 is lastUsedIndex, then list of distances
						diffMap[row][col] = [0, [[self.distance(pixel, childPixel), i]]]
					else:
						#print(diffMap[row][col])
						diffMap[row][col][1].append([self.distance(pixel, childPixel), i])
						#print(diffMap[row][col])

		#sort diffMap
		for row in range(self.imageHeight):
				for col in range(self.imageWidth):
					#print(diffMap[row][col])
					#print(diffMap[row][col][1])
					diffMap[row][col][1].sort()
					#print(diffMap[row][col])
					#print(diffMap[row][col][1])

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

	def compareImage(self, distanceThreshold, outputFileName, distancesArray, eligiblityFunction):
		# finalImage = np.zeros((self.imageWidth, self.imageHeight, 3), dtype=np.uint8)
		finalImage = np.copy(self.parentImage)

		close = 0
		total = 0
		for row in range(self.imageHeight):
			for col in range(self.imageWidth):
				#Now THAT's what I call good code!
				#This definitely only works either for min or max, not sure which. Will need sorting above to be reversed if wrong
				#DiffInfo is (currentlyUsedChildIndex, [[distance, childIndexNum], ...])
				diffInfo = self.diffMap[row][col]
				currentDiffIndex = diffInfo[0]

				#print("current diff index: " + str(currentDiffIndex))
				#print(diffInfo[1])
				#print(diffInfo[1][currentDiffIndex])
				#print(diffInfo[1][currentDiffIndex][0])
				currentDistance = diffInfo[1][currentDiffIndex][0]
				currentChildIndex = diffInfo[1][currentDiffIndex][1]
				
				if currentDistance < distanceThreshold:
					distancesArray[row][col] = diffInfo[1][currentDiffIndex][0]
					# close += 1
					finalImage[row][col] = self.childImageData[currentChildIndex][row][col]


					if diffInfo[0] + 1 < len(self.childImages):
						nextDistance = diffInfo[1][currentDiffIndex + 1][0]

						if nextDistance < distanceThreshold:
							diffInfo[0] += 1
				# total += 1

		# print("max of max: " + str(max(distancesArray.flatten('F').tolist())))
		# print("close: " + str(close) + ", total: " + str(total) + " percent: " + str(float(close)/float(total) * 100))

		Image.fromarray(finalImage, 'RGB').save(outputFileName)

	def maxEligibilityFunction(self, distance, maxDistances, row, col):
		return distance > maxDistances[row][col]

	def maxCompareImage(self, distanceThreshold, outputFileName):
		maxDistances = np.zeros((self.imageHeight, self.imageWidth, 1), dtype=np.float64)

		return self.compareImage(distanceThreshold, outputFileName, maxDistances, self.maxEligibilityFunction)
		
	def minEligibilityFunction(self, distance, minDistances, row, col):
		return distance < minDistances[row][col]

	def minCompareImage(self, distanceThreshold, outputFileName):
		minDistances = np.full((self.imageHeight, self.imageWidth, 1), 9999999, dtype=np.float64)
	
		return self.compareImage(distanceThreshold, outputFileName, minDistances, self.minEligibilityFunction)

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
	
	runner = PixelMatcherRunner(childFolder, parentImagePath)
	runner.makeCompareImages(outputFolder, start, stop, step=step, maxMin=maxMin)

if __name__ == '__main__':
	main(0, 100, "./output/", "./abstract - resized/", "./glitch_girl_small.jpg")