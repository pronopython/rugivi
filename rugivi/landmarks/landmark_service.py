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

from rugivi.landmarks.tour import Tour
from rugivi.world_database_service.world_database import WorldDatabase


class LandmarkService:
	def __init__(self, world_database: WorldDatabase) -> None:
		self.world_database = world_database
		self.tours = {}

	def load_from_db(self):
		pass

	def save_to_db(self):
		pass

	def get_tour_by_name(self, tourname) -> Tour:
		return None  # type: ignore

	def add_tour(self, tour: Tour):
		self.tours[tour.name] = tour
