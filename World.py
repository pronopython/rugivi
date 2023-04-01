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

import numpy
import math
from threading import Lock



class Frame:
	def __init__(self, image = None):
		self.image = image



class Chunk:


	def __init__(self, world, cx, cy):
		#lattice = np.empty( (3,3), dtype=object)
		#lattice.flat = [site(3) for _ in lattice.flat]
		self._lock = Lock()
		self._spots = numpy.empty( (World.CHUNK_SIZE, World.CHUNK_SIZE), dtype = object)
		self._numberOfEmptySpots = World.CHUNK_SIZE * World.CHUNK_SIZE
		self.world = world
		self.cx = cx
		self.cy = cy
		self.top_sx = cx * World.CHUNK_SIZE
		self.top_sy = cy * World.CHUNK_SIZE

	def getFrameAt_SL(self,slx,sly):
		return self._spots[slx,sly]

	def setFrameAt_SL(self,frame,slx,sly):
		with self._lock:
			if self._spots[slx,sly] == None and frame != None:
				self._numberOfEmptySpots -= 1
				self._spots[slx,sly] = frame
			elif self._spots[slx,sly] != None and frame == None:
				self._numberOfEmptySpots += 1
				self._spots[slx,sly] = frame

	def getAllSpots(self):
		with self._lock:
			return self._spots.flatten()


	def countEmptySpots(self):
		return self._numberOfEmptySpots

	def countUsedSpots(self):
		return (World.CHUNK_SIZE * World.CHUNK_SIZE) - self._numberOfEmptySpots

	def isEmpty(self):
		return self.countUsedSpots() == 0


class World:
	#SPOT_SIZE = 1024 # pixels
	#SPOT_SIZE = 2048 # pixels
	SPOT_SIZE = 4096 # pixels
	CHUNK_SIZE = 32 # spots

	# spot = 128x128 pixel
	# chunk = 32 x 32 spots (4096 x 4096 pixel), max 1024 frames
	# 
	# Addressing methods:
	#	pixel		_P
	#	spot		_S
	#	chunk		_C
	#   chunk+spot	_CS
	#				_.L local (eg chunk)

	def __init__(self):
		self._chunks = {}
		self._lock = Lock()
		self._chunksInMemory = 0
		self._numberOfFrames = 0
		self.chunkLoader = None

	def getSize_S(self):
		# size ((x1,y1),(x2,y2)) in spots
		pass


	def convert_S_to_C(self,s):
		return math.floor(s / World.CHUNK_SIZE)

	def convert_S_to_SL(self,s):
		return s % World.CHUNK_SIZE

	def getChunkAt_C(self,cx,cy):
		with self._lock:
			chunk = self._chunks.get((cx,cy))
			if chunk == None:
				newChunk = None
				if self.chunkLoader != None:
					newChunk = self.chunkLoader.getChunkAt_C(cx,cy)
					# this new chunk is NOT connected to this world yet!
					if newChunk != None:
						self._chunks[(cx,cy)] = newChunk
						self._chunksInMemory += 1

						return newChunk
				newChunk = Chunk(self,cx,cy)
				self._chunks[(cx,cy)] = newChunk
				self._chunksInMemory += 1
				return newChunk
			else:
				return chunk


	def getChunkAt_S(self,sx,sy):
		cx = self.convert_S_to_C(sx)
		cy = self.convert_S_to_C(sy)
		return self.getChunkAt_C(cx,cy)


	def getFrameAt_S(self,sx,sy):
		# get the chunk
		chunk = self.getChunkAt_S(sx,sy)

		slx = self.convert_S_to_SL(sx)
		sly = self.convert_S_to_SL(sy)

		return chunk.getFrameAt_SL(slx,sly)


	def setFrameAt_S(self,frame,sx,sy):
		# get the chunk
		chunk = self.getChunkAt_S(sx,sy)


		slx = self.convert_S_to_SL(sx)
		sly = self.convert_S_to_SL(sy)

		oldContent = chunk.getFrameAt_SL(slx,sly) 
		if oldContent == None and frame != None:
			self._numberOfFrames += 1
		elif oldContent != None and frame == None:
			self._numberOfFrames -= 1
		chunk.setFrameAt_SL(frame,slx,sly)

	def countChunksInMemory(self):
		return self._chunksInMemory

	def countFrames(self):
		return self._numberOfFrames


	def setChunkLoader(self, chunkLoader):
		self.chunkLoader = chunkLoader


	def getAllChunksInMemoryAsList(self):
		return list(self._chunks.values())
