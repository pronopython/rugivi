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
import platform
import importlib

OS_LINUX = "Linux"
OS_WINDOWS = "Windows"
OS_MACOS = "Darwin"


def get_home_dir() -> str:
	return os.path.expanduser("~")


def expand_home_dir(path: str) -> str:
	return path.replace("~", get_home_dir())


def get_filename_without_extension(path_with_full_filename: str) -> str:
	return Path(path_with_full_filename).stem


def get_os() -> str:
	return platform.system()


def get_config_dir(subfolder_for_windows) -> str:
	config_dir = ""
	myos = get_os()
	if myos == OS_LINUX or myos == OS_MACOS:
		config_dir = os.path.join(get_home_dir(), ".config")
	elif myos == OS_WINDOWS:
		config_dir = os.path.join(os.environ["APPDATA"], subfolder_for_windows)
	return config_dir

def is_config_file_present(subfolder_for_windows, config_file_name) -> bool:
	return os.path.isfile(os.path.join(get_config_dir(subfolder_for_windows),config_file_name))

def get_install_dir() -> str:
	return os.path.dirname(os.path.realpath(__file__))


def get_module_dir(module):
	moduleSpec = importlib.machinery.PathFinder().find_spec(module)  # type: ignore
	if moduleSpec != None:
		return moduleSpec.submodule_search_locations[0]
	else:
		return None
