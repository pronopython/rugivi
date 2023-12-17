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
from rugivi.fap_table.fap_table import FapTable
from rugivi.image_service.streamed_image import StreamedImage
from rugivi.image_service.image_server import *


class FapTableView:
	def __init__(self) -> None:

		self.fap_table: FapTable = None  # type: ignore

		self.edit_mode_enabled = False

		self.colormix = 0

		self.real_x = 0
		self.real_y = 0
		self.real_w = 0
		self.real_h = 0
		self.card_step_per_pixel = 0.1

	def set_current_fap_table(self, fapTable) -> None:
		if self.fap_table != None:
			self.fap_table.is_displayed = False
		self.fap_table = fapTable
		if self.fap_table != None:
			self.fap_table.is_displayed = True

	def get_card_at_pixel_pos(self, x, y):
		for card in self.fap_table.cards:
			image: AbstractStreamedMedia = card.image
			if image != None and (
				image.state == StreamedImage.STATE_READY
				or image.state == StreamedImage.STATE_READY_AND_RELOADING
			):
				real_x1 = int((card.x * self.real_w) + self.real_x)
				real_y1 = int((card.y * self.real_w) + self.real_y)

				real_x2 = int(((card.x + card.width) * self.real_w) + self.real_x)
				real_y2 = int(
					((card.y + (card.width * card.image.aspect_ratio)) * self.real_w)
					+ self.real_y
				)

				if real_x1 <= x and real_x2 >= x and real_y1 <= y and real_y2 >= y:
					return card
		return None

	def is_card_lower_corner(self, card, x, y):
		image: AbstractStreamedMedia = card.image
		if image != None and (
			image.state == StreamedImage.STATE_READY
			or image.state == StreamedImage.STATE_READY_AND_RELOADING
		):
			real_x1 = int((card.x * self.real_w) + self.real_x)
			real_y1 = int((card.y * self.real_w) + self.real_y)

			real_x2 = int(((card.x + card.width) * self.real_w) + self.real_x)
			real_y2 = int(
				((card.y + (card.width * card.image.aspect_ratio)) * self.real_w)
				+ self.real_y
			)

			if (
				real_x2 - 10 <= x
				and real_x2 >= x
				and real_y2 - 10 <= y
				and real_y2 >= y
			):
				return True
		return False

	def draw_fap_table_view(self, display, x, y, w, h):

		self.real_x = x
		self.real_y = y
		self.real_w = w
		self.real_h = h
		self.card_step_per_pixel = 1.0 / w

		if self.fap_table != None:

			for card in self.fap_table.cards:
				image: AbstractStreamedMedia = card.image
				if image != None and (
					image.state == StreamedImage.STATE_READY
					or image.state == StreamedImage.STATE_READY_AND_RELOADING
				):
					real_x1 = int((card.x * w) + x)
					real_y1 = int((card.y * w) + y)

					real_x2 = int(((card.x + card.width) * w) + x)
					real_y2 = int(
						((card.y + (card.width * image.aspect_ratio)) * w) + y
					)

					surface : pygame.surface.Surface = image.get_surface() # type: ignore
					cat2 = pygame.transform.scale(
						surface, (real_x2 - real_x1, real_y2 - real_y1)
					)

					display.blit(cat2, (real_x1, real_y1))

					# draw selections
					if self.edit_mode_enabled:
						self.colormix += 20

						if self.colormix > 200:
							self.colormix = -200
						g = abs(self.colormix)
						b = abs(self.colormix) + 127
						if b > 255:
							b = 255
						pygame.draw.rect(
							display,
							(255, g, b),
							(real_x1, real_y1, real_x2 - real_x1, real_y2 - real_y1),
							1,
							1,
						)
						pygame.draw.rect(
							display,
							(255, g, b),
							(real_x2 - 10, real_y2 - 10, 10, 10),
							1,
							1,
						)
