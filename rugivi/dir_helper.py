#!/usr/bin/python3
#
##############################################################################################
#
# The fapel system organizes image and video collections under Linux with standard folders.
#
# For updates see git-repo at
#https://github.com/pronopython/fapel-system
#
##############################################################################################
#
VERSION = "0.2.0" #TODO
CONFIGFILE="~/.config/fapel_system.conf"
#
##############################################################################################
#
# Copyright (C) 2022-2023 PronoPython
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
import platform
import importlib


def getHomeDir():
	return os.path.expanduser('~')

def expandHomeDir(path):
	return path.replace("~", getHomeDir())

def getFilenameWithoutExtension(pathWithFullFilename):
	return Path(pathWithFullFilename).stem

def getLastPartOfFilename(path):
	myName = getFilenameWithoutExtension(os.path.abspath(path))
	last1 = myName.split('_')[-1]
	last2 = myName.split('-')[-1]
	if (last1 != myName) or (last2 != myName):
		if len(last1) < len(last2):
			counterKey = last1
		else:
			counterKey = last2
	return counterKey

OS_LINUX = "Linux"
OS_WINDOWS = "Windows"
OS_MACOS = "Darwin"

def getOS():
	return platform.system()


def getConfigDir(subfolderForWindows):
	configDir = ""
	myos = getOS()
	if myos == OS_LINUX or myos == OS_MACOS:
		configDir = os.path.join(getHomeDir(),".config")
	elif myos == OS_WINDOWS:
		configDir = os.path.join(os.environ['APPDATA'], subfolderForWindows)
	return configDir

def getInstallDir():
	return os.path.dirname(os.path.realpath(__file__))


def getModuleDir(module):
	#return importlib.machinery.PathFinder().find_module(module).get_filename()
	moduleSpec = importlib.machinery.PathFinder().find_spec(module)
	if moduleSpec != None:
		return moduleSpec.submodule_search_locations[0]
	else:
		return None

