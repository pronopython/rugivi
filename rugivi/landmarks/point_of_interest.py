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


class PointOfInterest:
	def __init__(self, position=(0, 0), name="", color=(0, 0, 0)) -> None:
		self.position = position  # in x_S, y_S
		self.name = name
		self.color = color  # in R, G, B
		self.tour = None

	def _to_tuple(self):
		return (self.position, self.name, self.color)

	def _from_tuple(self, tuple):
		self.position = tuple[0]
		self.name = tuple[1]
		self.color = tuple[2]

	def is_same_spot(self, poi):
		if poi is None:
			return False
		return poi.position == self.position

	def __str__(self) -> str:
		return str(self.position)

	def __repr__(self):
		return self.__str__()
