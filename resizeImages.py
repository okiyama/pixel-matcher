import argparse
import subprocess
from PIL import Image
import os
from os import listdir
from os.path import join
import shutil

def resizeImages(parentImagePath, childFolder):
	if(os.path.isdir(parentImagePath)):
		parentImagePath = parentImagePath + "/" + listdir(parentImagePath)[0]
	dimensions = getImageDimensions(parentImagePath)
	dirBefore = os.path.dirname(os.path.realpath(__file__))

	childFolder = childFolder[0:-1] if childFolder[-1] == "\\" else childFolder
	targetChildDir = childFolder + "_" + dimensions
	if(not os.path.isdir(targetChildDir)):
		shutil.copytree(childFolder, targetChildDir)
		os.chdir(targetChildDir)

		for childFile in listdir("."):
			if os.path.isfile(childFile):
				shellCall = "convert " + childFile + " -resize " + dimensions + "! " + childFile
				subprocess.call(shellCall, shell=True)
	else:
		print("Target child folder: " + targetChildDir + " already exists, skipping resize.")

	os.chdir(dirBefore)
	return targetChildDir


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