from PIL import Image
from os import listdir
from os.path import join
import os
import numpy as np
import sys
import cProfile
import math
import argparse
import shutil
import mp4Maker


class CorrupterRunner:
	def __init__(self, parentImagePath):
		self.parentImage = Image.open(parentImagePath)
		self.parentImageData = np.asarray(self.parentImage)

		self.imageWidth = self.parentImage.size[0]
		self.imageHeight = self.parentImage.size[1]
		self.goalMap = self.initGoalMap()

	def initGoalMap(self):
		return np.random.randint(255, size=(self.imageHeight, self.imageWidth, 3))

	def makeCompareImages(self, outputFolder, start, stop, step=1, maxMin="max"):
		self.ensureWidthDivisibleByTwo()

		for i in range(start, stop, step):
			print("starting image " + str(i) + " of " + str(stop) + " (" + str(float(i-start)/float(stop-start)*100) + "%)")
			outputFileName = outputFolder + "/" + "out" + format(i, '05') + ".png"

			finalImage = np.copy(self.parentImage)

			for row in range(self.imageHeight):
				for col in range(self.imageWidth):
					goalPixel = self.goalMap[row][col]
					finalImage[row][col] = self.corruptPixel(self.parentImageData[row][col], goalPixel, i, stop)

			Image.fromarray(finalImage, 'RGB').save(outputFileName)

	#TODO the hard part. Figure out this math. I think I need to pass in step and stop
	def corruptPixel(self, pixelArray, goalPixel, corruptionAmount, stop):
		r = (pixelArray[0] + ((float(goalPixel[0]) / float(stop)) * corruptionAmount)) % 255
		g = (pixelArray[1] + ((float(goalPixel[1]) / float(stop)) * corruptionAmount)) % 255
		b = (pixelArray[2] + ((float(goalPixel[2]) / float(stop)) * corruptionAmount)) % 255
		return [r, g, b]


	# We can only make an MP4 if they width of the images is divisible by 2
	#TODO this should move to MP4Maker
	def ensureWidthDivisibleByTwo(self):
		if self.parentImage.width % 2 != 0:
			print("Width of images must be divisible by 2 to make an mp4")
			sys.exit()


def clearOutputFolder(outputFolder):
	if(os.path.isdir(outputFolder)):
		shutil.rmtree(outputFolder)
	os.makedirs(outputFolder)

def makeMp4(pngFolder, gifFolder):
	return mp4Maker.makeMp4(pngFolder, gifFolder)

#Note: 441.673 is the max distance between two pixels
def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("start", type=int, help="start value for max allowed distance")
	parser.add_argument("stop", type=int, help="stop value for max allowed distance")
	parser.add_argument("outputFolder", type=str, help="where to store temporary output files")
	parser.add_argument("parentImagePath", type=str, help="path to the parent image file")
	parser.add_argument("-step", type=int, nargs="?", default=1, help="how much to step each frame by, can speed up the gif")
	parser.add_argument('--limit-cpu-usage', dest='limitCpuUsage', action='store_true', help="flag to use less CPU. Making the computer more usable while the program runs")

	args = parser.parse_args()
	args.outputFolder = os.path.join(args.outputFolder, '')
		
	# print(args)
	clearOutputFolder(args.outputFolder)
	# print("start" + str(start) + str(type(start)))
	# print("stop" + str(stop) + str(type(stop)))
	# print("outputFolder" + str(outputFolder) + str(type(outputFolder)))
	# print("childFolder" + str(childFolder) + str(type(childFolder)))
	# print("parentImagePath" + str(parentImagePath) + str(type(parentImagePath)))
	# print("maxMin" + str(maxMin) + str(type(maxMin)))
	# print("step" + str(step) + str(type(step)))
	
	runner = CorrupterRunner(args.parentImagePath)
	runner.makeCompareImages(args.outputFolder, args.start, args.stop, step = args.step)


	print("making MP4")
	#TODO make arg for gif output folder
	makeMp4(args.outputFolder, "./gifs")

if __name__ == '__main__':
	main()