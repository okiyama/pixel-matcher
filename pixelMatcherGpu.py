from PIL import Image
from os import listdir
from os.path import join
import os
import cupy as cp
import sys
import cProfile
import math
import argparse
import time

#TODO either fix min or drop support
class PixelMatcherGpu:
	def __init__(self, childFolder, parentImagePath):
		self.initParentData(parentImagePath)

		self.childImages = [Image.open(join(childFolder, f)).convert("RGB") for f in listdir(childFolder) if os.path.isfile(join(childFolder, f))]
		self.childR, self.childG, self.childB = self.initChildImageData()

	def initParentData(self, parentImagePath):
		self.parentImage = Image.open(parentImagePath)
		self.parentImageData = cp.asarray(self.parentImage)
		self.imageWidth = self.parentImage.size[0]
		self.imageHeight = self.parentImage.size[1]
		self.parentR, self.parentG, self.parentB = self.flattenImageData(self.parentImageData)

	def initChildImageData(self):
		self.rawChildImageData = [cp.asarray(c) for c in self.childImages]
		childDataFlattened = [self.flattenImageData(imageData) for imageData in self.rawChildImageData]
		childR = [imageData[0] for imageData in childDataFlattened]
		childG = [imageData[1] for imageData in childDataFlattened]
		childB = [imageData[2] for imageData in childDataFlattened]
		return (childR, childG, childB)

	def flattenImageData(self, imageData):
		splitUp = cp.split(imageData, [0,1,2], axis=2)
		R = splitUp[1].flatten()
		G = splitUp[2].flatten()
		B = splitUp[3].flatten()
		return (R, G, B)

	def unflattenImageData(self, imageDataR, imageDataG, imageDataB):
		R = imageDataR.reshape((self.imageHeight,self.imageWidth))
		G = imageDataG.reshape((self.imageHeight,self.imageWidth))
		B = imageDataB.reshape((self.imageHeight,self.imageWidth))
		return cp.stack((R, G, B), axis=2)

	def makeCompareImages(self, outputFolder, start, stop, step=1, maxMin="max"):
		self.ensureWidthDivisibleByTwo()

		for i in range(start, stop, step):
			print("starting image " + str(i) + " of " + str(stop) + " (" + str(float(i-start)/float(stop-start)*100) + "%)")
			outputFileName = outputFolder + "/" + "out" + format(int(i/step), '05') + ".png"
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
		inputArgs = "uint16 distanceThreshold, uint8 parentR, uint8 parentG, uint8 parentB, "
		for child in range(0, len(self.childImages)):
			inputArgs += "uint8 childR" + str(child) + ", "
		for child in range(0, len(self.childImages)):
			inputArgs += "uint8 childG" + str(child) + ", "
		for child in range(0, len(self.childImages)):
			inputArgs += "uint8 childB" + str(child)
			if(child != len(self.childImages) - 1):
				inputArgs += ", "

		outputArgs = 'uint8 finalImageR, uint8 finalImageG, uint8 finalImageB'

		kernelFunction = ""
		for child in range(0, len(self.childImages)):
			kernelFunction += """
				int subR{child} = parentR - childR{child};
				int subG{child} = parentG - childG{child};
				int subB{child} = parentB - childB{child};
				if(subR{child} < 0) subR{child} = subR{child} + 256;
				if(subG{child} < 0) subG{child} = subG{child} + 256;
				if(subB{child} < 0) subB{child} = subB{child} + 256;
				unsigned long distanceR{child} = subR{child} * subR{child};
				unsigned long distanceG{child} = subG{child} * subG{child};
				unsigned long distanceB{child} = subB{child} * subB{child};
				unsigned long preSqrtDist{child} = distanceR{child} + distanceG{child} + distanceB{child};
				float distance{child} = sqrtf(preSqrtDist{child});\n
			""".format(child=child)
			#kernelFunction += "float distance{child} = sqrtf(((parentR - childR{child}) * (parentR - childR{child})) + ((parentG - childG{child}) * (parentG - childG{child})) + ((parentB - childB{child}) * (parentB - childB{child})));\n".format(child=child)
		kernelFunction += "float maxDistance = 0.0;\n"
		kernelFunction += "bool useParent = true;\n"

		for child in range(0, len(self.childImages)):
			kernelFunction += """
				if(distance{child} < distanceThreshold && distance{child} > maxDistance) {{
					maxDistance = distance{child};
					finalImageR = childR{child}; 
					finalImageG = childG{child};
					finalImageB = childB{child};
					useParent = false;
				}}\n
			""".format(child=child)

		kernelFunction += """
			if(useParent == true) {{
				finalImageR = parentR; 
				finalImageG = parentG;
				finalImageB = parentB;
			}}\n
		"""

		pixel_matcher = cp.ElementwiseKernel(
			inputArgs,
			outputArgs,
			kernelFunction,
			'pixel_matcher')

		finalImageR, finalImageG, finalImageB = pixel_matcher(distanceThreshold, self.parentR, self.parentG, self.parentB, *self.childR, *self.childG, *self.childB)
		Image.fromarray(cp.asnumpy(self.unflattenImageData(finalImageR, finalImageG, finalImageB)), 'RGB').save(outputFileName)


	def maxCompareImage(self, distanceThreshold, outputFileName):
		return self.compareImage(distanceThreshold, outputFileName)
		
	def minCompareImage(self, distanceThreshold, outputFileName):
		print("MIN NOT WORKING")
		exit()
		return self.compareImage(distanceThreshold, outputFileName)

	def distance(self, t1, t2):
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
	runner = PixelMatcherGpu(childFolder, parentImagePath)
	runner.makeCompareImages(outputFolder, start, stop, step=step, maxMin=maxMin)
	later = time.time()
	print("Took this child " + str(later - now) + " seconds to do " + str(stop - start) + " from " + str(start) + " to " + str(stop))

if __name__ == '__main__':
	#main(0, 441, "./output/", "./r_test/", "./100_r.png")
	main(0, 441, "./output/", "./abstract/", "./glitch_girl_small.jpg")