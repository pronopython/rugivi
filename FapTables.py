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

import pygame
import os

from ImageServer import *



class FapTables:


	def getAllSubDirs(self,path):
		subdirs = []
		for root,d_names,f_names in os.walk(path):
			for d_name in d_names:
				subdirs.append(os.path.join(root,d_name))
			break
		return subdirs





	def __init__(self, configParser):


		self.configParser = configParser

		self.fapTablesFlat = []
		self.fapTables = [[None]]
		self.fapTablesPos = [0]
		self.x = 0
		self.y = 0

		parentDirs = self.configParser.items("fapTableParentDirs")
		for parentDir in parentDirs:
			#print("Scanning", parentDir)
			subDirs = self.getAllSubDirs(parentDir[1])
			subDirs.sort()
			self.fapTables.append(subDirs)
			self.fapTablesPos.append(len(subDirs)-1)
			for subDir in subDirs:
				self.fapTablesFlat.append(subDir)

		singleDirsCnf = self.configParser.items("fapTableSingleDirs")
		singleDirs = []
		for singleDir in singleDirsCnf:
			singleDirs.append(singleDir[1])
			self.fapTablesFlat.append(singleDir[1])
		singleDirs.sort()
		self.fapTables.append(singleDirs)
		self.fapTablesPos.append(len(singleDirs)-1)
		print("Loaded FapTables:")
		print(self.fapTables)

	def getCurrentFapTableDir(self):
		#print("current ft dir"+str(self.fapTables[self.y][self.x]))

		return self.fapTables[self.y][self.x]



	def switchNext(self):
		self.x = self.x + 1
		if self.x >= len(self.fapTables[self.y]):
			self.x = len(self.fapTables[self.y])-1
		self.fapTablesPos[self.y] = self.x


	def switchPrevious(self):
		self.x = self.x - 1
		if self.x < 0:
			self.x = 0
		self.fapTablesPos[self.y] = self.x

	def switchUp(self):
		self.y = self.y - 1
		if self.y < 0:
			self.y = 0
		self.x = self.fapTablesPos[self.y]

	def switchDown(self):
		self.y = self.y + 1
		if self.y >= len(self.fapTables):
			self.y = len(self.fapTables)-1
		self.x = self.fapTablesPos[self.y]


