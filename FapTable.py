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



class FapTableCard:


	CARD_INITIAL_SIZE = 0.10
	CARD_MINIMUM_SIZE = 0.03

	def __init__(self, imagePath = None):


		self.image = None
		self.imagePath = imagePath
		if imagePath != None:
			self.filename = os.path.basename(imagePath)
		else:
			self.filename = None

		self.x = 0
		self.y = 0
		self.width = FapTableCard.CARD_INITIAL_SIZE

		#STATE
		# NEW => CHANGED (edited positions) <=> SAVED (in view) <=> SAVED (hibernated)

	def getJsonDictionary(self):
	
		return {'file' : self.filename,
			'x' : self.x,
			'y' : self.y,
			'width' : self.width}

	def loadFromJsonDictionary(self, jd, parentPath):
		self.imagePath = os.path.join(parentPath, jd['file'])
		self.filename = jd['file']
		self.x = jd['x']
		self.y = jd['y']
		self.width = jd['width']

class FapTable:


	STATUS_LOAD = "load"
	STATUS_NEW = "new"
	STATUS_CHANGED = "changed"
	STATUS_SAVED = "saved"

	TABLE_INITIAL_MAXIMUM_HEIGHT = 9.0 / 16.0	# always within a 16:9 display

	def __init__(self, tableDir):


		self.statusSync = FapTable.STATUS_LOAD
		self.isDisplayed = False
		self.tableDir = tableDir
		self.lastSyncTime = 0
		self.cards = []

		#self.fapTableFrames.append(FapTableFrame(p)

		#p = os.path.join(self.tableDir,"anQEzL0_460s.jpg")
		#self.si = self.imageServer.createStreamedImage(p, StreamedImage.QUALITY_THUMB)








