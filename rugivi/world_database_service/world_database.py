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

from time import time
from typing import Any
from rugivi.image_service.streamed_image import StreamedImage


from rugivi.image_service.image_server import *
from rugivi.world_database_service.abstract_world_database import AbstractWorldDatabase
from rugivi.world_things.chunk import Chunk
from rugivi.world_things.frame import Frame
from rugivi.world_things.world import *

from sqlitedict import SqliteDict


class ChunkSaveObject:
	def __init__(self) -> None:
		self.spots_filepath_list: list = []
		""" a list of spots filepath flattened from matrix row by row """

		self.number_of_empty_spots = 0
		self.x_C = 0
		self.y_C = 0
		self.top_spot_x_S = 0
		self.top_spot_y_S = 0

		self.extended_dictionaries: list = []

	def __save_numpy_spots(self, numpy_spots_matrix) -> None:
		self.spots_filepath_list = []
		for y_SL in range(0, World.CHUNK_SIZE):
			for x_SL in range(0, World.CHUNK_SIZE):
				frame: Frame = numpy_spots_matrix[x_SL, y_SL]
				if frame != None:
					if frame.image != None:
						self.spots_filepath_list.append(frame.image.original_file_path)
						continue
				self.spots_filepath_list.append("")

	def __save_extended_dictionaries(self, numpy_spots_matrix) -> None:
		self.extended_dictionaries = []
		has_extended_dictionary = False
		for y_SL in range(0, World.CHUNK_SIZE):
			for x_SL in range(0, World.CHUNK_SIZE):
				frame: Frame = numpy_spots_matrix[x_SL, y_SL]
				if frame != None:
					if frame.image != None:
						if (
							frame.image._extended_dictionary != None
							and len(frame.image._extended_dictionary) > 0
						):
							has_extended_dictionary = True
							self.extended_dictionaries.append(
								frame.image._extended_dictionary
							)
							continue
				self.extended_dictionaries.append({})
		if not has_extended_dictionary:
			self.extended_dictionaries = []

	def to_tuple(self) -> tuple:
		if len(self.extended_dictionaries) > 0:
			return (
				self.x_C,
				self.y_C,
				self.top_spot_x_S,
				self.top_spot_y_S,
				self.number_of_empty_spots,
				self.spots_filepath_list,
				self.extended_dictionaries,
			)
		else:
			return (
				self.x_C,
				self.y_C,
				self.top_spot_x_S,
				self.top_spot_y_S,
				self.number_of_empty_spots,
				self.spots_filepath_list,
			)

	def from_tupel(self, tupel) -> None:
		self.spots_filepath_list = tupel[5]
		self.number_of_empty_spots = tupel[4]
		self.x_C = tupel[0]
		self.y_C = tupel[1]
		self.top_spot_x_S = tupel[2]
		self.top_spot_y_S = tupel[3]
		if len(tupel) > 6:  # an extended dictionary was saved
			self.extended_dictionaries = tupel[6]

	def from_chunk(self, chunk: Chunk) -> None:
		self.spots_filepath_list = None  # type: ignore
		self.__save_numpy_spots(chunk._spots_matrix)
		self.__save_extended_dictionaries(chunk._spots_matrix)
		self.number_of_empty_spots = chunk._number_of_empty_spots
		self.x_C = chunk.x_C
		self.y_C = chunk.y_C
		self.top_spot_x_S = chunk.top_spot_x_S
		self.top_spot_y_S = chunk.top_spot_y_S


class WorldDatabase(AbstractWorldDatabase):

	KEY_BORDERSPOTS = "borderSpots"
	KEY_BASEDIR = "basedir"
	KEY_DIRANDSTARTSPOT = "dirAndStartSpot"
	KEY_STATUS = "crawl_status"

	VALUE_STATUS_CRAWLING = "crawling"
	VALUE_STATUS_CRAWL_COMPLETED = "crawl_completed"

	def __init__(
		self, crawler_db_file, world: World, image_server: ImageServer
	) -> None:

		self.db = SqliteDict(crawler_db_file)
		self.world = world
		self.image_server = image_server

	def commit_db(self) -> None:
		print("Commiting Chunk DB ...")
		self.db.commit()
		print("Commiting Chunk DB done")

	def get(self, key, object_if_none=None) -> Any:
		object_from_database = self.db.get(key)
		if object_from_database == None:
			return object_if_none
		return object_from_database

	def get_and_put_if_none(self, key, object_if_none) -> Any:
		object_from_database = self.db.get(key)
		if object_from_database == None:
			self.put(key, object_if_none)
			return object_if_none
		return object_from_database

	def put(self, key, object) -> None:
		self.db[key] = object

	def get_chunk_at_C(self, x_C, y_C) -> Chunk:
		tupel = self.db.get(str((x_C, y_C)))
		if tupel == None:
			return None  # type: ignore

		# ressurect chunk

		chunk_save_object = ChunkSaveObject()
		chunk_save_object.from_tupel(tupel)
		newChunk = Chunk(self.world, x_C, y_C)
		for y_SL in range(0, World.CHUNK_SIZE):
			for x_SL in range(0, World.CHUNK_SIZE):
				original_file_path = chunk_save_object.spots_filepath_list[
					(y_SL * World.CHUNK_SIZE) + x_SL
				]
				if original_file_path != "":
					streamed_image = self.image_server.create_streamed_image(
						original_file_path, StreamedImage.QUALITY_THUMB
					)

					if len(chunk_save_object.extended_dictionaries) > 0:
						streamed_image._extended_dictionary = (
							chunk_save_object.extended_dictionaries[
								(y_SL * World.CHUNK_SIZE) + x_SL
							]
						)

					newChunk.set_frame_at_SL(Frame(streamed_image), x_SL, y_SL)
		return newChunk

	def save_world_to_database(self) -> None:
		all_chunks = self.world.get_all_chunks_in_memory_as_list()
		for chunk in all_chunks:
			if chunk.is_empty():
				continue
			chunk_save_object = ChunkSaveObject()
			chunk_save_object.from_chunk(chunk)
			self.db[str((chunk.x_C, chunk.y_C))] = chunk_save_object.to_tuple()
		self.commit_db()
