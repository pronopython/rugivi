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

from rugivi.landmarks.point_of_interest import PointOfInterest


class Tour:
	def __init__(
		self,
		name="",
		insert_deletes_right_side=False,
		max_entries=-1,
		do_not_add_same_spot=False,
	) -> None:
		self.pois: list[PointOfInterest] = []
		self.tour_pois_position = 0
		self.insert_deletes_right_side = insert_deletes_right_side
		self.do_not_add_same_spot = do_not_add_same_spot
		self.max_entries = max_entries
		self.color = (0, 0, 0)
		self.name = name

	def __correct_size(self):
		while self.max_entries > 0 and len(self.pois) > self.max_entries:
			self.pois.pop(0)
			self.tour_pois_position -= 1

	def append(self, poi: PointOfInterest):
		if (
			self.do_not_add_same_spot
			and (
				(len(self.pois) > 0 and poi.is_same_spot(self.pois[-1]))
				or len(self.pois) == 0
			)
		) or not self.do_not_add_same_spot:
			poi.tour = self  # type: ignore
			self.pois.append(poi)
			self.tour_pois_position = len(self.pois) - 1
			self.__correct_size()

	def insert(self, poi: PointOfInterest):
		if (
			self.do_not_add_same_spot
			and (
				(
					len(self.pois) > 0
					and not poi.is_same_spot(self.pois[self.tour_pois_position])
				)
				or len(self.pois) == 0
			)
		) or not self.do_not_add_same_spot:
			poi.tour = self  # type: ignore
			if self.insert_deletes_right_side:
				if len(self.pois) > 1:
					self.pois = self.pois[0 : self.tour_pois_position + 1]
				self.pois.append(poi)
				self.tour_pois_position = len(self.pois) - 1
			else:
				self.pois.insert(self.tour_pois_position, poi)
				self.tour_pois_position = len(self.pois) + 1
			self.__correct_size()

	def get_poi(self):
		return self.pois[self.tour_pois_position]

	def go_back(self):
		if self.tour_pois_position > 0:
			self.tour_pois_position -= 1

	def go_forward(self):
		if self.tour_pois_position < len(self.pois) - 1:
			self.tour_pois_position += 1

	def get_current_poi(self) -> PointOfInterest:
		if self.has_pois():
			return self.pois[self.tour_pois_position]
		else:
			return None  # type: ignore

	def has_pois(self):
		return len(self.pois) > 0

	def _to_tuple(self):
		result = []
		tour_data = (
			self.name,
			self.color,
			self.max_entries,
			self.insert_deletes_right_side,
			self.tour_pois_position,
			self.do_not_add_same_spot,
		)
		result.append(tour_data)
		for poi in self.pois:
			result.append(poi._to_tuple)
		return result

	def _from_tuple(self, tuple):
		self.name = tuple[0][0]
		self.color = tuple[0][1]
		self.max_entries = tuple[0][2]
		self.insert_deletes_right_side = tuple[0][3]
		self.tour_pois_position = tuple[0][4]
		self.do_not_add_same_spot = tuple[0][5]
		for poi_tuple in tuple[1:]:
			poi = PointOfInterest()
			poi._from_tuple(poi_tuple)
			self.append(poi)
