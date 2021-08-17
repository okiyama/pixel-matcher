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
import time
from moviepy.editor import VideoFileClip

def createOutputFolder(outputFolder):
	if(not os.path.isdir(outputFolder)):
		os.makedirs(outputFolder)
	actualOutputFolder = outputFolder + "/" + time.strftime("%Y-%m-%d_%H-%M-%S", time.localtime())
	os.makedirs(actualOutputFolder)
	return actualOutputFolder

def makeMp4(pngFolder, gifFolder):
	return mp4Maker.makeMp4(pngFolder, gifFolder)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("start", type=int, help="start value for max allowed distance")
	parser.add_argument("stop", type=int, help="stop value for max allowed distance")
	parser.add_argument("outputFolder", type=str, help="where to store temporary output files")
	parser.add_argument("childFolder", type=str, help="what files to iterate through")
	parser.add_argument("parentImagePath", type=str, help="path to the parent image file, if a folder then each image in the folder will be used for one frame, if an .mp4 it will be split into frames then that folder will be used")
	parser.add_argument("-maxMin", type=str, nargs="?", default="max", help="either maximizing or minimizing differences (max/min)")
	parser.add_argument("-step", type=int, nargs="?", default=1, help="how much to step each frame by, can speed up the gif")
	parser.add_argument('--limit-cpu-usage', dest='limitCpuUsage', action='store_true', help="flag to use less CPU. Making the computer more usable while the program runs")
	parser.add_argument('--volume-intensity', dest='volumeIntensity', action='store_true', help="flag to have the corruption be proportional to the volume of the frame")

	args = parser.parse_args()
	args.outputFolder = os.path.join(args.outputFolder, '')
	args.childFolder = os.path.join(args.childFolder, '')

	isMp4 = os.path.isfile(args.parentImagePath) and args.parentImagePath.lower().endswith(".mp4")
	if(args.volumeIntensity and not isMp4):
		print("Must pass MP4 as parent when using volume intensity flag")
		exit()
		
	# print(args)
	outputFolder = createOutputFolder(args.outputFolder)

	numCpus = mp.cpu_count()
	if args.limitCpuUsage and numCpus > 1:
		numCpus -= 1


	processes = []
	if(isMp4):
		print("Provided MP4 as parent, splitting into frames then using that parent as directory")
		parentImageDir = mp4Maker.splitMp4IntoFrames(args.parentImagePath, args.outputFolder)
	else:
		parentImageDir = os.path.join(args.parentImagePath, '')

	print("resizing child images to match parent image")
	childFolder = resizeImages.resizeImages(str(parentImageDir), args.childFolder)


	if(os.path.isdir(parentImageDir)):
		print("Parent was folder: " + str(parentImageDir))
		parentImagePaths = []
		for f in os.listdir(parentImageDir):
			thisParentImagePath = os.path.join(parentImageDir, f)
			if os.path.isfile(thisParentImagePath):
				parentImagePaths.append(thisParentImagePath)

		if args.volumeIntensity:
			print("Making corruption proportional to volume")
			clip = VideoFileClip(args.parentImagePath)
			frameTimings = np.linspace(0, clip.audio.duration, clip.reader.nframes)

			#source: https://stackoverflow.com/questions/28119082/how-can-i-get-the-volume-of-sound-of-a-video-in-python-using-moviepy
			cut = lambda i: clip.audio.subclip(frameTimings[i],frameTimings[i+1]).to_soundarray()
			volume = lambda array: np.sqrt(((1.0*array)**2).mean())
			volumes = [volume(cut(i)) for i in range(len(frameTimings) - 1)]
			maxval = np.max(volumes)
			minval = np.min(volumes)
			segments = np.array([((args.stop - args.start) * ((x - minval) / (maxval - minval))) + args.start for x in volumes])
		else:
			segments = np.linspace(args.start, args.stop, len(parentImagePaths))
		subArgs = []
		for x in range(len(parentImagePaths)):
			subArgs.append(([segments[x]], outputFolder, childFolder, parentImagePaths[x], args.maxMin, x))
		processes = [mp.Process(target=pixelMatcherGpu.main, args=(subArgs[x])) for x in range(len(parentImagePaths))]
	else:
		segments = np.array_split(range(args.start, args.stop, args.step), numCpus)
		subArgs = [(segments[x], outputFolder, childFolder, args.parentImagePath, args.maxMin, segments[x][0]) for x in range(numCpus)]
		processes = [mp.Process(target=pixelMatcherGpu.main, args=(subArgs[x])) for x in range(len(segments))]
	
	print("starting child processes")
	now = time.time()
	numLaunched = 0
	#TODO output num launched as percent each batch
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
	makeMp4(outputFolder, "./gifs")

if __name__ == '__main__':
	main()