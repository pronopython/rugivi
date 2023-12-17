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
from pathlib import Path
import configparser
from . import dir_helper as dir_helper


class ConfigFileHandler:
	def __init__(self, configFilePath) -> None:
		self.config_file_path = configFilePath

		self.homedir = dir_helper.get_home_dir()
		self.config_file_path = dir_helper.expand_home_dir(self.config_file_path)

		self.create_config_parser_and_load_config()
		self.config_changed = False

	def create_config_parser_and_load_config(self) -> None:
		self.config_parser: configparser.RawConfigParser = None  # type: ignore
		print("Opening config file", self.config_file_path)
		if os.path.isfile(self.config_file_path):
			self.config_parser = configparser.RawConfigParser(allow_no_value=True)
			self.config_parser.read(self.config_file_path)
		else:
			print("Config file is missing, abort!")
			exit()

	def get_config_parser(self) -> configparser.RawConfigParser:
		return self.config_parser

	def get(self, group, key) -> str:
		return self.config_parser.get(group, key)

	def get_int(self, group, key) -> int:
		return int(self.config_parser.get(group, key))

	def get_boolean(self, group, key) -> bool:
		return self.config_parser.get(group, key) in ("True", "TRUE", "true", "1")

	def get_directory_path(self, group, key, ifEmpty="") -> str:
		path = self.get(group, key)
		if path == "":
			return ifEmpty.replace("~", self.homedir)
		return path.replace("~", self.homedir)

	def items(self, group) -> list:
		return self.config_parser.items(group)

	def change_config(self) -> configparser.RawConfigParser:
		self.config_changed = True
		return self.config_parser

	def write_changed_config(self) -> None:
		if self.config_changed:
			print("Writing changes to config file", self.config_file_path)
			configfile = open(self.config_file_path, "w")
			self.config_parser.write(configfile)
