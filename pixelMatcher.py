import argparse
import pixelMatcherRunner
import multiprocessing as mp
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
	parser.add_argument("parentImagePath", type=str, help="path to the parent image file")
	parser.add_argument("-maxMin", type=str, nargs="?", default="max", help="either maximizing or minimizing differences (max/min)")
	parser.add_argument("-step", type=int, nargs="?", default=1, help="how much to step each frame by, can speed up the gif")
	parser.add_argument('--limit-cpu-usage', dest='limitCpuUsage', action='store_true', help="flag to use less CPU. Making the computer more usable while the program runs")

	args = parser.parse_args()
	args.outputFolder = os.path.join(args.outputFolder, '')
	args.childFolder = os.path.join(args.childFolder, '')
		
	# print(args)
	clearOutputFolder(args.outputFolder)

	print("resizing child images to match parent image")
	resizeImages.resizeImages(args.parentImagePath, args.childFolder)

	numCpus = mp.cpu_count()
	if args.limitCpuUsage and numCpus > 1:
		numCpus -= 1

	segmentSize = args.stop/numCpus
	subArgs = [(int((x*segmentSize)+1), int((x+1)*segmentSize)+1, args.outputFolder, args.childFolder, args.parentImagePath, args.maxMin, args.step) for x in range(numCpus)]
	processes = [mp.Process(target=pixelMatcherRunner.main, args=(subArgs[x])) for x in range(numCpus)]

	print("starting child processes")
	for p in processes:
		p.start()

	for p in processes:
		p.join()

	print("making MP4")
	#TODO make arg for gif output folder
	makeMp4(args.outputFolder, "./gifs")

if __name__ == '__main__':
	main()