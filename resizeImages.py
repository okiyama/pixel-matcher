import argparse
import subprocess
from PIL import Image
import os
from os import listdir
from os.path import join

def resizeImages(parentImagePath, childFolder):
	dimensions = getImageDimensions(parentImagePath)
	dirBefore = os.path.dirname(os.path.realpath(__file__))
	
	childFiles = [f for f in listdir(childFolder) if os.path.isfile(join(childFolder, f))]
	os.chdir(childFolder)
	for childFile in childFiles:
		#dear future self: welcome back! You can thank me later. So I think you wrote these directories to work for Linux
		#and I tried running in Cygwin and Git Bash but it barfed. Anyways, these are windows paths now.
		#You may have to switch them back to Linux, maybe check git history?
		#Also, it is 2020. Trump refuses to concede and is attempting a coup. I hope things are better on the other side of this pandemic.
		#At times, it feels there will be no other side.
		#I certainly won't view America the same way ever again.
		shellCall = "convert \".\\" + childFile + "\" -resize " + dimensions + "! \".\\" + childFile + "\""
		#print(shellCall)
		#print(os.getcwd())
		subprocess.call(shellCall, shell=True)

	os.chdir(dirBefore)


def getImageDimensions(imagePath):
	image = Image.open(imagePath)
	return str(image.size[0]) + "x" + str(image.size[1])


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("parentImage", type=str, help="parent image to get size of")
	parser.add_argument('childFolder', type=str, help="child folder to resize")
	args = parser.parse_args()
	args.childFolder = os.path.join(args.childFolder, '')

	resizeImages(args.parentImage, args.childFolder)

if __name__ == '__main__':
	main()