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


import os

from rugivi.image_service.image_server import *


class FapTableCard:

	CARD_INITIAL_SIZE = 0.10
	CARD_MINIMUM_SIZE = 0.03

	def __init__(self, image_path=None) -> None:

		self.image: AbstractStreamedMedia = None  # type: ignore
		self.image_path = image_path
		if image_path != None:
			self.filename = os.path.basename(image_path)
		else:
			self.filename = None

		self.x = 0
		self.y = 0
		self.width = FapTableCard.CARD_INITIAL_SIZE

		# STATE
		# NEW => CHANGED (edited positions) <=> SAVED (in view) <=> SAVED (hibernated)

	def get_json_dictionary(self) -> dict:
		return {"file": self.filename, "x": self.x, "y": self.y, "width": self.width}

	def load_from_json_dictionary(self, jd, parent_path) -> None:
		self.image_path = os.path.join(parent_path, jd["file"])
		self.filename = jd["file"]
		self.x = jd["x"]
		self.y = jd["y"]
		self.width = jd["width"]


class FapTable:

	STATUS_LOAD = "load"
	STATUS_NEW = "new"
	STATUS_CHANGED = "changed"
	STATUS_SAVED = "saved"

	TABLE_INITIAL_MAXIMUM_HEIGHT = 9.0 / 16.0  # always within a 16:9 display

	def __init__(self, table_dir) -> None:
		self.status_sync = FapTable.STATUS_LOAD
		self.is_displayed = False
		self.table_dir = table_dir
		self.last_sync_time: float = 0
		self.cards = []
