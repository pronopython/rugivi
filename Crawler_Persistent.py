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
import os
import random
from time import sleep,time
from pathlib import Path
from functools import reduce


from ImageServer import *
from World import *

from sqlitedict import SqliteDict


class ChunkSaveObject:

	def __init__(self):
		self.spots = []
		self.numberOfEmptySpots = 0
		self.cx = 0
		self.cy = 0
		self.top_sx = 0
		self.top_sy = 0



	'''
	def saveNumpySpots(self,numpySpots):
		matrix = []
		for y in range(0, World.CHUNK_SIZE):
			line = []
			for x in range(0, World.CHUNK_SIZE):
				frame = numpySpots[x,y]
				if frame != None:
					if frame.image != None:
						line.append(frame.image.originalFilePath)
						continue
				line.append("")
			matrix.append(line)
		self.spots = matrix
	'''
	def saveNumpySpots(self,numpySpots):
		self.spots = []
		for y in range(0, World.CHUNK_SIZE):
			for x in range(0, World.CHUNK_SIZE):
				frame = numpySpots[x,y]
				if frame != None:
					if frame.image != None:
						self.spots.append(frame.image.originalFilePath)
						continue
				self.spots.append("")

	def getSaveTupel(self):
		return (self.cx,self.cy,self.top_sx,self.top_sy,self.numberOfEmptySpots,self.spots)

	def loadFromTupel(self,tupel):
		self.spots = tupel[5]
		self.numberOfEmptySpots = tupel[4]
		self.cx = tupel[0]
		self.cy = tupel[1]
		self.top_sx = tupel[2]
		self.top_sy = tupel[3]

	def loadFromChunk(self,chunk):
		self.spots = None
		self.saveNumpySpots(chunk._spots)
		self.numberOfEmptySpots = chunk._numberOfEmptySpots
		self.cx = chunk.cx
		self.cy = chunk.cy
		self.top_sx = chunk.top_sx
		self.top_sy = chunk.top_sy







class Crawler_Persistent_DB:

	KEY_BORDERSPOTS = "borderSpots"
	KEY_BASEDIR = "basedir"
	KEY_DIRANDSTARTSPOT = "dirAndStartSpot"
	KEY_STATUS = "crawl_status"

	VALUE_STATUS_CRAWLING = "crawling"
	VALUE_STATUS_CRAWL_COMPLETED = "crawl_completed"



	def __init__(self, crawlerDbFile):

		self.db = SqliteDict(crawlerDbFile)
		#self.db_chunkSaveObjects = SqliteDict("chunks.sqlite", tablename="chunksaveobjects")
		#self.db_dirAndStartSpot = SqliteDict("chunks.sqlite", tablename="dirAndStartSpot")
		#self.db_visitedPaths = SqliteDict("chunks.sqlite", tablename="visitedPaths")



	def commitDB(self):

		# convert or update ChunkSaveObjects


		print("Commiting Chunk DB ...")
		self.db.commit()
		#self.db_chunkSaveObjects.commit()
		print("Commiting Chunk DB done")



	def get(self, key, zeroObject = None):
		obj = self.db.get(key)
		if obj == None:
			return zeroObject
		return obj


	def getAndPutIfNone(self, key, zeroObject = None):
		obj = self.db.get(key)
		if obj == None:
			self.put(key,zeroObject)
			return zeroObject
		return obj



	def put(self, key, obj):
		#print("putting",key,"=",obj)
		self.db[key] = obj


	#def putChunk(self, chunk):
	#	cso = ChunkSaveObject()



	def getChunkAt_C(self, cx,cy, world,imageServer):
		tupel = self.db.get(str((cx,cy)))
		if tupel == None:
			#print("PersiCrawl: Chunk not in db ",cx,cy)
			return None
		#print("PersiCrawl: Chunk db fetch  ",cx,cy)
		cso = ChunkSaveObject()
		cso.loadFromTupel(tupel)

		# ressurrect chunk...
		newChunk = Chunk(world,cx,cy)

		for y in range(0, World.CHUNK_SIZE):
			for x in range(0, World.CHUNK_SIZE):
				p = cso.spots[(y * World.CHUNK_SIZE) + x]
				if p != "":
					si = imageServer.createStreamedImage(p, StreamedImage.QUALITY_THUMB)

					#self.world.setFrameAt_S(Frame(si),sx,sy)
					newChunk.setFrameAt_SL(Frame(si),x,y)
		return newChunk

class Crawler_Persistent:

	def checksum(self,st):							# TODO remove?! not needed!
		return reduce(lambda x,y:x+y, map(ord, st))

	def __init__(self, world, imageServer,basedir, crawlerDbFile, skipFiles):



		self.db = Crawler_Persistent_DB(crawlerDbFile)


		self.world = world
		self.world.setChunkLoader(self) # set this crawler as the chunk loader

		self.imageServer = imageServer
		self.currentDir = ""
		self.status = "new"
		self.basedir = self.db.getAndPutIfNone(Crawler_Persistent_DB.KEY_BASEDIR,basedir)
		self.paused = False
		self.skipFiles = skipFiles
		
		self.STARTSPOT_NEAR_WORLD_CENTER = False
		#or
		self.STARTSPOT_NEAR_PARENT_DIR = True
		#
		self.ORGANIC_GROW = True
		self.NO_DIAGONAL_GROW = True
		self.REACH_OUT_ANT_MODE = True
		self.ANT_CORRIDOR_PROB = 1 # 0.5..1 less..more

		self.running = True
		self.crawlerLoopRunning = False




	def run(self):
		self.thread = threading.Thread(target=self.crawlerLoop, args=())
		self.thread.daemon = True # so these threads get killed when program exits
		self.thread.start()


	def stop(self):
		self.running = False
		print("Waiting for crawler to finish current dir...")
		while (self.crawlerLoopRunning):
			sleep(0.05)


	def crawlerLoop(self):

		status = self.db.getAndPutIfNone(Crawler_Persistent_DB.KEY_STATUS,Crawler_Persistent_DB.VALUE_STATUS_CRAWLING)

		if status == Crawler_Persistent_DB.VALUE_STATUS_CRAWL_COMPLETED:
			return

		#borderSpots = [(0,0)]


		borderSpots = self.db.get(Crawler_Persistent_DB.KEY_BORDERSPOTS)
		if borderSpots == None:
			borderSpots = set()
			borderSpots.add((0,0))



		path = Path(self.basedir)
		parentPath = path.parent.absolute()

		dirAndStartSpot = self.db.get(Crawler_Persistent_DB.KEY_DIRANDSTARTSPOT)
		if dirAndStartSpot == None:
			dirAndStartSpot = {}

		nextSaveAtNumberOfFrames = 10000

		self.crawlerLoopRunning = True
		for root,d_names,f_names in os.walk(self.basedir):


			while self.paused and self.running == True:
				sleep(1)
				self.status = "paused"

			rootPath = Path(root).absolute()
			#print("did i visit",rootPath,"?")
			if str(rootPath) in dirAndStartSpot:
				# already visited according to database
				#print("		already visited!")
				continue
			#print("		no, not found")

			# populating dirAndStartSpot when this is crawler is run for the first time
			if len(dirAndStartSpot) == 0:
				dirAndStartSpot[str(path.absolute())] = (0,0)
				dirAndStartSpot[str(parentPath)] = (0,0)

			self.status = "filter files"

			f_names = [ file for file in f_names if file.lower().endswith( ('.jpg','.jpeg','.gif','.png','.tif') ) ]
			#f_names = [ file for file in f_names if file.lower().endswith( ('.jpg','.jpeg') ) ]

			#self.status = "sleeping"
			#sleep(0.002)

			if self.imageServer.getQueueSize() > 100:
				while self.imageServer.getQueueSize() > 10 and self.running == True:
					self.status = "sleeping"
					sleep(0.2)

			if self.skipFiles > 0:
				self.skipFiles -= len(f_names)

				self.status = "to be skipped: "+str(self.skipFiles)
				continue




			neededSpots = len(f_names) # TODO... only count images...

			if neededSpots == 0:
				continue

			self.currentDir = os.path.basename(root)

			found = False


			foundSpots = []

			self.status = "finding biome"
			while not found:

				if self.running == False:
					print("Crawler loop stopped")
					self.crawlerLoopRunning = False
					return

				foundSpots = []

				#random.seed(self.checksum(self.currentDir))
				#startSpot = random.choice(borderSpots)
				startSpot = random.choice(tuple(borderSpots))

				if self.STARTSPOT_NEAR_WORLD_CENTER:
					for i in range (0,50):
						#candidate = random.choice(borderSpots)
						candidate = random.choice(tuple(borderSpots))
						(cx,cy) = candidate
						(sx,sy) = startSpot
						if abs(cx) < abs(sx) or abs(cy) < abs(sy):
							startSpot = candidate



				if self.STARTSPOT_NEAR_PARENT_DIR:
					path = Path(root)

					basedir = Path(self.basedir).absolute()
					# error: 2 times going to parent dir!
					#parentPath = path.parent.absolute()
					parentPath = path.absolute()
					while len(str(parentPath)) > len(str(basedir)):
						parentPath = parentPath.parent.absolute()
						if str(parentPath) in dirAndStartSpot:
							break


					parentSpot = dirAndStartSpot[str(parentPath)]
					#print("",parentSpot," -> ",parentPath)
					(px,py) = parentSpot
					# was 300 -> more time needed
					for i in range (0,30):
						#candidate = random.choice(borderSpots)
						candidate = random.choice(tuple(borderSpots))
						(cx,cy) = candidate
						(sx,sy) = startSpot
						# TODO changed or -> and
						if abs(cx-px) < abs(sx-px) and abs(cy-py) < abs(sy-py):
							startSpot = candidate








				'''

				if True:   # TODO far away
					# cool ====> do this from while to while
					# TODO: grow not around center but around start point of parent dir!!!!!
					for i in range (0,50):
						candidate = random.choice(borderSpots)
						(cx,cy) = candidate
						(sx,sy) = startSpot
						if abs(cx) > abs(sx) or abs(cy) > abs(sy):
							startSpot = candidate

				'''

				stack = [startSpot]

				while len(stack) > 0 and not found:

					if self.running == False:
						print("Crawler loop stopped")
						self.crawlerLoopRunning = False
						return

					if not self.ORGANIC_GROW:
						currentSpot = stack.pop(0)
					else:
						(sx,sy) = startSpot
						currentSpot = random.choice(stack)



						#REACH_OUT = random.random() < 0.4

						if self.REACH_OUT_ANT_MODE and neededSpots - len(foundSpots) != 0:
							REACH_OUT = random.random() < ( (neededSpots - len(foundSpots)) / neededSpots) * self.ANT_CORRIDOR_PROB
						else:
							REACH_OUT = False

						for i in range (0,50):
							candidate = random.choice(stack)
							(cx,cy) = candidate
							(ux,uy) = currentSpot
							#if abs(cx-sx) < abs(ux-sx) or abs(cy-sy) < abs(uy-sy):


							# TODO was both or, now test and
							if REACH_OUT:
								# TODO changed or -> and
								if abs(cx-sx) > abs(ux-sx) and abs(cy-sy) > abs(uy-sy):
									currentSpot = candidate
							else:
								# TODO changed or -> and
								if abs(cx-sx) < abs(ux-sx) and abs(cy-sy) < abs(uy-sy):
									currentSpot = candidate

						stack.remove(currentSpot)
					'''

				
					currentSpot = random.choice(stack)
					stack.remove(currentSpot)

					'''


					foundSpots.append(currentSpot)

					if len(foundSpots) >= neededSpots:
						found = True
						break

					(sx,sy) = currentSpot

					for x in range(sx - 1, sx + 2):
						for y in range(sy - 1, sy + 2):
							if sx == x and sy == y:
								continue

							if self.NO_DIAGONAL_GROW and abs(x-sx) - abs(y-sy) == 0:
								continue
							if (x,y) in foundSpots:
								continue
							if (x,y) in stack:
								continue
							if self.world.getFrameAt_S(x,y) != None:
								continue
							else:
								stack.append((x,y))


			self.status = "creating frames"

			for i,f in enumerate(f_names):
				p = os.path.join(root, f)


				si = self.imageServer.createStreamedImage(p, StreamedImage.QUALITY_THUMB)

				(sx,sy) = foundSpots[i]

				self.world.setFrameAt_S(Frame(si),sx,sy)


			self.status = "correcting border, "+str(len(foundSpots))+" spots to check"
			# correct border spots
			for currentSpot in foundSpots:
				(sx,sy) = currentSpot
				sleep(0.00003)

				for x in range(sx - 1, sx + 2):
					for y in range(sy - 1, sy + 2):
						if self.world.getFrameAt_S(x,y) != None:
							if (x,y) in borderSpots:
								borderSpots.remove((x,y))
						else:
							if (x,y) not in borderSpots:
								#borderSpots.append((x,y))
								borderSpots.add((x,y))


			self.status = "remember start spot"
			# remember startSpot of this dir
			path = Path(root).absolute()
			dirAndStartSpot[str(path)] = startSpot



			if self.world.countFrames() > nextSaveAtNumberOfFrames:
				nextSaveAtNumberOfFrames += 10000
				self.saveToDB(borderSpots,dirAndStartSpot)

			self.status = "fetching next dir"

			if self.running == False:
				print("Crawler loop stopped")
				self.crawlerLoopRunning = False
				return


		self.db.put(Crawler_Persistent_DB.KEY_STATUS, Crawler_Persistent_DB.VALUE_STATUS_CRAWLING)
		self.saveToDB(borderSpots,dirAndStartSpot)
		self.status = "crawl completed, chunk database finalized"
		self.crawlerLoopRunning = False
		print(self.status)

	def getChunkAt_C(self, cx,cy):
		#return None
		return self.db.getChunkAt_C(cx,cy, self.world,self.imageServer)



	def saveToDB(self,borderSpots,dirAndStartSpot):


		print("saving to db")
		self.status = "saving to db"
		self.db.put(Crawler_Persistent_DB.KEY_BORDERSPOTS, borderSpots)
		self.db.put(Crawler_Persistent_DB.KEY_DIRANDSTARTSPOT, dirAndStartSpot)

		#self.db.commitDB()
		allChunks = self.world.getAllChunksInMemoryAsList()
		for chunk in allChunks:
			if chunk.isEmpty():
				continue
			cso = ChunkSaveObject()
			cso.loadFromChunk(chunk)
			k = str((chunk.cx,chunk.cy))
			#print("inserting chunk",k)
			# storing in same as all the other keys is so hacky...
			# but commits are per table sadly...
			# and if program crashes between two commits...
			self.db.db[str((chunk.cx,chunk.cy))] = cso.getSaveTupel()


		self.db.commitDB()







