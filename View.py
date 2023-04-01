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

from World import *
from ImageServer import *
from Selection import *
import random
from time import time_ns





class View:

	def __init__(self, world):
		self.worldx = 0
		self.worldy = 0
	#	self.height = 128.0
		self.height = World.SPOT_SIZE / ImageServer.QUALITY_PIXEL_SIZE[StreamedImage.QUALITY_THUMB]
		self.maxHeight = 600
		self.worldx_old = 0
		self.worldy_old = -1
		self.height_old = self.height



		self.worldx1_S = 0
		self.worldy1_S = 0
		self.worldx2_S = 0
		self.worldy2_S = 0

		#self.font = pygame.font.SysFont("monospace", 15)


		self.manycats = [] # TODO TEEEEMP!
		self.performance_imagesDrawn = 0
		#self.redraw = True

		self.world = world

		self.selection = Selection(world, self)

		self.redrawtoken = 0

		self.updateMatrix = []

		self.drawGrid = True


		self.updateMatrixSideLength = 4
		for y in range (0,self.updateMatrixSideLength):
			for x in range (0,self.updateMatrixSideLength):
				self.updateMatrix.append((x,y))

		random.shuffle(self.updateMatrix)

		self.updateMatrixPosition = 0
		self.redrawNecessary = True

		self.drawnPositions = {}

		self.maxdrawrounds = 1
		#self.maxdrawroundsqueue = [1,1,1,1,1,1,1,1,1,1]
		self.maxdrawroundsqueue = [1,1,1,1,1]


	def drawView(self,display,x,y,w,h):

		#draw snap grid

		#  ------------w------------
		#  |
		#  |
		#  h
		#  |
		#  |
		#  |------------------------
		#
		#   wx1,wy1
		#
		#
		#			worldx,worldy
		#			+ height
		#
		#
		#                       wx2,wy2

		#if self.redraw:
		#	display.fill((0,0,0,128))
		#	self.redraw = False

		wx1 = self.worldx-int((w/2)*self.height)
		wy1 = self.worldy-int((h/2)*self.height)
		wx2 = self.worldx+int((w/2)*self.height)
		wy2 = self.worldy+int((h/2)*self.height)



		'''
		gridstep = 128

		gridStartx = math.floor(wx1 / gridstep) * gridstep


		for gridx in range(gridStartx, wx2, gridstep):
			gx = int((gridx - wx1) / self.height)
			c = (80,0,0)
			if (gridx / gridstep) % 10 == 0:
				c = (128,128,128)
			pygame.draw.line(display, c, (gx,y), (gx,y+h))


		gridStarty = math.floor(wy1 / gridstep) * gridstep

		for gridy in range(gridStarty, wy2, gridstep):
			gy = int((gridy - wy1) / self.height)
			c = (80,0,0)
			if (gridy / gridstep) % 10 == 0:
				c = (128,128,128)
			pygame.draw.line(display, c, (x,gy), (x+w,gy))


		'''





		#label = self.font.render(str(self.worldx)+","+str(self.worldy), 1, (0,255,0))
		#display.blit(label, (3, 300))

		self.performance_imagesDrawn = 0
		nox = 240
		noy = 130
		#catscalew = int(World.SPOT_SIZE / self.height)
		#catscaleh = int(World.SPOT_SIZE / self.height)
		catscalew = math.ceil(World.SPOT_SIZE / self.height)
		catscaleh = math.ceil(World.SPOT_SIZE / self.height)		

		vcx1 = int(wx1/World.SPOT_SIZE) - 1
		#if vcx1 < 0:
		#	vcx1 = 0

		vcy1 = int(wy1/World.SPOT_SIZE) - 1
		#if vcy1 < 0:
		#	vcy1 = 0
		vcx2 = int(wx2/World.SPOT_SIZE) + 1
		#if vcx2 > nox:
		#	vcx2 = nox
		vcy2 = int(wy2/World.SPOT_SIZE) + 1
		#if vcy2 > noy:
		#	vcy2 = noy

		self.worldx1_S = vcx1
		self.worldy1_S = vcy1
		self.worldx2_S = vcx2
		self.worldy2_S = vcy2


		if (self.worldx != self.worldx_old) or (self.worldy != self.worldy_old) or (self.height != self.height_old):
			self.worldx_old = self.worldx
			self.worldy_old = self.worldy
			self.height_old = self.height
			self.redrawNecessary = True
			#self.updateMatrixPosition = 0


		#if self.redrawNecessary:
		#	drawrounds = int(3+30-((self.height / self.maxHeight)*30))
		#	drawrounds = int(3+len(self.updateMatrix)-((self.height / self.maxHeight)*len(self.updateMatrix)))
		#else:
		#	drawrounds = 1


		drawrounds = self.maxdrawrounds

		starttime = time_ns()
		for drawround in range(0,drawrounds):


			self.updateMatrixPosition += 1
			if self.updateMatrixPosition >= len(self.updateMatrix):
				self.updateMatrixPosition = 0
				self.redrawNecessary = False



			for caty in range(vcy1,vcy2):
				for catx in range(vcx1,vcx2):

					#if random.random() < 0.7:
					#	continue
					#pos = caty*nox+catx

					#if not  self.redrawNecessary:
					#	continue

					# respect the update Matrix except when it's the selected image, this is always drawn
					if (self.selection.x_S != catx or self.selection.y_S != caty) and (catx%self.updateMatrixSideLength,caty%self.updateMatrixSideLength) != self.updateMatrix[self.updateMatrixPosition]:
						continue

					self.drawnPositions[(catx,caty)] = 0

					catworldposx = catx*World.SPOT_SIZE
					catworldposy = caty*World.SPOT_SIZE


					catscreenx = int((catworldposx - wx1) / self.height)
					catscreeny = int((catworldposy - wy1) / self.height)




					frame = self.world.getFrameAt_S(catx,caty)

					if frame == None:
						#pygame.draw.rect(display, (26,26,29), (catscreenx,catscreeny,catscalew+1,catscaleh+1))
						pygame.draw.rect(display, (26,26,29), (catscreenx,catscreeny,catscalew,catscaleh))
						
						#r = 0
						#b = random.randint(-25,9)
						#pygame.draw.rect(display, (3,0,29+b), (catscreenx,catscreeny,catscalew+1,catscaleh+1))
						continue

					image = frame.image

					if image == None or (image.state != StreamedImage.STATE_READY and image.state != StreamedImage.STATE_READY_AND_RELOADING):
						pygame.draw.rect(display, (111,34,50), (catscreenx,catscreeny,catscalew+1,catscaleh+1))
						continue



					if image.state == StreamedImage.STATE_READY or image.state == StreamedImage.STATE_READY_AND_RELOADING:


						#       x
						#    1---->2
						#if catworldposx+catscalew > wx1 and catworldposx < wx2 and catworldposy+catscaleh > wy1 and catworldposy < wy2:
						if catworldposx+World.SPOT_SIZE > wx1 and catworldposx < wx2 and catworldposy+World.SPOT_SIZE > wy1 and catworldposy < wy2:


							if image.drawnworldx == self.worldx and image.drawnworldy == self.worldy and image.drawnheight == self.height and image.drawntoken == self.redrawtoken:
								continue

							image.drawnworldx = self.worldx
							image.drawnworldy = self.worldy
							image.drawnheight = self.height
							image.drawntoken = self.redrawtoken



							#display.blit(self.manycats[pos].getScaledSurface(),(catscreenx,catscreeny))


							drww = catscalew
							drww_offset = 0
							drwh = catscaleh
							drwh_offset = 0

							if image.aspectRatio < 1.0:
								drwh = int(catscaleh * image.aspectRatio)
								drwh_offset = int((catscaleh - drwh) / 2)
							else:
								drww = int(catscalew / image.aspectRatio)
								drww_offset = int((catscalew - drww) / 2)

							#pygame.draw.rect(display, image.averageColor, (catscreenx,catscreeny,catscalew+1,catscaleh+1))
							pygame.draw.rect(display, image.averageColor, (catscreenx,catscreeny,catscalew,catscaleh))
							if catscalew < 16:
								pass
								#pygame.draw.rect(display, self.manycats[pos].averageColor, (catscreenx,catscreeny,drww,drwh))
							elif catscalew <= 32:
								surface = image.getSurface(StreamedImage.QUALITY_THUMB)
								#if surface != None:
								cat2 = pygame.transform.scale(surface, (drww,drwh))
								display.blit(cat2,(catscreenx+drww_offset,catscreeny+drwh_offset))
								self.performance_imagesDrawn = self.performance_imagesDrawn + 1
							else:
								surface = image.getSurface()
								#if surface != None:
								cat2 = pygame.transform.scale(surface, (drww,drwh))
								display.blit(cat2,(catscreenx+drww_offset,catscreeny+drwh_offset))
								self.performance_imagesDrawn = self.performance_imagesDrawn + 1


		elapsedtime = int((time_ns() - starttime) / 1000000)

		newmaxdrawrounds = 1

		perround = elapsedtime / self.maxdrawrounds
		if perround < 1:
			perround = 1
		fps = 10
		newmaxdrawrounds = int((1000 / fps) / perround)
		if newmaxdrawrounds < 1:
			newmaxdrawrounds = 1

		self.maxdrawroundsqueue.append(newmaxdrawrounds)
		self.maxdrawroundsqueue.pop(0)

		self.maxdrawrounds = int(sum(self.maxdrawroundsqueue) / len(self.maxdrawroundsqueue))


		if self.maxdrawrounds < 1:
			self.maxdrawrounds = 1



		'''
		if (elapsedtime < (1000 / (fps + 1))):
			self.maxdrawrounds += 1
		elif (elapsedtime > (1000 / fps)):
			#self.maxdrawrounds = int (self.maxdrawrounds / 2)
			#self.maxdrawrounds -= 1
			self.maxdrawrounds -= int(elapsedtime / (1000 / fps))
			if self.maxdrawrounds < 1:
				self.maxdrawrounds = 1
		'''	

		#print(self.maxdrawrounds)

		if self.drawGrid:

			gridstep = World.SPOT_SIZE

			gridStartx = math.floor(wx1 / gridstep) * gridstep


			for gridx in range(gridStartx, wx2, gridstep):
				gx = int((gridx - wx1) / self.height)
				c = (80,0,0)
				if (gridx / gridstep) % World.CHUNK_SIZE == 0:
					c = (128,128,128)
					pygame.draw.line(display, c, (gx,y), (gx,y+h))


			gridStarty = math.floor(wy1 / gridstep) * gridstep

			for gridy in range(gridStarty, wy2, gridstep):
				gy = int((gridy - wy1) / self.height)
				c = (80,0,0)
				if (gridy / gridstep) % World.CHUNK_SIZE == 0:
					c = (128,128,128)
					pygame.draw.line(display, c, (x,gy), (x+w,gy))

		'''
		if self.height >= World.SPOT_SIZE / ImageServer.QUALITY_PIXEL_SIZE[StreamedImage.QUALITY_GRID]:

			# draw crosshair

			chl = 20 # crosshairlength
			x1 = int(w/2)-chl+x
			x2 = int(w/2)+chl+x
			y1 = int(h/2)+y
			pygame.draw.line(display, (255,0,0), (x1,y1), (x2,y1))

			y1 = int(h/2)-chl+y
			y2 = int(h/2)+chl+y
			x1 = int(w/2)+x
			pygame.draw.line(display, (255,0,0), (x1,y1), (x1,y2))
		'''



		if self.selection.isVisible():

			selworldposx = self.selection.x_S*World.SPOT_SIZE
			selworldposy = self.selection.y_S*World.SPOT_SIZE


			catscreenx = int((selworldposx - wx1) / self.height)
			catscreeny = int((selworldposy - wy1) / self.height)

			thick = 3 + int(6.0 * ( 1.0 - (self.height / self.maxHeight)))

			self.selection.colormix += 20

			if self.selection.colormix > 200:
				self.selection.colormix = -200
			g = abs(self.selection.colormix)
			b = abs(self.selection.colormix) + 127
			if b > 255:
				b = 255
			pygame.draw.rect(display, (255,g,b), (catscreenx-thick+1,catscreeny-thick+1,catscalew+thick+thick-1,catscaleh+thick+thick), thick,thick)


			self.selection.updateSelectedSpot()

			# peek

			peekSize = 300
			if self.selection.peekEnabled and peekSize > (World.SPOT_SIZE / self.height):

				#frame = self.world.getFrameAt_S(self.selection.x_S,self.selection.y_S)
				#if frame != None:
					#image = frame.image
				image = self.selection.image
				if image != None:
					if image.state == StreamedImage.STATE_READY or image.state == StreamedImage.STATE_READY_AND_RELOADING:

						peekw = peekSize
						peekh = peekSize

						drww = peekw
						drwh = peekh

						if image.aspectRatio < 1.0:
							drwh = int(peekh * image.aspectRatio)
						else:
							drww = int(peekw / image.aspectRatio)

						surface = image.getSurface()
						cat2 = pygame.transform.scale(surface, (drww,drwh))
						display.blit(cat2,(catscreenx + catscalew + (thick * 2),catscreeny))
						self.performance_imagesDrawn = self.performance_imagesDrawn + 1


						pygame.draw.rect(display, (255,g,b), (catscreenx+catscalew + thick ,catscreeny - thick,drww+thick+thick,drwh+thick+thick), thick,thick)
