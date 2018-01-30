import argparse, time, os, subprocess
from os import listdir


def makeMp4(pngFolder, gifFolder):
		gifOutputFile = gifFolder + "/animation" + str(int(time.time())) + ".mp4"
		os.path.dirname(os.path.realpath(__file__))
		shellCall = 'ffmpeg -r 30 -f image2 -s 1920x1080 -i ' + pngFolder + 'out%05d.png -vcodec libx264 -crf 25 ' + \
			'-pix_fmt yuv420p -filter_complex "[0]reverse[r];[0][r]concat,loop=0:250,setpts=N/30/TB" ' + gifOutputFile
		subprocess.call(shellCall, shell=True)

def findMissing(pngFolder):
	fileList = [int(f[3:8]) for f in listdir(pngFolder)]
	for i in range(len(fileList)-1):
		if fileList[i+1] - fileList[i] != 1:
			print(i+1)

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