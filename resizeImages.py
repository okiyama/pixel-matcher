import argparse
import subprocess
from PIL import Image
import os
from os import listdir
from os.path import join

def resizeImages(parentImagePath, childFolder, imageWidth=None, imageHeight=None):
	if(imageWidth is not None and imageHeight is not None):
		dimensions = str(imageWidth) + "x" + str(imageHeight)
	else:
		dimensions = getImageDimensions(parentImagePath)
	dirBefore = os.path.dirname(os.path.realpath(__file__))
	
	childFiles = [f for f in listdir(childFolder) if os.path.isfile(join(childFolder, f))]
	os.chdir(childFolder)
	for childFile in childFiles:
		shellCall = "convert " + childFile + " -resize " + dimensions + "! " + childFile
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