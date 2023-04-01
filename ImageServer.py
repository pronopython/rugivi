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

import pygame
from pygame.locals import *
import threading
from time import sleep,time
from queue import Queue
from ThreadSafeList import *
from World import *
from ImageServerDatabase import *


class StreamedImage:
	STATE_NEW = "new"
	STATE_LOADED = "data loaded"
	STATE_RESCALE = "rescale"
	STATE_READY = "surface ready"
	STATE_READY_AND_RELOADING = "surface ready and reloading"
	STATE_ERROR_ON_LOAD = "error on load"


	QUALITY_NONE = -2
	QUALITY_COLOR = -1
	QUALITY_THUMB = 0		# really small
	QUALITY_GRID = 1 # bigger as a thumb, grid size *2 ?
	QUALITY_SCREEN = 2 # max screen fit
	QUALITY_ORIGINAL = 3

	SURFACE_AGE = 0
	SURFACE_ACCESSED = 1
	SURFACE_BYTES = 2
	SURFACE_SURFACE = 3


	def __init__(self):
		self._surface = None
		self._scaledSurface = None
		self.originalFilePath = None
		self.state = StreamedImage.STATE_NEW
		#self.pilImageBytes = None
		self.width = 0
		self.height = 0
		self.mode = None
		self.averageColor = (255,0,0)
		self.aspectRatio = 1.0 # width * aspectRatio = height
		self.bytesPerPixel = 3

		# age, bytes, surface
		self._surfaces = [ [0, 0, 0, None], [0, 0, 0, None], [0, 0, 0, None], [0, 0, 0, None]]
		self._availableQuality = StreamedImage.QUALITY_NONE
		self._loadQuality = StreamedImage.QUALITY_NONE
		self._orderedQuality = StreamedImage.QUALITY_NONE

		self.drawnworldx = -1
		self.drawnworldy = -1
		self.drawnheight = -1
		self.drawntoken = -1

	def setOriginalFilePath(self,path):
		self.originalFilePath = path


	def getAvailableQuality(self):
		return self._availableQuality

	def getOrderedQuality(self):
		return self._orderedQuality

	def setOrderedQuality(self, quality):
		self._orderedQuality = quality

	def getStatus(self):
		return self.state + "@" + self.originalFilePath

	def setNotNeededAnymore(self):
		# TODO
		pass

	def getSurface(self, quality = None):
		if quality == None:
			quality = self._availableQuality
		self._surfaces[quality][StreamedImage.SURFACE_ACCESSED] += 1
		self._surfaces[quality][StreamedImage.SURFACE_AGE] = 0
		# TODO here LOCK !!! with unload!!!
		return self._surfaces[quality][StreamedImage.SURFACE_SURFACE]


	def _calculateBytesOfSurface(self,surface):
		if surface != None:
			w,h = surface.get_size()
			b = surface.get_bytesize()
			return w*h*b
		else:
			return 0

	def getMemoryUsage(self):
		return self._surfaces[0][StreamedImage.SURFACE_BYTES] + self._surfaces[1][StreamedImage.SURFACE_BYTES] + self._surfaces[2][StreamedImage.SURFACE_BYTES] + self._surfaces[3][StreamedImage.SURFACE_BYTES]


	def incrementAge(self):
		self._surfaces[0][StreamedImage.SURFACE_AGE] += 1
		self._surfaces[1][StreamedImage.SURFACE_AGE] += 1
		self._surfaces[2][StreamedImage.SURFACE_AGE] += 1
		self._surfaces[3][StreamedImage.SURFACE_AGE] += 1


	def unloadUnused(self):
		if self.getAvailableQuality() >= StreamedImage.QUALITY_GRID:
			self._availableQuality = StreamedImage.QUALITY_THUMB
			#self._availableQuality = StreamedImage.QUALITY_GRID
			self._surfaces[1][StreamedImage.SURFACE_SURFACE] = None
			self._surfaces[2][StreamedImage.SURFACE_SURFACE] = None
			self._surfaces[3][StreamedImage.SURFACE_SURFACE] = None

			self._surfaces[1][StreamedImage.SURFACE_BYTES] = 0
			self._surfaces[2][StreamedImage.SURFACE_BYTES] = 0
			self._surfaces[3][StreamedImage.SURFACE_BYTES] = 0


			self._surfaces[1][StreamedImage.SURFACE_AGE] = 0
			self._surfaces[2][StreamedImage.SURFACE_AGE] = 0
			self._surfaces[3][StreamedImage.SURFACE_AGE] = 0






class ImageServerConduit:
	def __init__(self,name,imageServer):
		self.name = name
		self.thread = None
		self.job = None
		self.waiting = True
		self.imageServer = imageServer
		self.imageServerDatabase = None


	def load_img(self):
		while (True):
			sleep(0.00001)
			#sleep(0.01)


			#if self.job == None:
			#	print("[C-",self.name,"] isBusy:",self.isBusy())
			#else:
			#	print("[C-",self.name,"] isBusy:",self.isBusy(),self.job.getStatus())



			# TODO RACING!!!
			if not self.waiting and self.job != None:
				#if self.job.state == StreamedImage.STATE_NEW:
				#	# TODO error handling while loading
				#	# TODO what does the display do? sad smily??)
				#	im = Image.open(self.job.originalFilePath)
				#	#print("Converting to bytes:",im)
				#	self.job.width = im.width
				#	self.job.height = im.height
				#	self.job.mode = im.mode
				#	#im1 = im.tobytes("xbm", "rgb")
				#	im1 = im.tobytes()
				#	self.job.pilImageBytes = im1
				#	self.waiting = True
				#	self.job.state = StreamedImage.STATE_LOADED


				if self.job.state == StreamedImage.STATE_NEW or self.job.state == StreamedImage.STATE_READY_AND_RELOADING:


					# only when thumb not already available (on reload job) AND ordered == thumb and not higher!!!
					if self.job.getAvailableQuality() < StreamedImage.QUALITY_THUMB and self.job.getOrderedQuality() <= StreamedImage.QUALITY_THUMB:

						if (self.imageServerDatabase != None):
							imageProxy = self.imageServerDatabase.getImageProxyByPath(self.job.originalFilePath)
							if imageProxy != None:
							

								self.job.width = imageProxy.width
								self.job.height = imageProxy.height
								self.job.aspectRatio = imageProxy.aspectRatio
								self.job.bytesPerPixel = imageProxy.bytesPerPixel
								self.job._surfaces[StreamedImage.QUALITY_THUMB][StreamedImage.SURFACE_SURFACE] = imageProxy.thumbSurface
								self.job._surfaces[StreamedImage.QUALITY_THUMB][StreamedImage.SURFACE_BYTES] = imageProxy.thumbWidth * imageProxy.thumbHeight * self.job.bytesPerPixel

								self.job.averageColor = imageProxy.averageColor

								self.imageServer._totalDBLoaded += 1
								self.waiting = True
								self.job.drawnheight = -1
								self.job._availableQuality = StreamedImage.QUALITY_THUMB
								self.job.state = StreamedImage.STATE_READY
								#print("Fetched from DB")


				if not self.waiting and (self.job.state == StreamedImage.STATE_NEW or self.job.state == StreamedImage.STATE_READY_AND_RELOADING):
					# load image from disk
					#original = pygame.image.load("happycat.jpg").convert()

					try:
						original = pygame.image.load(self.job.originalFilePath).convert()
						#original = pygame.image.load(self.job.originalFilePath)
						self.job.state = StreamedImage.STATE_LOADED
						#print("load image (disk access)",original.get_size())
						self.imageServer._totalDiskLoaded += 1
					except pygame.error as message:
						print("Conduit "+str(self.name)+" cannot load ", self.job.originalFilePath)
						self.job.state = StreamedImage.STATE_ERROR_ON_LOAD
						self.waiting = True
					except FileNotFoundError as e:
						print("Conduit "+str(self.name)+" cannot load ", self.job.originalFilePath)
						self.job.state = StreamedImage.STATE_ERROR_ON_LOAD
						self.waiting = True

				if not self.waiting and self.job.state == StreamedImage.STATE_LOADED:
					# gather info
					self.job.width, self.job.height = original.get_size()
					self.job.aspectRatio = self.job.height / self.job.width
					self.job.bytesPerPixel = original.get_bytesize()


					#print("load quality:",self.job._loadQuality)
					# QUALITY_COLOR
					self.job.averageColor = pygame.transform.average_color(original)


					# TODO change load + available quality based on size of image (e.g. image smaller than ordered "screen" size => keep original


					# QUALITY_THUMB ... QUALITY_SCREEN
					if self.job._loadQuality >= StreamedImage.QUALITY_THUMB:
						qmax = self.job._loadQuality
						if qmax > StreamedImage.QUALITY_SCREEN:
							qmax = StreamedImage.QUALITY_SCREEN
						for q in range(0, qmax + 1):
							w = self.imageServer.qualityPixelSizes[q]
							h = int(w * self.job.aspectRatio)
							self.job._surfaces[q][StreamedImage.SURFACE_SURFACE] = pygame.transform.scale(original, (w,h))
							self.job._surfaces[q][StreamedImage.SURFACE_BYTES] = w * h * self.job.bytesPerPixel

					# QUALITY_ORIGINAL
					if self.job._loadQuality == StreamedImage.QUALITY_ORIGINAL:
							self.job._surfaces[StreamedImage.QUALITY_ORIGINAL][StreamedImage.SURFACE_SURFACE] = original
							self.job._surfaces[StreamedImage.QUALITY_ORIGINAL][StreamedImage.SURFACE_BYTES] = self.job.width * self.job.height * self.job.bytesPerPixel
					original = None

					self.job._availableQuality = self.job._loadQuality



					if (self.imageServerDatabase != None):
						imageProxy = self.imageServerDatabase.getImageProxyByPath(self.job.originalFilePath)
						if imageProxy == None and self.job.getAvailableQuality() >= StreamedImage.QUALITY_THUMB:
							self.imageServerDatabase.addImage(self.job)



					#DEFAULT_IMAGE_SIZE = (200, 200)
					#self.job.surface = pygame.transform.scale(self.job.surface, DEFAULT_IMAGE_SIZE)
					#if self.job.scaledSize != None:
					#	self.job.state = StreamedImage.STATE_RESCALE
					#else:
					self.waiting = True
					self.job.drawnheight = -1
					self.job.state = StreamedImage.STATE_READY


				if self.job.state == StreamedImage.STATE_RESCALE:
					#self.job.setScaledSurface(pygame.transform.scale(self.job._surface, self.job.scaledSize))
					self.waiting = True
					self.job.state = StreamedImage.STATE_READY


	def run(self):
		self.thread = threading.Thread(target=self.load_img, args=())
		self.thread.daemon = True # so these threads get killed when program exits
		self.thread.start()


	def isBusy(self):
		return self.job != None

	def setJob(self,job):
		self.job = job
		self.waiting = False


	def isRunning(self):
		return self.thread.is_alive()


	def close(self):
		if not self.isRunning():
			print("Close",self.name)
			self.thread.join()


class ImageServer:

	HOUSEKEEPING_EVERY_SECONDS = 300
	MEMCHECK_EVERY_SECONDS = 120
	HOUSEKEEPING_THRESHOLD = [-1,5000,150,20]
	HOUSEKEEPING_MAX_MEM_MB_THRESHOLD = 2000 # TODO not implemented!
	QUALITY_PIXEL_SIZE = [32,128,1000] # thumb, grid, screen


	def __init__(self, noOfConduits, thumbDbFile):
		self.conduits = []
		for c in range(0,noOfConduits):
			self.conduits.append(ImageServerConduit(c, self))
		self.threadLoader = None
		self.threadViewFetcher = None
		self.jobQueue = Queue()
		self.surfaceQueue = Queue()
		self.streamedImages = ThreadSafeList()
		self.qualityPixelSizes = ImageServer.QUALITY_PIXEL_SIZE # thumb, grid, screen
		self._bytesUsedTotal = 0

		self._bytesUsedSizes = [0,0,0,0]
		self._surfacesPresent = [0,0,0,0]
		self._statusLine = "---"
		self._totalDiskLoaded = 0
		self._totalDBLoaded = 0

		self.running = True
		self.loaderLoopRunning = False
		self.fetcherLoopRunning = False
		
		self.views = []
		self.fapTableViews = []

		self.paused = False

		self.imageServerDatabase = ImageServerDatabase(thumbDbFile)
		for conduit in self.conduits:
			conduit.imageServerDatabase = self.imageServerDatabase

	def start(self):
		for conduit in self.conduits:
			conduit.run()

		self.run()


	def serverLoaderLoop(self):


		nextHousekeeping = time() + ImageServer.HOUSEKEEPING_EVERY_SECONDS
		nextMemCheck = time()

		self.loaderLoopRunning = True
		while (self.running):
			if self.jobQueue.qsize() > 0:
				#sleep(0.00001)
				sleep(0.00001)
			else:
				sleep(0.01)


			#print("Queue Size:",self.jobQueue.qsize())

			for conduit in self.conduits:
				if conduit.isBusy():
					#if conduit.job.state == StreamedImage.STATE_LOADED:
					#	job = conduit.job
					#	conduit.job = None
					#	self.surfaceQueue.put(job)

					# TODO TEMP!
					if conduit.job.state == StreamedImage.STATE_READY:
						conduit.job = None
					elif conduit.job.state == StreamedImage.STATE_ERROR_ON_LOAD:
						conduit.job = None


			if not self.paused:
				if self.jobQueue.qsize() > 0:
					for conduit in self.conduits:
						if not conduit.isBusy():
							job = self.jobQueue.get()


							# TODO make dependend on ram
							job._loadQuality = job._orderedQuality




							conduit.setJob(job)
							if self.jobQueue.qsize() == 0:
								break



			housekeepingNow = False
			if nextMemCheck < time() or nextHousekeeping < time():
				nextMemCheck = time() + ImageServer.MEMCHECK_EVERY_SECONDS
				self._calculateMemoryUsage()
				
				if self._bytesUsedTotal > ImageServer.HOUSEKEEPING_MAX_MEM_MB_THRESHOLD * 1024 * 1024:
					pass
					#housekeepingNow = True
					# TODO when more than MB RAM => panic if it will not go down after gc => then housekeeping IS ALWAYS RUNNING

				self.printStatistic()


			if nextHousekeeping < time() or housekeepingNow:
				nextHousekeeping = time() + ImageServer.HOUSEKEEPING_EVERY_SECONDS

				
				for i in range(0,4):
					if ImageServer.HOUSEKEEPING_THRESHOLD[i] > 0 and ImageServer.HOUSEKEEPING_THRESHOLD[i] < self._surfacesPresent[i]:
						housekeepingNow = True

				'''
				for conduit in self.conduits:
					j = conduit.job
					if j != None:
						print("Conduit "+str(conduit.name)+" job: "+j.originalFilePath)
					else:
						print("Conduit "+str(conduit.name)+" job: None")
				'''

				if housekeepingNow:
					print("Housekeeping!")

					for image in self.streamedImages.getCopyOfList():

						if image._surfaces[1][StreamedImage.SURFACE_AGE] >= 5:
							image.unloadUnused()

						image.incrementAge()
				else:
					print("No housekeeping needed!")

		print("ImageServer loader loop exited")
		self.loaderLoopRunning = False

	def addView(self,view):
		self.views.append(view)

	def addFapTableView(self,fapTableView):
		self.fapTableViews.append(fapTableView)

	def serverViewFetcherLoop(self):


		self.fetcherLoopRunning = True
		while (self.running):
			sleep(0.2)
			for view in self.views:
				sleep(1)


				# did view move at all?

				viewChunkx1_C = view.world.convert_S_to_C(view.worldx1_S)
				viewChunky1_C = view.world.convert_S_to_C(view.worldy1_S)
				viewChunkx2_C = view.world.convert_S_to_C(view.worldx2_S)
				viewChunky2_C = view.world.convert_S_to_C(view.worldy2_S)

				# based on height, fetch surrounding chunks also
				#print("HiRes Reloading"+str(abs(viewChunkx2_C-viewChunkx1_C)*abs(viewChunky2_C-viewChunky1_C))+"chunks")
				#print(str(viewChunkx1_C)+","+str(viewChunky1_C)+" -- "+str(viewChunkx2_C)+","+str(viewChunky2_C))
				for x in range(viewChunkx1_C, viewChunkx2_C+1):
					for y in range(viewChunky1_C, viewChunky2_C+1):
						chunk = view.world.getChunkAt_C(x,y)


						for SLx in range(0, World.CHUNK_SIZE):
							for SLy in range(0, World.CHUNK_SIZE):
								frame = chunk.getFrameAt_SL(SLx,SLy)


								if frame != None:
									image = frame.image
	

									neededQuality = StreamedImage.QUALITY_THUMB

									if view.height < World.SPOT_SIZE / self.qualityPixelSizes[StreamedImage.QUALITY_THUMB]:
										neededQuality = StreamedImage.QUALITY_GRID
									sx = SLx + chunk.top_sx
									sy = SLy + chunk.top_sy
									isOnScreen = (view.worldx1_S <= sx) and (sx <= view.worldx2_S) and (view.worldy1_S <= sy) and (sy <= view.worldy2_S)
									if isOnScreen and view.height <= World.SPOT_SIZE / (self.qualityPixelSizes[StreamedImage.QUALITY_SCREEN] / 2):
										neededQuality = StreamedImage.QUALITY_SCREEN
	
									if isOnScreen and view.height < World.SPOT_SIZE / (self.qualityPixelSizes[StreamedImage.QUALITY_SCREEN]):
										neededQuality = StreamedImage.QUALITY_ORIGINAL
									#print(neededQuality)

									if image.state == StreamedImage.STATE_READY and image.getAvailableQuality() < neededQuality:
										image.setOrderedQuality(neededQuality)

										if image.getOrderedQuality() > image.getAvailableQuality():
											image.state = StreamedImage.STATE_READY_AND_RELOADING
											#self.jobQueue.put(image)
											self.jobQueue.queue.insert(0,image)
											#print("Rescheduling "+image.originalFilePath+" with Q="+str(neededQuality)+" but is "+str(image.getAvailableQuality())+" Chunk "+str(x)+","+str(y))

				# fetch all images from all frames, is correct size already loaded?

				# if not, schedule

				# nevertheless, put to front of corresponding pipeline


				# load peek
				frame = view.world.getFrameAt_S(view.selection.x_S,view.selection.y_S)
				if frame != None:
					image = frame.image
					if image != None:


						if image.state == StreamedImage.STATE_READY and image.getAvailableQuality() < StreamedImage.QUALITY_ORIGINAL:
							image.setOrderedQuality(StreamedImage.QUALITY_ORIGINAL)

							if image.getOrderedQuality() > image.getAvailableQuality():
								image.state = StreamedImage.STATE_READY_AND_RELOADING

								#self.jobQueue.put(image)
								self.jobQueue.queue.insert(0,image)

			# load current Fap Table in HiRes
			for fapTableView in self.fapTableViews:

				currentFapTable = fapTableView.fapTable
				if currentFapTable != None and currentFapTable.isDisplayed:
					for card in currentFapTable.cards:
						if card.image != None:
							image = card.image
							if image.state == StreamedImage.STATE_READY and image.getAvailableQuality() < StreamedImage.QUALITY_ORIGINAL:
								image.setOrderedQuality(StreamedImage.QUALITY_ORIGINAL)

								if image.getOrderedQuality() > image.getAvailableQuality():
									image.state = StreamedImage.STATE_READY_AND_RELOADING


									self.jobQueue.queue.insert(0,image)
					
					


		print("ImageServer fetcher loop exited")
		self.fetcherLoopRunning = False


	def run(self):
		self.threadLoader = threading.Thread(target=self.serverLoaderLoop, args=())
		self.threadLoader.daemon = True # so these threads get killed when program exits
		self.threadLoader.start()

		self.threadViewFetcher = threading.Thread(target=self.serverViewFetcherLoop, args=())
		self.threadViewFetcher.daemon = True # so these threads get killed when program exits
		self.threadViewFetcher.start()

	def stop(self):
		self.running = False
		for conduit in self.conduits:
			conduit.close()

		while (self.fetcherLoopRunning) or (self.loaderLoopRunning):
			sleep(0.06)

		self.imageServerDatabase.stop()

	#def createStreamedImage(self,path,proxySurface):
	#	image = StreamedImage()
	#	image.setProxySurface(proxySurface.copy())
	#	image.setOriginalFilePath(path)

	#	self.jobQueue.put(image)
	#	return image

	def createStreamedImage(self,path, quality = StreamedImage.QUALITY_ORIGINAL):
		image = StreamedImage()
		image.setOriginalFilePath(path)
		image.setOrderedQuality(quality)
		self.streamedImages.append(image)
		self.jobQueue.put(image)
		return image


	def getNumberOfImages(self):
		return self.streamedImages.length()



	def getQueueSize(self):
		return self.jobQueue.qsize()

	def _calculateMemoryUsage(self):
		self._bytesUsedTotal = 0
		self._bytesUsedSizes = [0,0,0,0]
		self._surfacesPresent = [0,0,0,0]

		for image in self.streamedImages.getCopyOfList():
			self._bytesUsedTotal += image.getMemoryUsage()
			self._bytesUsedSizes[0] += image._surfaces[0][StreamedImage.SURFACE_BYTES]
			self._bytesUsedSizes[1] += image._surfaces[1][StreamedImage.SURFACE_BYTES]
			self._bytesUsedSizes[2] += image._surfaces[2][StreamedImage.SURFACE_BYTES]
			self._bytesUsedSizes[3] += image._surfaces[3][StreamedImage.SURFACE_BYTES]

			if image._surfaces[0][StreamedImage.SURFACE_SURFACE] != None:
				self._surfacesPresent[0] += 1
			if image._surfaces[1][StreamedImage.SURFACE_SURFACE] != None:
				self._surfacesPresent[1] += 1
			if image._surfaces[2][StreamedImage.SURFACE_SURFACE] != None:
				self._surfacesPresent[2] += 1
			if image._surfaces[3][StreamedImage.SURFACE_SURFACE] != None:
				self._surfacesPresent[3] += 1

			p = ""
			if self.paused:
				p = " PAUSED"
			self._statusLine = "T "+str(self._surfacesPresent[0])+" G "+str(self._surfacesPresent[1])+" S "+str(self._surfacesPresent[2])+" O "+str(self._surfacesPresent[3])+p

	def getStatusLine(self):
		return self._statusLine

	def printStatistic(self):
		mb = 1024*1024
		print("Total:",int(self._bytesUsedTotal / mb))
		print("Thumbs   ",self._surfacesPresent[0],"using",int(self._bytesUsedSizes[0]/mb),"MB")
		print("Grid     ",self._surfacesPresent[1],"using",int(self._bytesUsedSizes[1]/mb),"MB")
		print("Screen   ",self._surfacesPresent[2],"using",int(self._bytesUsedSizes[2]/mb),"MB")
		print("Original ",self._surfacesPresent[3],"using",int(self._bytesUsedSizes[3]/mb),"MB")

	def calculateMemoryUsage(self):
		return self._bytesUsedTotal

	#def update(self):
	#	# to be called from pygame thread
	#	updatesDone = 0
	#	while updatesDone < 4 and self.surfaceQueue.qsize() > 0:
	#		job = self.surfaceQueue.get()
	#		#print("Buffer LENGTH:",len(job.pilImageBytes))
	#		image = pygame.image.frombuffer(job.pilImageBytes, (job.width, job.height), job.mode)
	#		job.setSurface(image)
	#		job.state = StreamedImage.STATE_READY
	#		job.pilImageBytes = None # TODO useful for garbage collector? or does pygame reuse bytes?
	#		updatesDone = updatesDone + 1
