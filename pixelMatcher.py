import argparse
import pixelMatcherRunner
import pixelMatcherGpu
import multiprocessing as mp
import numpy as np
import shutil
import os
import time
import sys
import mp4Maker
import resizeImages

def clearOutputFolder(outputFolder):
	if(os.path.isdir(outputFolder)):
		shutil.rmtree(outputFolder)
	os.makedirs(outputFolder)

def makeMp4(pngFolder, gifFolder):
	return mp4Maker.makeMp4(pngFolder, gifFolder)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("start", type=int, help="start value for max allowed distance")
	parser.add_argument("stop", type=int, help="stop value for max allowed distance")
	parser.add_argument("outputFolder", type=str, help="where to store temporary output files")
	parser.add_argument("childFolder", type=str, help="what files to iterate through")
	parser.add_argument("parentImagePath", type=str, help="path to the parent image file, if a folder then each image in the folder will be used for one frame")
	parser.add_argument("-maxMin", type=str, nargs="?", default="max", help="either maximizing or minimizing differences (max/min)")
	parser.add_argument("-step", type=int, nargs="?", default=1, help="how much to step each frame by, can speed up the gif")
	parser.add_argument('--limit-cpu-usage', dest='limitCpuUsage', action='store_true', help="flag to use less CPU. Making the computer more usable while the program runs")

	args = parser.parse_args()
	args.outputFolder = os.path.join(args.outputFolder, '')
	args.childFolder = os.path.join(args.childFolder, '')
		
	# print(args)
	clearOutputFolder(args.outputFolder)

	numCpus = mp.cpu_count()
	if args.limitCpuUsage and numCpus > 1:
		numCpus -= 1

	processes = []
	parentImageDir = os.path.join(args.parentImagePath, '')
	if(os.path.isdir(parentImageDir)):
		print("Parent was folder")
		parentImagePaths = []
		for f in os.listdir(parentImageDir):
			thisParentImagePath = os.path.join(args.parentImagePath, f)
			if os.path.isfile(thisParentImagePath):
				parentImagePaths.append(thisParentImagePath)
		segments = np.array_split(range(args.start, args.stop, args.step), len(parentImagePaths))
		subArgs = [(segments[x][0], segments[x][-1]+args.step, args.outputFolder, args.childFolder, parentImagePaths[x], args.maxMin, args.step) for x in range(len(parentImagePaths))]
		processes = [mp.Process(target=pixelMatcherGpu.main, args=(subArgs[x])) for x in range(len(parentImagePaths))]
	else:
		print("resizing child images to match parent image")
		resizeImages.resizeImages(args.parentImagePath, args.childFolder)

		segments = np.array_split(range(args.start, args.stop, args.step), numCpus)
		subArgs = [(segments[x][0], segments[x][-1]+args.step, args.outputFolder, args.childFolder, args.parentImagePath, args.maxMin, args.step) for x in range(numCpus)]
		processes = [mp.Process(target=pixelMatcherGpu.main, args=(subArgs[x])) for x in range(numCpus)]
	
	print("starting child processes")
	now = time.time()
	numLaunched = 0
	while numLaunched < len(processes):
		for i in range(numCpus):
			if(numLaunched + i < len(processes)):
				processes[numLaunched + i].start()

		for i in range(numCpus):
			if(numLaunched + i < len(processes)):
				processes[numLaunched + i].join()

		numLaunched += numCpus

	later = time.time()
	print("Took this many seconds: " + str(later - now))

	print("making MP4")
	#TODO make arg for gif output folder
	makeMp4(args.outputFolder, "./gifs")

if __name__ == '__main__':
	main()