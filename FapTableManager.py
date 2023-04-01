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
from pygame.locals import *
import threading
from time import sleep,time

from ThreadSafeList import *
from FapTable import *
import random
from pathlib import Path
import json


class FapTableManager:

	SYNC_TABLE_EVERY_SECONDS = 5


	def __init__(self, imageServer):


		self.fapTables = ThreadSafeList()

		self.imageServer = imageServer
		self.running = True
		self.run()


	

	def run(self):
		self.thread = threading.Thread(target=self.managerLoop, args=())
		self.thread.daemon = True # so these threads get killed when program exits
		self.thread.start()


	def openFapTable(self, path):
		# TODO check if already loaded in manager
		path = Path(path).absolute()
		fapTable = FapTable(path)
		self.fapTables.append(fapTable)
		# is there a faptable.pos?
		return fapTable


	def openFapTableParentDir(self, path):
		lastFapTable = None
		for root,d_names,f_names in os.walk(path):
		
			for d_name in d_names:
				lastFapTable = self.openFapTable(os.path.join(root,d_name))

			break
		return lastFapTable



	def getFapTableByDir(self,path):
		if path == None:
			return None
		path = Path(path).absolute()
		for ft in self.fapTables.getCopyOfList():
			if ft.tableDir == path:
				#print("ft by dir:",ft.tableDir)
				return ft
		return None



	def getPreviousFapTable(self, currentFapTable):
		ft = self.fapTables.getCopyOfList()
		i = ft.index(currentFapTable)
		i = i - 1
		if i == -1:
			i = len(ft) - 1
		return ft[i]
	def getNextFapTable(self, currentFapTable):
		ft = self.fapTables.getCopyOfList()
		i = ft.index(currentFapTable)
		i = i + 1
		if i == len(ft):
			i = 0
		return ft[i]

	def managerLoop(self):

		self.managerLoopRunning = True
		print("FapTableManager started")
		while(self.running):

			sleep(3)
			for fapTable in self.fapTables.getCopyOfList():

				# TODO in view??? displayed?

				if fapTable.statusSync == FapTable.STATUS_SAVED:
					pass # TODO anything??
				elif fapTable.statusSync == FapTable.STATUS_NEW:
					pass # TODO anything??
				elif fapTable.statusSync == FapTable.STATUS_LOAD:

					cardsJson = []
					jsonFilename = os.path.join(fapTable.tableDir, "ftpositions.json")

					if (os.path.isfile(jsonFilename)):
						print("Loading fapTable json:", jsonFilename)
						with open(jsonFilename,encoding='utf-8') as f:
							cardsJson = json.load(f)
						for cardJson in cardsJson:
							card = FapTableCard()
							card.loadFromJsonDictionary(cardJson, fapTable.tableDir)
							card.image = self.imageServer.createStreamedImage(card.imagePath, StreamedImage.QUALITY_ORIGINAL)
							fapTable.cards.append(card)
							#print("Loaded card from json: "+card.filename)
						
							fapTable.statusSync = FapTable.STATUS_SAVED
					else:
						fapTable.statusSync = FapTable.STATUS_NEW
						



				if fapTable.lastSyncTime + FapTableManager.SYNC_TABLE_EVERY_SECONDS < time():

					fapTable.lastSyncTime = time()
					
					if fapTable.statusSync == FapTable.STATUS_CHANGED:
						saveCards = fapTable.cards.copy()
						cardsJson = []
						for card in saveCards:
							cardsJson.append(card.getJsonDictionary())
						#print(cardsJson)

						jsonFilename = os.path.join(fapTable.tableDir, "ftpositions.json")

						print("Saving fapTable json:", jsonFilename)
						with open(jsonFilename, 'w', encoding='utf-8') as f:
							json.dump(cardsJson, f, ensure_ascii=False, indent=4)

						fapTable.statusSync = FapTable.STATUS_SAVED


					if fapTable.isDisplayed:
						#loadsync
						#print("Syncing FT:",fapTable.tableDir)
						for root,d_names,f_names in os.walk(fapTable.tableDir):


							f_names = [ file for file in f_names if file.lower().endswith( ('.jpg','.jpeg','.gif','.png','.tif') ) ]

							previousCards = fapTable.cards.copy()
							newFiles = []
							foundCards = []

							for f_name in f_names:
								found = False
								for card in fapTable.cards:
									f_path = os.path.join(root, f_name)
									if card.imagePath == f_path:
										foundCards.append(card)
										previousCards.remove(card)
										found = True
										break
								if not found:
									newFiles.append(f_name)

							if len(newFiles) > 0 or len(previousCards) > 0:
								print("Syncing FT: "+fapTable.tableDir + " adding "+str(len(newFiles))+" and removing "+str(len(previousCards)))
								fapTable.statusSync = FapTable.STATUS_CHANGED

							# add new cards
							for filename in newFiles:
								f_path = os.path.join(root, filename)
								card = FapTableCard(f_path)
								fapTable.cards.append(card)

								card.image = self.imageServer.createStreamedImage(f_path, StreamedImage.QUALITY_ORIGINAL)
								card.x = random.uniform(0.01,0.99 - FapTableCard.CARD_INITIAL_SIZE)
								card.y = random.uniform(0.01,FapTable.TABLE_INITIAL_MAXIMUM_HEIGHT - FapTableCard.CARD_INITIAL_SIZE)





							# TODO remove vacant cards


							break

				# new? then init table
				# saved? load positions + thumbs
				# displayed? load images hi res
				#		AND sync dir every 5 sec if new image present (or one deleted)!
				# changed? save positions from time to time
				# out of display save positions now


				# also watch tables:
				# =====SETS============
				# |   |   |   |   |   |
				# =====ct============     NO too many images!!!






		print("FapTableManager loop exited")
		self.managerLoopRunning = False

	def stop(self):
		self.running = False

		while (self.managerLoopRunning):
			sleep(0.06)


