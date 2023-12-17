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

from rugivi.world_things.frame import Frame
from rugivi.world_things.abstract_world import AbstractWorld


import numpy


from threading import Lock


class Chunk:
	def __init__(self, world: AbstractWorld, x_C, y_C) -> None:
		self._lock = Lock()
		self._spots_matrix = numpy.empty(
			(AbstractWorld.CHUNK_SIZE, AbstractWorld.CHUNK_SIZE), dtype=object
		)
		self._number_of_empty_spots = AbstractWorld.CHUNK_SIZE * AbstractWorld.CHUNK_SIZE
		self.world = world
		self.x_C = x_C
		self.y_C = y_C
		self.top_spot_x_S = x_C * AbstractWorld.CHUNK_SIZE
		self.top_spot_y_S = y_C * AbstractWorld.CHUNK_SIZE

	def get_frame_at_SL(self, x_SL: int, y_SL: int) -> Frame:
		return self._spots_matrix[x_SL, y_SL]

	def set_frame_at_SL(self, frame: Frame, x_SL: int, y_SL: int) -> None:

		if frame != None:
			frame.x_SL = x_SL
			frame.y_SL = y_SL
			frame.x_S = self.world.convert_SL_to_S(x_SL, self.x_C)
			frame.y_S = self.world.convert_SL_to_S(y_SL, self.y_C)

		with self._lock:
			if self._spots_matrix[x_SL, y_SL] == None and frame != None:
				self._number_of_empty_spots -= 1
				self._spots_matrix[x_SL, y_SL] = frame
			elif self._spots_matrix[x_SL, y_SL] != None and frame == None:
				self._number_of_empty_spots += 1
				self._spots_matrix[x_SL, y_SL] = frame

	def count_empty_spots(self) -> int:
		return self._number_of_empty_spots

	def count_used_spots(self) -> int:
		return (AbstractWorld.CHUNK_SIZE * AbstractWorld.CHUNK_SIZE) - self._number_of_empty_spots

	def is_empty(self) -> bool:
		return self.count_used_spots() == 0