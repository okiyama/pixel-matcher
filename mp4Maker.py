import argparse, time, os, subprocess
from os import listdir


def makeMp4(pngFolder, gifFolder, loopGif=True):
	gifOutputFile = gifFolder + "/animation" + str(int(time.time())) + ".mp4"
	os.path.dirname(os.path.realpath(__file__))
	shellCall = 'ffmpeg -r 24000/1001 -i ' + pngFolder + '/out%05d.png -vcodec libx265 '
	if(loopGif):
		shellCall += '-filter_complex "[0]reverse[r];[0][r]concat,loop=0:250,setpts=N/30/TB" '
	shellCall += gifOutputFile
	print(shellCall)
	subprocess.call(shellCall, shell=True)

def findMissing(pngFolder):
	fileList = [int(f[3:8]) for f in listdir(pngFolder)]
	for i in range(len(fileList)-1):
		if fileList[i+1] - fileList[i] != 1:
			print(i+1)

def splitMp4IntoFrames(mp4Path, outputFolder):
	baseFilename = os.path.basename(mp4Path)
	rawFilename = os.path.splitext(baseFilename)[0]
	outputDirectory = outputFolder + "\\" if outputFolder[-1] != "\\" else outputFolder
	outputDirectory = outputDirectory + rawFilename + "_frames\\"
	if(not os.path.isdir(outputDirectory)):
		os.makedirs(outputDirectory)
		shellCall = "ffmpeg -i " + mp4Path + " " + outputDirectory + "/out%05d.png"
		subprocess.call(shellCall, shell=True)
	else:
		print("Target frame split directory: " + outputDirectory + " already existing, skipping splitting MP4 into frames")

	return outputDirectory

def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("outputFolder", type=str, help="where the pngs are stored")
	parser.add_argument('--find-missing', dest='findMissing', action='store_true', help="whether to find missing output images, will not make an mp4")
	args = parser.parse_args()
	args.outputFolder = os.path.join(args.outputFolder, '')

	if(args.findMissing):
		findMissing(args.outputFolder)
	else:
		makeMp4(args.outputFolder, "./gifs")

if __name__ == '__main__':
	main()