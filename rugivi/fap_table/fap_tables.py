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
from rugivi.config_file_handler import ConfigFileHandler

from rugivi.image_service.image_server import *

from rugivi import dir_helper


class FapTables:
	def __init__(self, configParser : ConfigFileHandler) -> None:

		self.configParser = configParser

		self.fap_tables_flat = []
		self.fap_tables = [[None]]
		self.fap_tables_pos = [0]
		self.x = 0
		self.y = 0

		parent_dirs = self.configParser.items("fapTableParentDirs")
		for parent_dir in parent_dirs:
			print("Scanning", parent_dir[1])
			sub_dirs = self.get_all_sub_dirs(parent_dir[1])
			print("   Subdirs:" + str(sub_dirs))
			sub_dirs.sort()
			self.fap_tables.append(sub_dirs)
			self.fap_tables_pos.append(len(sub_dirs) - 1)
			for sub_dir in sub_dirs:
				self.fap_tables_flat.append(sub_dir)

		single_dirs_from_config = self.configParser.items("fapTableSingleDirs")
		single_dirs = []
		for single_dir in single_dirs_from_config:
			single_dirs.append(single_dir[1])
			self.fap_tables_flat.append(single_dir[1])
		single_dirs.sort()
		self.fap_tables.append(single_dirs)
		self.fap_tables_pos.append(len(single_dirs) - 1)
		print("Loaded FapTables:")
		print(self.fap_tables)

	def get_all_sub_dirs(self, path):
		subdirs = []
		for root, d_names, f_names in os.walk(dir_helper.expand_home_dir(path)):
			for d_name in d_names:
				subdirs.append(os.path.join(root, d_name))
			break
		return subdirs

	def get_current_fap_table_dir(self):
		# print("current ft dir"+str(self.fapTables[self.y][self.x]))
		print("X=", self.x, "Y=", self.y)
		return self.fap_tables[self.y][self.x]

	def switch_next(self):
		self.x = self.x + 1
		if self.x >= len(self.fap_tables[self.y]):
			self.x = len(self.fap_tables[self.y]) - 1
		self.fap_tables_pos[self.y] = self.x

	def switch_previous(self):
		self.x = self.x - 1
		if self.x < 0:
			self.x = 0
		self.fap_tables_pos[self.y] = self.x

	def switch_up(self):
		self.y = self.y - 1
		if self.y < 0:
			self.y = 0
		self.x = self.fap_tables_pos[self.y]

	def switch_down(self):
		self.y = self.y + 1
		if self.y >= len(self.fap_tables):
			self.y = len(self.fap_tables) - 1
		self.x = self.fap_tables_pos[self.y]
