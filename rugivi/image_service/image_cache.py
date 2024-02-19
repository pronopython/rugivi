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
import pathlib
import uuid

from rugivi.image_service.abstract_cache_filename_generator import AbstractCacheFilenameGenerator

class ImageCache(AbstractCacheFilenameGenerator):



	def __init__(self, cache_base_dir) -> None:
		self.cache_base_dir = cache_base_dir

	def generate_path_for_uuid(self,uuid_name):
		full_path = self.__get_path_for_uuid(uuid_name)
		pathlib.Path(full_path).mkdir(parents=True, exist_ok=True)

	def generate_new_cache_uuid_and_filename(self) -> (str,str): # type: ignore
		uuid_name = uuid.uuid4().hex
		self.generate_path_for_uuid(uuid_name)
		full_path = self.__get_path_for_uuid(uuid_name)
		return uuid_name, self.__append_filename_to_path(full_path,uuid_name)
	
	def __get_path_for_uuid(self, uuid_name) -> str:
		path_level_1 = uuid_name[:2]
		path_level_2 = uuid_name[2:4]
		full_path = os.path.join(self.cache_base_dir, path_level_1, path_level_2)
		#full_path_and_filename = os.path.abspath(os.path.join(full_path, uuid_name))
		return str(full_path)


	def __append_filename_to_path(self, full_path,uuid_name)->str:
		return os.path.abspath(os.path.join(full_path, uuid_name + ".jpg"))

	def get_filename_for_uuid(self, uuid_name) -> str:
		full_path = self.__get_path_for_uuid(uuid_name)
		return self.__append_filename_to_path(full_path,uuid_name)

	def file_exists(self, uuid_name):
		return os.path.isfile(self.get_filename_for_uuid(uuid_name))