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
# Copyright (C) PronoPython
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

from typing import Optional
from rugivi.world_database_service.abstract_world_database import AbstractWorldDatabase
from rugivi.world_things.chunk import Chunk
from rugivi.world_things.frame import Frame
from threading import Lock
from .abstract_world import AbstractWorld
from rugivi.world_things.chunk import Chunk

class World(AbstractWorld):

	#
	# Addressing methods:
	# 	pixel		_P
	# 	spot		_S
	# 	chunk		_C
	#   chunk+spot	_CS
	# 				    +L local (eg chunk)

	def __init__(self) -> None:
		super().__init__()
		self._chunks: dict[tuple[int, int], Chunk] = {}
		self._lock = Lock()
		self._chunksInMemory: int = 0
		self._numberOfFrames: int = 0
		self.chunkLoader : AbstractWorldDatabase = None # type: ignore



	def get_chunk_at_C(self, x_C: int, y_C: int) -> Chunk:
		with self._lock:
			chunk = self._chunks.get((x_C, y_C))
			if chunk == None:
				newChunk: Optional[Chunk] = None
				if self.chunkLoader != None:
					newChunk = self.chunkLoader.get_chunk_at_C(x_C, y_C)
					# this new chunk is NOT connected to this world yet!
					if newChunk != None:
						self._chunks[(x_C, y_C)] = newChunk
						self._chunksInMemory += 1

						return newChunk
				newChunk = Chunk(self, x_C, y_C)
				self._chunks[(x_C, y_C)] = newChunk
				self._chunksInMemory += 1
				return newChunk
			else:
				return chunk

	def get_chunk_at_S(self, x_S: int, y_S: int) -> Chunk:
		x_C = self.convert_S_to_C(x_S)
		y_C = self.convert_S_to_C(y_S)
		return self.get_chunk_at_C(x_C, y_C)

	def get_frame_at_S(self, x_S: int, y_S: int) -> Frame:
		# get the chunk
		chunk = self.get_chunk_at_S(x_S, y_S)

		x_SL = self.convert_S_to_SL(x_S)
		y_SL = self.convert_S_to_SL(y_S)

		return chunk.get_frame_at_SL(x_SL, y_SL)

	def set_frame_at_S(self, frame, x_S: int, y_S: int) -> None:
		# get the chunk
		chunk = self.get_chunk_at_S(x_S, y_S)

		x_SL = self.convert_S_to_SL(x_S)
		y_SL = self.convert_S_to_SL(y_S)

		old_content_at_spot = chunk.get_frame_at_SL(x_SL, y_SL)
		if old_content_at_spot == None and frame != None:
			self._numberOfFrames += 1
		elif old_content_at_spot != None and frame == None:
			self._numberOfFrames -= 1
		chunk.set_frame_at_SL(frame, x_SL, y_SL)

	def count_chunks_in_memory(self) -> int:
		return self._chunksInMemory

	def count_frames(self) -> int:
		return self._numberOfFrames

	def set_chunk_loader(self, chunkLoader) -> None:
		self.chunkLoader = chunkLoader

	def get_all_chunks_in_memory_as_list(self) -> 'list[Chunk]':
		return list(self._chunks.values())
