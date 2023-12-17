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

import pygame

class Status:


	def __init__(self, fontsize=12):
		self.fontsize = fontsize
		self.blackwidth = int(400 * (fontsize / 12))
		self.font = pygame.font.SysFont("monospace",fontsize)
		self.lines = []



	def writeln(self, line):
		self.lines.append(line)


	def draw(self, display):
		px = 10
		py = 10
		for line in self.lines:
			#text_surf = self.font.render(line, False, (255, 255, 255)).convert()
			#text_with_ouline = self.add_outline_to_image(text_surf, 5, (0, 255, 0))
			#display.blit(text_with_ouline, (10, py))


			#text = self.font.render(line, False, (0,0,0)).convert()

			#for x in range(px-4, px+4):
			#	for y in range(py-4,py+4):
			#		display.blit(text, (x, y))



			text = self.font.render(line, True, (0, 0, 0))


			w = text.get_size()[0]
			h = text.get_size()[1]
			if w < self.blackwidth:
				w = self.blackwidth
			temp_surface = pygame.Surface((w,h))
			#temp_surface.fill((26,26,26))
			temp_surface.fill((100,100,100))
			temp_surface.blit(text, (0, 0))
			display.blit(temp_surface, (px,py))


			#display.blit(text, (px, py))

			py = py + self.fontsize
		self.lines = []

