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
VERSION = "0.1.0-alpha"
#
##############################################################################################
#
# Copyright (C) 2023 PronoPython
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


