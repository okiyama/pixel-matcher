import argparse
import pixelMatcherRunner
import multiprocessing as mp
import shutil
import os
import time
import subprocess

"""
	customDiffThreshold = None
	if len(sys.argv) > 1:
		customDiffThreshold = int(sys.argv[1])

	# parentFolder = "./parents/"
	childFolder = "./abstract/"
	outputFolder = "./output/"
	parentImagePath = "./parents/tumblr_static_bx9tc24cjhko88owskcowgco8_640_v2.jpg"
	matcher = PixelMatcher(childFolder, parentImagePath, customDiffThreshold=customDiffThreshold)

	# matcher.minCompareImage(1000, outputFolder + "outTest.png")
	matcher.makeCompareGif(outputFolder, loops=400, maxMin="min")
	# matcher.maxCompareImage(100, "")
	"""

def clearOutputFolder(outputFolder):
	text = input("Clear contents of folder " + outputFolder + " ? ")
	if(text.lower() == "y"):
		shutil.rmtree(outputFolder)
		os.makedirs(outputFolder)
	else:
		sys.exit()

def makeMp4(pngFolder, gifFolder):
	gifOutputFile = gifFolder + "/animation" + str(int(time.time())) + ".mp4"
	os.path.dirname(os.path.realpath(__file__))
	shellCall = 'ffmpeg -r 30 -f image2 -s 1920x1080 -i ' + pngFolder + 'out%05d.png -vcodec libx264 -crf 25 ' + \
		'-pix_fmt yuv420p -filter_complex "[0]reverse[r];[0][r]concat,loop=0:250,setpts=N/30/TB" ' + gifOutputFile
	subprocess.call(shellCall, shell=True)

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("start", type=int)
	parser.add_argument("stop", type=int)
	parser.add_argument("outputFolder", type=str)
	parser.add_argument("childFolder", type=str)
	parser.add_argument("parentImagePath", type=str)
	parser.add_argument("maxMin", type=str, nargs="?", default="max")
	parser.add_argument("step", type=int, nargs="?", default=1)

	args = parser.parse_args()
	# print(args)
	clearOutputFolder(args.outputFolder)

	numCpus = mp.cpu_count()
	stop = args.stop
	#TODO: This seems like it'll fail for values not evenly divisible. Should see if there's a helper for this in multiprocessing
	subArgs = [(int(x*(stop/numCpus)), int((x*(stop/numCpus)-1) + stop/numCpus), args.outputFolder, args.childFolder, args.parentImagePath, args.maxMin, args.step) for x in range(numCpus)]
	processes = [mp.Process(target=pixelMatcherRunner.main, args=(subArgs[x])) for x in range(numCpus)]

	for p in processes:
		p.start()

	for p in processes:
		p.join()

	print("all done")

	#TODO make arg
	makeMp4(args.outputFolder, "./gifs")

if __name__ == '__main__':
	main()