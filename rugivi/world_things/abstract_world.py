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
import math

class AbstractWorld:
	__metaclass__ = abc.ABCMeta 
	SPOT_SIZE = 4096  # pixels
	CHUNK_SIZE = 32  # spots

	def __init__(self) -> None:
		pass

	def convert_SL_to_S(self,sl,c):
		return ( c * AbstractWorld.CHUNK_SIZE ) + sl
	
	def convert_S_to_C(self, s: int) -> int:
		return math.floor(s / AbstractWorld.CHUNK_SIZE)

	def convert_S_to_SL(self, s: int) -> int:
		return s % AbstractWorld.CHUNK_SIZE