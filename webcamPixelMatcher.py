import numpy as np
import cv2
import os
import argparse
import resizeImages
from pixelMatcherRunner import PixelMatcherRunner

class WebcamPixelMatcher:
	def __init__(self, childFolder, distanceThreshold, stopKey='q'):
		self.childFolder = childFolder
		self.stopKey = stopKey
		self.distanceThreshold = distanceThreshold
		self.cap = cv2.VideoCapture(0)

		self.webcamWidth = int(self.cap.get(3))
		self.webcamHeight = int(self.cap.get(4))

		print("resizing child images to match parent image")
		resizeImages.resizeImages(None, childFolder, self.webcamWidth, self.webcamHeight)

	def showCorruptedWebcam(self):
		while(True):
		    # Capture frame-by-frame
		    ret, frame = self.cap.read()

		    pixelMatcher = PixelMatcherRunner(self.childFolder, None, frame, self.webcamWidth, self.webcamHeight)

		    # Display the resulting frame
		    cv2.imshow('frame',pixelMatcher.maxCompareImage(self.distanceThreshold))
		    if cv2.waitKey(1) & 0xFF == ord(self.stopKey):
		        break

		# When everything done, release the capture
		cap.release()
		cv2.destroyAllWindows()



def main():
	parser = argparse.ArgumentParser()
	parser.add_argument("childFolder", type=str, help="what files to iterate through")
	parser.add_argument("distanceThreshold", type=int, help="how much to corrupt the file, max value 441")
	parser.add_argument("-stopKey", type=str, nargs="?", default="q", help="what key to press to close the window")

	args = parser.parse_args()
	args.childFolder = os.path.join(args.childFolder, '')

	webcamPixelMatcher = WebcamPixelMatcher(args.childFolder, args.distanceThreshold, args.stopKey)
	webcamPixelMatcher.showCorruptedWebcam()

if __name__ == '__main__':
	main()
