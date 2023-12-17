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

import threading
from threading import Lock
from time import sleep, time
import pygame

from sqlitedict import SqliteDict

from ..image_service.streamed_image import (
	StreamedImage,
)

from rugivi.image_service.abstract_streamed_media import AbstractStreamedMedia


class ImageProxy:
	def __init__(self) -> None:
		self.path: str = ""
		self.image_surface: pygame.surface.Surface = None  # type: ignore
		self.average_color = (255, 0, 0)
		self.aspect_ratio: float = 1
		self.width: int = -1
		self.height: int = -1
		self.bytes_per_pixel: int = 3
		self.thumb_width: int = -1
		self.thumb_height: int = -1

	def to_tuple(self) -> tuple:
		# Pygame 2.1.3 uses tobyte instead of tostring ... both result in bytes...
		return (
			pygame.image.tostring(self.image_surface, "RGB"),
			self.average_color,
			self.aspect_ratio,
			self.width,
			self.height,
			self.bytes_per_pixel,
			self.thumb_width,
			self.thumb_height,
		)

	def from_tuple(self, tuple_to_load) -> bool:
		""" :return: true, if this ImageProxy could be updated by the tuple_to_load """
		self.average_color = tuple_to_load[1]
		self.aspect_ratio = tuple_to_load[2]
		self.width = tuple_to_load[3]
		self.height = tuple_to_load[4]
		self.bytes_per_pixel = tuple_to_load[5]
		self.thumb_width = tuple_to_load[6]
		self.thumb_height = tuple_to_load[7]
		# Pygame 2.1.3 uses frombyte instead of fromstring ... both result in bytes...
		try:
			self.image_surface = pygame.image.fromstring(
				tuple_to_load[0], (self.thumb_width, self.thumb_height), "RGB"
			)
		except Exception as e:
			return False
		return True


class ImageServerDatabase:

	DB_COMMIT_EVERY_SECONDS = 120

	def __init__(self, db_filename) -> None:
		self.db_filename = db_filename
		self.db = SqliteDict(db_filename)
		self.image_db_size = 0
		self.running = True
		self.housekeeping_loop_running = False
		self.run()

	def add_image_thumb(self, image: StreamedImage) -> None:
		imageProxy = ImageProxy()

		imageProxy.path = image.original_file_path
		imageProxy.image_surface = image.get_surface(
			AbstractStreamedMedia.QUALITY_THUMB
		)
		imageProxy.average_color = image.average_color
		imageProxy.aspect_ratio = image.aspect_ratio
		imageProxy.bytes_per_pixel = image.bytes_per_pixel
		imageProxy.width = image.width
		imageProxy.height = image.height
		(
			imageProxy.thumb_width,
			imageProxy.thumb_height,
		) = imageProxy.image_surface.get_size()

		if imageProxy.image_surface != None:
			if imageProxy.path not in self.db:
				self.db[imageProxy.path] = imageProxy.to_tuple()

	def get_image_proxy_by_path(self, path) -> ImageProxy:
		""" :return: ImageProxy on success, None otherwise """
		tuple = self.db.get(path)
		if tuple != None:
			imageProxy = ImageProxy()
			success = imageProxy.from_tuple(tuple)
			if success:
				return imageProxy
			else:
				return None  # type: ignore
		else:
			return None  # type: ignore

	def run(self) -> None:
		self.thread = threading.Thread(target=self.housekeeping_loop, args=())
		self.thread.daemon = True  # so these threads get killed when program exits
		self.thread.start()

	def housekeeping_loop(self):
		self.housekeeping_loop_running = True
		while self.running:
			self.image_db_size = len(self.db)
			print("Thumb DB Size:", self.image_db_size)

			seconds_passed = 0

			while seconds_passed < ImageServerDatabase.DB_COMMIT_EVERY_SECONDS and self.running:
				sleep(1)
				seconds_passed += 1

			print("Commiting to thumb database...")
			self.db.commit()
			print("Commit to thumb database done")

		print("ImageServerDatabase stopped")
		self.housekeeping_loop_running = False

	def stop(self):
		self.running = False
		while self.housekeeping_loop_running:
			sleep(0.06)

	def close(self):
		self.thread.join()
		self.db.close()
