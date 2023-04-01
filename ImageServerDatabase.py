#!/usr/bin/python3
#
##############################################################################################
#
# RuGiVi - Adult Media Landscape Browser
#
# For updates see git-repo at
# https://github.com/pronopython/rugivi
#
##############################################################################################
#
VERSION = "0.1.0-alpha"
#
##############################################################################################
#
# Copyright (C) 2023 PronoPython
#
# Contact me at pronopython@proton.me
#
# This program is free software: you can redistribute it and/or modify it 
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
##############################################################################################
#

import threading
from threading import Lock
from time import sleep,time
import pygame

from sqlitedict import SqliteDict  # needs pip install sqlitedict


class ImageProxy:

	QUALITY_THUMB = 0 	# TODO a hack, ImageServer.py cannot be imported because of circular imports => separate CONST file?


	def __init__(self):
		self.path = ""
		self.thumbSurface = None
		self.averageColor = (255,0,0)
		self.aspectRatio = 1
		self.width = -1
		self.height = -1
		self.bytesPerPixel = 3
		self.thumbWidth = -1
		self.thumbHeight = -1

	def toPickle(self):
		# TODO: Pygame 2.1.3 uses tobyte instead of tostring ... both result in bytes...
		return (pygame.image.tostring(self.thumbSurface,"RGB"), self.averageColor, self.aspectRatio, self.width, self.height, self.bytesPerPixel, self.thumbWidth,self.thumbHeight)


	def fromPickle(self, pickle):

		#print("Recreating Pickle:",pickle[3],pickle[4])

		self.averageColor = pickle[1]
		self.aspectRatio = pickle[2]
		self.width = pickle[3]
		self.height = pickle[4]
		self.bytesPerPixel = pickle[5]
		self.thumbWidth = pickle[6]
		self.thumbHeight = pickle[7]
		# TODO: Pygame 2.1.3 uses frombyte instead of fromstring ... both result in bytes...
		try:
			self.thumbSurface = pygame.image.fromstring(pickle[0],(self.thumbWidth,self.thumbHeight),"RGB")
		except Exception as e:
			return False
		return True

class ImageServerDatabase:

	DB_COMMIT_EVERY_SECONDS = 120

	def __init__(self, thumbDbFile):
		self.dbFilename = thumbDbFile
		self.db = SqliteDict(thumbDbFile)
		self.imageDBsize = 0
		self.running = True
		self.housekeepingLoopRunning = False
		self.run()

	def addImage(self, image):
		imageProxy = ImageProxy()

		imageProxy.path = image.originalFilePath
		imageProxy.thumbSurface = image.getSurface(ImageProxy.QUALITY_THUMB)
		imageProxy.averageColor = image.averageColor
		imageProxy.aspectRatio = image.aspectRatio
		imageProxy.bytesPerPixel = image.bytesPerPixel
		imageProxy.width = image.width
		imageProxy.height = image.height
		imageProxy.thumbWidth, imageProxy.thumbHeight = imageProxy.thumbSurface.get_size()

		if imageProxy.thumbSurface != None:
			if imageProxy.path not in self.db:
				self.db[imageProxy.path] = imageProxy.toPickle()


	def removeImage(self, image):
		pass

	def getImageProxyByPath(self, path):
		'''
		if path in self.db:
			pickle = self.db[path]

			imageProxy = ImageProxy()
			imageProxy.fromPickle(pickle)
			return imageProxy
		else:
			return None
		'''
		#pickle = self.db[path]
		pickle = self.db.get(path)
		if pickle != None:
			imageProxy = ImageProxy()
			success = imageProxy.fromPickle(pickle)
			if success:
				return imageProxy
			else:
				return None
		else:
			return None




	def noOfImages(self):
		pass


	def run(self):
		self.thread = threading.Thread(target=self.housekeepingLoop, args=())
		self.thread.daemon = True # so these threads get killed when program exits
		self.thread.start()


	def housekeepingLoop(self):
		self.housekeepingLoopRunning = True
		while(self.running):
			self.imageDBsize = len(self.db)
			print("Thumb DB Size:",self.imageDBsize)

			sec = 0

			while sec < ImageServerDatabase.DB_COMMIT_EVERY_SECONDS and self.running:
				sleep(1)
				sec += 1

			print("Commiting Thumb Database")
			self.db.commit()
			print("Commit done")

		print("ImageServerDatabase stopped")
		self.housekeepingLoopRunning = False

	def stop(self):
		self.running = False
		while (self.housekeepingLoopRunning):
			sleep(0.06)


	def close(self):
		self.thread.join()
		self.db.close()
