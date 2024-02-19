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


class StreamedMockup(AbstractStreamedMedia):
	def __init__(self):
		super().__init__()
		self._surface = None
		self._scaledSurface = None
		self.mode = None

	def get_surface(self, quality=None):
		return None

	def get_memory_usage_in_bytes(
		self, quality: int = AbstractStreamedMedia.QUALITY_ALL
	) -> int:
		return 13

	def get_number_of_surfaces_loaded_in_ram(
		self, quality: int = AbstractStreamedMedia.QUALITY_ALL
	) -> int:
		return 0

	def increment_age(self) -> None:
		pass

	def unload_except_thumb(self) -> None:
		pass
