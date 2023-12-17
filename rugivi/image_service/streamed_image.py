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

from rugivi.image_service.abstract_streamed_media import AbstractStreamedMedia


class StreamedImage(AbstractStreamedMedia):
	def __init__(self):
		super().__init__()
		self._surface = None
		self._scaledSurface = None
		self.mode = None

	def get_surface(self, quality=None):
		if quality == None:
			quality = self._available_quality
		self._surfaces[quality][StreamedImage.SURFACE_ACCESSED] += 1
		self._surfaces[quality][StreamedImage.SURFACE_AGE] = 0
		return self._surfaces[quality][StreamedImage.SURFACE_SURFACE]

	def get_memory_usage_in_bytes(
		self, quality: int = AbstractStreamedMedia.QUALITY_ALL
	) -> int:
		if (
			quality >= AbstractStreamedMedia.QUALITY_THUMB
			and quality <= AbstractStreamedMedia.QUALITY_ORIGINAL
		):
			return self._surfaces[quality][StreamedImage.SURFACE_BYTES]
		else:
			# QUALITY_ALL (total bytes)
			return (
				self._surfaces[0][StreamedImage.SURFACE_BYTES]
				+ self._surfaces[1][StreamedImage.SURFACE_BYTES]
				+ self._surfaces[2][StreamedImage.SURFACE_BYTES]
				+ self._surfaces[3][StreamedImage.SURFACE_BYTES]
			)

	def get_number_of_surfaces_loaded_in_ram(
		self, quality: int = AbstractStreamedMedia.QUALITY_ALL
	) -> int:

		if (
			quality >= AbstractStreamedMedia.QUALITY_THUMB
			and quality <= AbstractStreamedMedia.QUALITY_ORIGINAL
		):
			if self._surfaces[quality][StreamedImage.SURFACE_SURFACE] != None:
				return 1
			else:
				return 0
		else:
			surface_present = 0
			for q in range(
				AbstractStreamedMedia.QUALITY_THUMB,
				AbstractStreamedMedia.QUALITY_ORIGINAL + 1,
			):
				if self._surfaces[q][StreamedImage.SURFACE_SURFACE] != None:
					surface_present += 1
			return surface_present

	def increment_age(self) -> None:
		self._surfaces[0][StreamedImage.SURFACE_AGE] += 1
		self._surfaces[1][StreamedImage.SURFACE_AGE] += 1
		self._surfaces[2][StreamedImage.SURFACE_AGE] += 1
		self._surfaces[3][StreamedImage.SURFACE_AGE] += 1

	def unload_except_thumb(self) -> None:
		if self.get_available_quality() >= StreamedImage.QUALITY_GRID:
			self._availableQuality = StreamedImage.QUALITY_THUMB

			self._surfaces[1][StreamedImage.SURFACE_SURFACE] = None
			self._surfaces[2][StreamedImage.SURFACE_SURFACE] = None
			self._surfaces[3][StreamedImage.SURFACE_SURFACE] = None

			self._surfaces[1][StreamedImage.SURFACE_BYTES] = 0
			self._surfaces[2][StreamedImage.SURFACE_BYTES] = 0
			self._surfaces[3][StreamedImage.SURFACE_BYTES] = 0

			self._surfaces[1][StreamedImage.SURFACE_AGE] = 0
			self._surfaces[2][StreamedImage.SURFACE_AGE] = 0
			self._surfaces[3][StreamedImage.SURFACE_AGE] = 0
