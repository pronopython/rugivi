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

import abc
from typing import Optional
from pygame.surface import Surface


class AbstractStreamedMedia:
	__metaclass__ = abc.ABCMeta

	# for .state
	STATE_NEW = "new"
	STATE_LOADED = "data loaded"
	STATE_RESCALE = "rescale"
	STATE_READY = "surface ready"
	STATE_READY_AND_RELOADING = "surface ready and reloading"
	STATE_ERROR_ON_LOAD = "error on load"

	# for quality attributes
	QUALITY_NONE = -2
	QUALITY_COLOR = -1
	QUALITY_THUMB = 0  # really small
	QUALITY_GRID = 1  # bigger as a thumb, grid size
	QUALITY_SCREEN = 2  # max screen fit
	QUALITY_ORIGINAL = 3
	QUALITY_ALL = 100  # used for memory usage

	# for ._surfaces
	SURFACE_AGE = 0
	SURFACE_ACCESSED = 1
	SURFACE_BYTES = 2
	SURFACE_SURFACE = 3

	def __init__(self) -> None:
		self.state = AbstractStreamedMedia.STATE_NEW

		self.original_file_path: str = None  # type: ignore # always the path to an image (user file or cache image surrogate)
		self._extended_dictionary = None

		self.aspect_ratio: float = 1.0  # width * aspectRatio = height
		self.width = 0
		self.height = 0
		self.bytes_per_pixel = 3

		self.average_color = (255, 0, 0)

		self.drawn_view_world_x_P = -1
		self.drawn_view_world_y_P = -1
		self.drawn_view_height = -1.0
		self.drawn_view_token = -1

		# age, bytes, surface
		self._surfaces = [
			[0, 0, 0, None],
			[0, 0, 0, None],
			[0, 0, 0, None],
			[0, 0, 0, None],
		]
		self._available_quality = AbstractStreamedMedia.QUALITY_NONE
		self._load_quality = AbstractStreamedMedia.QUALITY_NONE
		self._ordered_quality = AbstractStreamedMedia.QUALITY_NONE

	@abc.abstractmethod
	def get_surface(self, quality=None) -> Optional[Surface]:
		""":return: Ordered Quality or if no quality is specified best quality surface"""
		pass

	@abc.abstractmethod
	def get_memory_usage_in_bytes(self, quality: int = QUALITY_ALL) -> int:
		"""
		:param quality: for which quality to return the used bytes
		                (allowed: QUALITY_THUMB, QUALITY_GRID, QUALITY_SCREEN, QUALITY_ORIGINAL, QUALITY_ALL)
		:return: usage in bytes per QUALITY_x constant
		"""
		pass

	@abc.abstractmethod
	def get_number_of_surfaces_loaded_in_ram(self, quality: int = QUALITY_ALL) -> int:
		"""
		:param quality: for which quality to return the number of loaded surfaces
		                (allowed: QUALITY_THUMB, QUALITY_GRID, QUALITY_SCREEN, QUALITY_ORIGINAL, QUALITY_ALL)
		:return: number of loaded surfaces of this media in the given quality (normally 0..1 for images, 0..* for videos)
		"""
		pass

	@abc.abstractmethod
	def increment_age(self) -> None:
		"""increments all age counter this media has"""
		pass

	@abc.abstractmethod
	def unload_except_thumb(self) -> None:
		"""discards all RAM stored media data except color and thumbnail representation"""
		pass

	def set_original_file_path(self, path) -> None:
		self.original_file_path = path

	def get_status(self) -> str:
		return self.state + "@" + self.original_file_path

	def get_available_quality(self) -> int:
		return self._available_quality

	def get_ordered_quality(self) -> int:
		return self._ordered_quality

	def set_ordered_quality(self, quality) -> None:
		self._ordered_quality = quality

	def set_extended_attribute(self, key, value):
		if self._extended_dictionary == None:
			self._extended_dictionary = {}
		self._extended_dictionary[key] = value

	def get_extended_attribute(self, key):
		if self._extended_dictionary == None:
			return None
		if key in self._extended_dictionary:
			return self._extended_dictionary[key]
		else:
			return None