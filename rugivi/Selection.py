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

class Selection:

	def __init__(self, world, view):
		self.world = world
		self.view = view

		self.x_S = 0
		self.y_S = 0

		self.colormix = 0

		self.peekEnabled = False

		self.frame = None
		self.image = None


	def isVisible(self):
		return self.view.worldx1_S <= self.x_S and  self.view.worldy1_S <= self.y_S and  self.view.worldx2_S >= self.x_S and  self.view.worldy2_S >= self.y_S


	def updateSelectedSpot(self):
		self.frame = self.world.getFrameAt_S(self.x_S,self.y_S)
		if self.frame != None:
			self.image = self.frame.image

	def getSelectedFile(self):
		if self.image != None:
			return self.image.originalFilePath
		else:
			return None
