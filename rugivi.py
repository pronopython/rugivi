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
#INSTALLDIR="/opt/rugivi" # TODO activate
INSTALLDIR="."
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
import sys

# Import pygame, hide welcome message because it messes with
# status output
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
from pygame.locals import *


import threading
from time import sleep
from time import time_ns
from queue import Queue
#from PIL import Image
import math
import psutil # TODO needs  pip install psutil
import random

from ImageServer import *
from Status import *
from World import *
#from Crawler_Simple import *
from Crawler_Persistent import *
from Dialogs import *
from View import *
from FapTableManager import *
from FapTableView import *
from FapTable import *
from FapTables import *
from Selection import *
#from InodeDatabase import *

import platform
import subprocess

import getopt	# commandline arg handler

from ConfigParser import *




class App:

	DOUBLECLICKTIME = 500





	def __init__(self):
		self.size = self.weight, self.heigth = 640,480 # TODO "height" results in segmentation fault errors... because... dunno
		self.display = None
		self.running = False
		self.imageServer = None
		self.showInfo = 2
		#self.iNodeDatabase = None

		self.worldDbFile = "chunks.sqlite"
		self.thumbDbFile = "thumbs.sqlite"
		self.iNodeDbFile = "inodes.sqlite"
		self.crawlDir = "."
		self.tagDir = ""


		self.configParser = ConfigParser()

		self.worldDbFile = self.configParser.getDir("world","worldDB", self.worldDbFile)
		self.thumbDbFile = self.configParser.getDir("thumbs","thumbDB", self.thumbDbFile)
		self.crawlDir = self.configParser.getDir("world","crawlerRootDir", self.crawlDir)
		#self.iNodeDbFile = self.configParser.getDir("tags","inodesDB", self.iNodeDbFile)
		#self.tagDir = self.configParser.getDir("tags","tagDir", self.tagDir)


		self.fapTables = FapTables(self.configParser)

		'''
		fapTables = [None]
		parentDirs = self.configParser.items("fapTableParentDirs")
		for parentDir in parentDirs:
			subDirs = self.getAllSubDirs(parentDir[0])
			fapTables.append(subDirs)

		singleDirsCnf = self.configParser.items("fapTableSingleDirs")
		singleDirs = []
		for singleDir in singleDirsCnf:
			singleDirs.append(singleDir[0])
		fapTables.append(singleDirs)
		print(fapTables)
		'''


		self.parseCommandlineArgs()


		print("World DB  :",self.worldDbFile)
		print("Thumbs DB :",self.thumbDbFile)
		print("Crawl root:",self.crawlDir)


		if self.configParser.getBoolean("control","reverseScrollWheelZoom"):
			self.zoomDirection = -1
		else:
			self.zoomDirection = 1


	def parseCommandlineArgs(self):

		#if len(sys.argv) < 2:
		#	print("Please specifiy dir to crawl") # TODO better help
		#	sys.exit(2)
		#elif len(sys.argv) == 2:
		#	self.crawlDir = str(sys.argv[1])
		#else:
		try:
			options, args = getopt.getopt(sys.argv[1:],"?hc:",["thumb-db=","world-db="])
		except getopt.GetoptError:
			print("Wrong parameters")
			# TODO show help
			sys.exit(2)


		for opt, arg in options:
			if (opt == '-h') or (opt == '-?'):
				# TODO add some help...
				sys.exit(2)
			elif opt == '-c':
				self.crawlDir = str(arg)
			elif opt == '--thumb-db':
				self.thumbDbFile = str(arg)
			elif opt == '--world-db':
				self.worldDbFile = str(arg)



	def open_file(self,path):
		if platform.system() == "Windows":
			os.startfile(path)
		elif platform.system() == "Darwin":
			subprocess.Popen(["open", path])
		else:
			subprocess.Popen(["xdg-open", path])




	def run(self):


		pygame.init()


		pygame.display.set_caption("RuGiVi")

		icon = pygame.image.load('icon.png')
		pygame.display.set_icon(icon)


		#self.display = pygame.display.set_mode(self.size, pygame.HWSURFACE | pygame.DOUBLEBUF)
		self.display = pygame.display.set_mode(self.size, pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF)

		self.imageServer = ImageServer(16, self.thumbDbFile)
		#window = pygame._sdl2.Window.from_display_module()

		#window.maximize()
		self.world = World()

		self.fapTableManager = FapTableManager(self.imageServer)

		clock = pygame.time.Clock()



		view = View(self.world)

		fapTableView = FapTableView()
		
		#currentFapTable = self.fapTableManager.openFapTable("./Fapsets/20220624")
		for ftdir in self.fapTables.fapTablesFlat:
			currentFapTable = self.fapTableManager.openFapTable(ftdir)
		#currentFapTable = self.fapTableManager.openFapTableParentDir("./../../fapelsystem/Fapsets")

		currentFapTable = self.fapTableManager.getFapTableByDir(self.fapTables.getCurrentFapTableDir())
		fapTableView.setCurrentFapTable(currentFapTable)

		self.imageServer.addView(view)
		self.imageServer.addFapTableView(fapTableView)


		moveview = False
		viewmoved = False

		movecard = False
		cardmoved = False
		currentEditCard = None
		cardResizeMode = False


		status = Status(self.configParser.getInt("fonts","statusFontSize"))


		#print("creating cat jobs")

		#nox = 240
		#noy = 130
		#for i in range(0,nox*noy):
			#view.manycats.append(self.imageServer.createStreamedImage("examplepics/sophiscated_cat.PNG", StreamedImage.QUALITY_GRID))

		'''
		sx = 0
		sy = 0
		sx_max = 240
		sy_max = 130
		for root,d_names,f_names in os.walk("PROV"):
			for f in f_names:
				p = os.path.join(root, f)
				si = self.imageServer.createStreamedImage(p, StreamedImage.QUALITY_GRID)
				view.manycats.append(si)
				self.world.setFrameAt_S(Frame(si),sx,sy)
				sx += 1
				if sx > sx_max:
					sx = 0
					sy += 1
				if sy > sy_max:
					break
			if sy > sy_max:
				break
			#if len(view.manycats) > 240*130:
			#	break


		print("Chunks loaded:",self.world.countChunksInMemory())
		'''



		#print("jobs created")

		path = self.crawlDir



		#if len(sys.argv) > 1:
		#	path = sys.argv[1]
		crawlerSkipFiles = 0 # TODO remove
		#if len(sys.argv) > 2:
		#	crawlerSkipFiles = int(sys.argv[2])



		#self.crawler = Crawler_Simple(self.world, self.imageServer,path, crawlerSkipFiles)
		self.crawler = Crawler_Persistent(self.world, self.imageServer,path, self.worldDbFile, crawlerSkipFiles)
		self.crawler.run()


		#self.iNodeDatabase = InodeDatabase(self.iNodeDbFile)
		#if self.tagDir != "":
		#	self.iNodeDatabase.addDir(self.tagDir)
		#self.iNodeDatabase.addDir(self.crawlDir)

		#self.iNodeDatabase.run()


		self.imageServer.start()

		print("Queue Size:",self.imageServer.jobQueue.qsize())

		self.running = True

		#fileUnderCenter = ""


		view_w_old = -1
		view_h_old = -1

		xyDialog = None

		dbclock = pygame.time.Clock() # clock for doubleclick left
		selectionclock = pygame.time.Clock() # clock for last willfull selection click
		selectionclockClickDone = False



		#smlsurf = pygame.Surface((320,200)) # TODO 8 bit test
		#pali = pygame.image.load("cranes.gif")

		while (self.running):



			#self.display.fill((0,0,0))

			info = pygame.display.Info()
			view_w,view_h = info.current_w,info.current_h

			redraw = False



			for event in pygame.event.get():
				if event.type == pygame.QUIT:

					self.running = False


				if fapTableView.editModeEnabled:
					if event.type == pygame.MOUSEMOTION and movecard:
						motion = pygame.mouse.get_rel()
						#print(motion)
						#view.worldx = view.worldx - int(motion[0]*view.height)
						#view.worldy = view.worldy - int(motion[1]*view.height)
						#view.redraw = True
						if currentEditCard != None:
							card = currentEditCard
						else:
							card = fapTableView.getCardAtPixelPos(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1])
							currentEditCard = card
							if card != None:
								if fapTableView.isCardLowerCorner(card,pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]):
									cardResizeMode = True
						if card != None:
							#print(card.imagePath)
							currentFapTable.statusSync = FapTable.STATUS_CHANGED
							if cardResizeMode:
								width = card.width + (motion[0]*fapTableView.cardStepPerPixel)
								if width >= FapTableCard.CARD_MINIMUM_SIZE:
									card.width = width
							else:
								card.x = card.x + (motion[0]*fapTableView.cardStepPerPixel)
								card.y = card.y + (motion[1]*fapTableView.cardStepPerPixel)
						cardmoved = True
						redraw = True

					elif event.type == pygame.MOUSEBUTTONDOWN:
						if event.button == 1:

							if dbclock.tick() < App.DOUBLECLICKTIME:
								#print("double click detected!")
								#view.selection.peekEnabled = not view.selection.peekEnabled
								pass


							motion = pygame.mouse.get_rel() # clear relative movement
							movecard = True

						elif event.button == 2:
							fapTableView.editModeEnabled = False
							redraw = True

					elif event.type == pygame.MOUSEBUTTONUP:
						if event.button == 1:
							movecard = False
							if cardmoved:
								cardmoved = False
								currentEditCard = None
								cardResizeMode = False
							else:
								# select clicked spot
								pass
								#clickx = view.worldx + int((pygame.mouse.get_pos()[0]-int(view_w/2))*view.height)
								#clicky = view.worldy + int((pygame.mouse.get_pos()[1]-int(view_h/2))*view.height)
								#clickx_S = int(clickx / World.SPOT_SIZE)
								#if clickx <

				else:
					if event.type == pygame.MOUSEMOTION and moveview:
						motion = pygame.mouse.get_rel()
						#print(motion)
						view.worldx = view.worldx - int(motion[0]*view.height)
						view.worldy = view.worldy - int(motion[1]*view.height)
						#view.redraw = True
						viewmoved = True

					elif event.type == pygame.MOUSEBUTTONDOWN:
						#print('In the event loop:', event.pos, event.button)
						if event.button == 1:

							if dbclock.tick() < App.DOUBLECLICKTIME:
								#print("double click detected!")
								view.selection.peekEnabled = not view.selection.peekEnabled



							motion = pygame.mouse.get_rel() # clear relative movement
							moveview = True
						elif event.button == 3:
						
														# select clicked spot
							clickx = view.worldx + int((pygame.mouse.get_pos()[0]-int(view_w/2))*view.height)
							clicky = view.worldy + int((pygame.mouse.get_pos()[1]-int(view_h/2))*view.height)
							clickx_S = int(clickx / World.SPOT_SIZE)
							if clickx < 0:
								clickx_S -= 1
							clicky_S = int(clicky / World.SPOT_SIZE)
							if clicky < 0:
								clicky_S -= 1
							view.selection.x_S = clickx_S
							view.selection.y_S = clicky_S
							view.selection.updateSelectedSpot()
							redraw = True

							selectionclock.tick()
							selectionclockClickDone = True
						
						
						
						
							view.worldx = view.worldx + int((pygame.mouse.get_pos()[0]-int(view_w/2))*view.height)
							view.worldy = view.worldy + int((pygame.mouse.get_pos()[1]-int(view_h/2))*view.height)
						elif event.button == 2:
							#if view.selection.getSelectedFile() != None:
								#subprocess.Popen(["python3","/opt/fapelsystem/fapel_tagger.py", view.selection.getSelectedFile()])
							fapTableView.editModeEnabled = True


					elif event.type == pygame.MOUSEBUTTONUP:
						if event.button == 1:
							moveview = False
							if viewmoved:
								viewmoved = False
							else:
								# select clicked spot
								clickx = view.worldx + int((pygame.mouse.get_pos()[0]-int(view_w/2))*view.height)
								clicky = view.worldy + int((pygame.mouse.get_pos()[1]-int(view_h/2))*view.height)
								clickx_S = int(clickx / World.SPOT_SIZE)
								if clickx < 0:
									clickx_S -= 1
								clicky_S = int(clicky / World.SPOT_SIZE)
								if clicky < 0:
									clicky_S -= 1
								view.selection.x_S = clickx_S
								view.selection.y_S = clicky_S
								view.selection.updateSelectedSpot()
								redraw = True

								selectionclock.tick()
								selectionclockClickDone = True



					elif event.type == MOUSEWHEEL:
						#print(event)
						#print(event.x, event.y)
						#print(event.flipped)
						if event.y != 0:
							#view.height = view.height - (event.y*0.04)
							#view.height = view.height - (event.y*0.12)
							#view.height = view.height - (event.y*0.15*(1+(16*(view.height/600))))

							if event.y * self.zoomDirection > 0:
								view.height = view.height / (1.2 + ((view.height / 20) * 0.1))

								if selectionclock.tick() > 500:
									selectionclockClickDone = False

								if ((World.SPOT_SIZE / view.height < view_h * 0.3) and (World.SPOT_SIZE / view.height < view_w * 0.3)) or selectionclockClickDone:

									# move view further to the selection when zooming in
									selx = int(view.selection.x_S * World.SPOT_SIZE + (World.SPOT_SIZE / 2))
									sely = int(view.selection.y_S * World.SPOT_SIZE + (World.SPOT_SIZE / 2))
									if view.selection.x_S != view.worldx / World.SPOT_SIZE or view.selection.y_S != view.worldy / World.SPOT_SIZE:
										distx = int((selx - view.worldx) / (1 + (0.3 * (1 - (view.height / view.maxHeight)))))
										disty = int((sely - view.worldy) / (1 + (0.3 * (1 - (view.height / view.maxHeight)))))
										view.worldx = view.worldx + distx
										view.worldy = view.worldy + disty



							else:
								view.height = view.height * (1.2 + ((view.height / 20) * 0.1))

							redraw = True
							#view.height = view.height - (event.y*1.30*(1+(30*(view.height/100))))
						if view.height < 1.0:
							view.height = 1.0
						if view.height > view.maxHeight:
							view.height = view.maxHeight
						#view.redraw = True

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_1:
						view.height = 1.0
						redraw = True
					elif event.key == pygame.K_2:
						#view.height = 1.0 + (((World.SPOT_SIZE / self.imageServer.qualityPixelSizes[StreamedImage.QUALITY_GRID]) - 1.0) / 2)
						view.height = World.SPOT_SIZE / self.imageServer.qualityPixelSizes[StreamedImage.QUALITY_SCREEN]
						redraw = True
					elif event.key == pygame.K_3:
						view.height = World.SPOT_SIZE / self.imageServer.qualityPixelSizes[StreamedImage.QUALITY_GRID]
						redraw = True
					elif event.key == pygame.K_4:
						view.height = World.SPOT_SIZE / self.imageServer.qualityPixelSizes[StreamedImage.QUALITY_THUMB]
						redraw = True
					elif event.key == pygame.K_5:
						view.height = 190.0 # 80
						redraw = True
					elif event.key == pygame.K_6:
						view.height = 280.0 #140
						redraw = True
					elif event.key == pygame.K_7:
						view.height = view.maxHeight #300.0
						redraw = True
					elif event.key == pygame.K_0:
						view.height = World.SPOT_SIZE / view_h
						redraw = True
					elif event.key == pygame.K_p:
						self.crawler.paused = not self.crawler.paused
					elif event.key == pygame.K_o:
						self.imageServer.paused = not self.imageServer.paused
					elif event.key == pygame.K_i:
						self.showInfo += 1
						if self.showInfo > 2:
							self.showInfo = 0
						redraw = True
					elif event.key == pygame.K_g:
						xyDialog = Dialog_xy()
					elif event.key == pygame.K_j:
						last_x_S = math.floor(view.worldx/World.SPOT_SIZE)
						last_y_S = math.floor(view.worldy/World.SPOT_SIZE)
						
						next_x_S = last_x_S
						next_y_S = last_y_S
						i = 20
						while i > 0 :
							i = i - 1
							next_x_S = last_x_S + random.randint(-100,100)
							next_y_S = last_y_S + random.randint(-100,100)
							frame = self.world.getFrameAt_S(next_x_S,next_y_S)
							if frame != None:
								last_x_S = next_x_S
								last_y_S = next_y_S
						view.worldx = last_x_S * World.SPOT_SIZE + int(World.SPOT_SIZE / 2)
						view.worldy = last_y_S * World.SPOT_SIZE + int(World.SPOT_SIZE / 2)
						redraw = True



					elif event.key == pygame.K_n:
						if view.selection.getSelectedFile() != None:
							self.open_file(view.selection.getSelectedFile())
					elif event.key == pygame.K_t:
						if view.selection.getSelectedFile() != None:
							subprocess.Popen(["python3","/opt/fapelsystem/fapel_tagger.py", view.selection.getSelectedFile()]) 
					elif event.key == pygame.K_s:
						if view.selection.getSelectedFile() != None:
							subprocess.Popen(["python3","/opt/fapelsystem/fapel_fap_set.py", view.selection.getSelectedFile()]) 
					elif event.key == pygame.K_LEFT:
						self.fapTables.switchPrevious()
						currentFapTable = self.fapTableManager.getFapTableByDir(self.fapTables.getCurrentFapTableDir())
						fapTableView.setCurrentFapTable(currentFapTable)
						redraw = True
					elif event.key == pygame.K_RIGHT:
						self.fapTables.switchNext()
						currentFapTable = self.fapTableManager.getFapTableByDir(self.fapTables.getCurrentFapTableDir())
						fapTableView.setCurrentFapTable(currentFapTable)
						redraw = True
					elif event.key == pygame.K_UP:
						self.fapTables.switchUp()
						currentFapTable = self.fapTableManager.getFapTableByDir(self.fapTables.getCurrentFapTableDir())
						fapTableView.setCurrentFapTable(currentFapTable)
						redraw = True
					elif event.key == pygame.K_DOWN:
						self.fapTables.switchDown()
						currentFapTable = self.fapTableManager.getFapTableByDir(self.fapTables.getCurrentFapTableDir())
						fapTableView.setCurrentFapTable(currentFapTable)
						redraw = True




			if (view_h != view_h_old) or (view_w != view_w_old):
				view_h_old = view_h
				view_w_old = view_w
				redraw = True


			if xyDialog != None and xyDialog.result != None:
				print("Going to", xyDialog.result)
				view.worldx = xyDialog.result[0] * World.SPOT_SIZE + int(World.SPOT_SIZE / 2)
				view.worldy = xyDialog.result[1] * World.SPOT_SIZE + int(World.SPOT_SIZE / 2)
				xyDialog = None





			if (not view.selection.isVisible()) or (not World.SPOT_SIZE / view.height < view_h * 0.7) or (not World.SPOT_SIZE / view.height < view_w * 0.7):
				# move selection to center when it's out of view or the image is almost full screen
				clickx = view.worldx
				clicky = view.worldy

				clickx_S = int(clickx / World.SPOT_SIZE)
				if clickx < 0:
					clickx_S -= 1
				clicky_S = int(clicky / World.SPOT_SIZE)
				if clicky < 0:
					clicky_S -= 1

				view.selection.x_S = clickx_S
				view.selection.y_S = clicky_S
				view.selection.updateSelectedSpot()

				# and switch off peek, when selection moves by itself
				view.selection.peekEnabled = False

				redraw = True



			if redraw:
				view.redrawtoken += 1
				if view.redrawtoken == 256:
					view.redrawtoken = 0


			# Instead of the event loop above you could also call pygame.event.pump
			# each frame to prevent the window from freezing. Comment it out to check it.
			# pygame.event.pump()

			#click = pygame.mouse.get_pressed()
			#mousex, mousey = pygame.mouse.get_pos()
			#print(click, mousex, mousey)



			#if img1 != None:
			#	if img1.state == StreamedImage.STATE_READY:
			#		self.display.blit(img1.getSurface(),(80,10))


			#for y in range(0,noy):
			#	for x in range(0,nox):
			#		pos = y*nox+x
			#		if manycats[pos].state == StreamedImage.STATE_READY:
			#			self.display.blit(manycats[pos].getScaledSurface(),(x*100,y*100))









			view.drawGrid = self.showInfo > 1

			if not fapTableView.editModeEnabled:

			
				#view.drawView(smlsurf,0,0,320,200)
				#smlsurf = smlsurf.convert(pali)
			
				#cat2 = pygame.transform.scale(smlsurf, (1600,1000))
				#self.display.blit(cat2,(0,0))
			
				view.drawView(self.display,0,0,view_w,view_h)
			else:
				self.display.fill((0,0,0,0))
			fapTableView.drawFapTableView(self.display,0,0,view_w,view_h)



			if self.showInfo > 0:



				#frame = self.world.getFrameAt_S(math.floor(view.worldx / World.SPOT_SIZE), math.floor(view.worldy / World.SPOT_SIZE))
				#if frame != None and frame.image != None:
				#	fileUnderCenter = frame.image.originalFilePath
				#else:
				#	fileUnderCenter = ""



				memuse = int(psutil.Process().memory_info().rss / (1024*1024))
				memuse2 = int(self.imageServer.calculateMemoryUsage() / (1024*1024))

				if (self.showInfo > 1):
					status.writeln("FPS: "+str(int(clock.get_fps())))
					status.writeln("Center: "+str(int(view.worldx))+","+str(int(view.worldy))+" Pixel; Spot: "+str(math.floor(view.worldx/World.SPOT_SIZE))+","+str(math.floor(view.worldy/World.SPOT_SIZE))+" Height: "+str(view.height))
					
				status.writeln("Selected Spot: "+str(view.selection.x_S)+","+str(view.selection.y_S))

				if (self.showInfo > 1):
					status.writeln("Disk Access Total Loaded: File: "+str(self.imageServer._totalDiskLoaded)+" DB: "+str(self.imageServer._totalDBLoaded))
					status.writeln("DB Size: "+str(self.imageServer.imageServerDatabase.imageDBsize))
					status.writeln("ImgDrawn: "+str(view.performance_imagesDrawn)+" maxDrawRounds:"+str(view.maxdrawrounds))
					status.writeln("MemP: "+str(memuse)+" MB")
					status.writeln("MemI: "+str(memuse2)+" MB")
					status.writeln("ImgServer: "+self.imageServer.getStatusLine())
					status.writeln("World loaded: Chunks: "+str(self.world.countChunksInMemory())+" Frames: "+str(self.world.countFrames()))
					status.writeln("Crawler Status: "+self.crawler.status)
					status.writeln("Crawler Dir: "+self.crawler.currentDir)
				status.writeln("Selected Image: "+view.selection.getSelectedFile())
				status.writeln("Queue: "+str(self.imageServer.getQueueSize()))
				if (self.showInfo > 1):
					status.writeln("")
					status.writeln("Keys: 1-7 zoom, 0 zoom fit, n open file")
					status.writeln("      i toggle info, o/p pause imgserver/crawl")
					status.writeln("      t tag, s add to set")

				status.draw(self.display)

			if self.running == False:
				self.display.fill((100,100,100,0))

				font = pygame.font.SysFont("monospace", 50)
				label = font.render("closing databases... please wait!", 1, (0,0,0))
				self.display.blit(label, (30, 30))

			pygame.display.flip()
			#self.imageServer.update()
			
			if self.imageServer.getQueueSize() > 200 and not moveview and not fapTableView.editModeEnabled:
				sleep(0.2)
			
			clock.tick(80) # TODO limits fps
			#clock.tick(20) # TODO limits fps

		font = pygame.font.SysFont("monospace", 50)
		label = font.render(".", 1, (0,0,0))
		self.display.blit(label, (30, 80))
		pygame.display.flip()

		print("Stopping image crawler")
		self.crawler.stop()
		#print("Stopping inode crawler")
		#self.iNodeDatabase.stop()
		self.display.blit(label, (30+40*1, 80))
		pygame.display.flip()

		print("Stopping FapTableManager")
		self.fapTableManager.stop()
		self.display.blit(label, (30+40*2, 80))
		pygame.display.flip()


		print("Stopping image server")
		self.imageServer.stop()
		self.display.blit(label, (30+40*3, 80))
		pygame.display.flip()
		print("Closing pygame window")
		pygame.quit()
		print("Bye bye")
		sys.exit(0)


print("RuGiVi Image World Viewer")
print("Version", VERSION)



if __name__ == "__main__":
	app = App()
	app.run()



