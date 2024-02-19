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

from typing import Optional
from .world_things.world import World
from .image_service.abstract_streamed_media import AbstractStreamedMedia


class Selection:
	def __init__(self, world, view) -> None:
		self.world: World = world
		self.view = view

		self.x_S = 0
		self.y_S = 0

		self.colormix = 0

		self.peek_enabled = False

		self.frame = None
		self.image: AbstractStreamedMedia = None  # type: ignore

	def is_visible(self) -> bool:
		return (
			self.view.world_x1_S <= self.x_S
			and self.view.world_y1_S <= self.y_S
			and self.view.world_x2_S >= self.x_S
			and self.view.world_y2_S >= self.y_S
		)

	def update_selected_spot(self) -> None:
		self.frame = self.world.get_frame_at_S(self.x_S, self.y_S)
		if self.frame != None:
			self.image = self.frame.image  # type: ignore
		else:
			self.image = None # type: ignore

	def get_selected_file(self) -> Optional[str]:
		if self.image != None:
			if self.image.get_extended_attribute("video_file") != None:
				return self.image.get_extended_attribute("video_file")
			else:
				return self.image.original_file_path
		else:
			return None
