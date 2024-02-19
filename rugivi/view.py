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
from pygame.surface import Surface

from .world_things.frame import Frame

from .world_things.world import *
#from .image_server import *
from .image_service.abstract_streamed_media import AbstractStreamedMedia
from .selection import *
import random
from time import time_ns
import math

class View:
	def __init__(self, world: World, initial_height : float) -> None:
		self.current_center_world_pos_x_P = 0
		self.current_center_world_pos_y_P = 0
		self.height = initial_height
		self.max_height = 1400
		self.old_center_world_pos_x_P = 0
		self.old_center_world_pos_y_P = -1
		self.old_height = self.height

		self.world_x1_S = 0
		self.world_y1_S = 0
		self.world_x2_S = 0
		self.world_y2_S = 0

		self.performance_images_drawn = 0

		self.world = world

		self.selection: Selection = Selection(world, self)

		self.redrawtoken = 0

		self.update_matrix = []

		self.draw_grid = True

		self.update_matrix_side_length = 4
		self.update_matrix_side_length = 6
		for y in range(0, self.update_matrix_side_length):
			for x in range(0, self.update_matrix_side_length):
				self.update_matrix.append((x, y))

		random.shuffle(self.update_matrix)

		self.update_matrix_position = 0

		self.max_draw_rounds = 1
		self.max_draw_rounds_queue = [1, 1, 1, 1, 1]

	def draw_view(
		self, display, view_surface_top_x, view_surface_top_y, view_width, view_height
	) -> None:
		#
		# Addressing methods:
		# 	pixel		_P
		# 	spot		_S
		# 	chunk		_C
		#   chunk+spot	_CS
		# 				    +L local (eg chunk)
		#
		#  ------------view_width------------
		#  |
		#  |
		#  view_height
		#  |
		#  |
		#  |------------------------
		#
		#   world_x1_P,world_y1_P
		#
		#
		# 			self.current_center_world_pos_x_P,self.current_center_world_pos_y_P
		# 			+ height
		#
		#
		#                       world_x2_P,world_y2_P

		world_x1_P = self.current_center_world_pos_x_P - int(
			(view_width / 2) * self.height
		)
		world_y1_P = self.current_center_world_pos_y_P - int(
			(view_height / 2) * self.height
		)
		world_x2_P = self.current_center_world_pos_x_P + int(
			(view_width / 2) * self.height
		)
		world_y2_P = self.current_center_world_pos_y_P + int(
			(view_height / 2) * self.height
		)

		self.performance_images_drawn = 0

		spot_width_P = math.ceil(World.SPOT_SIZE / self.height)
		spot_height_P = math.ceil(World.SPOT_SIZE / self.height)

		self.world_x1_S = int(world_x1_P / World.SPOT_SIZE) - 1
		self.world_y1_S = int(world_y1_P / World.SPOT_SIZE) - 1
		self.world_x2_S = int(world_x2_P / World.SPOT_SIZE) + 1
		self.world_y2_S = int(world_y2_P / World.SPOT_SIZE) + 1

		if (
			(self.current_center_world_pos_x_P != self.old_center_world_pos_x_P)
			or (self.current_center_world_pos_y_P != self.old_center_world_pos_y_P)
			or (self.height != self.old_height)
		):
			self.old_center_world_pos_x_P = self.current_center_world_pos_x_P
			self.old_center_world_pos_y_P = self.current_center_world_pos_y_P
			self.old_height = self.height

		drawrounds = self.max_draw_rounds

		start_time = time_ns()
		for drawround in range(0, drawrounds):

			self.update_matrix_position += 1
			if self.update_matrix_position >= len(self.update_matrix):
				self.update_matrix_position = 0

			for current_spot_y_S in range(self.world_y1_S, self.world_y2_S):
				for current_spot_x_S in range(self.world_x1_S, self.world_x2_S):

					# respect the update Matrix except when it's the selected image, this is always drawn
					if (
						self.selection.x_S != current_spot_x_S
						or self.selection.y_S != current_spot_y_S
					) and (
						current_spot_x_S % self.update_matrix_side_length,
						current_spot_y_S % self.update_matrix_side_length,
					) != self.update_matrix[
						self.update_matrix_position
					]:
						continue

					current_world_pos_x_P = current_spot_x_S * World.SPOT_SIZE
					current_world_pos_y_P = current_spot_y_S * World.SPOT_SIZE

					current_screen_x_PL = int(
						(current_world_pos_x_P - world_x1_P) / self.height
					)
					current_screen_y_PL = int(
						(current_world_pos_y_P - world_y1_P) / self.height
					)

					frame: Frame = self.world.get_frame_at_S(
						current_spot_x_S, current_spot_y_S
					)

					if frame == None:
						pygame.draw.rect(
							display,
							(26, 26, 29),
							(
								current_screen_x_PL,
								current_screen_y_PL,
								spot_width_P,
								spot_height_P,
							),
						)
						continue

					image: AbstractStreamedMedia = frame.image  # type: ignore

					if image == None or (
						image.state != AbstractStreamedMedia.STATE_READY
						and image.state != AbstractStreamedMedia.STATE_READY_AND_RELOADING
					):
						pygame.draw.rect(
							display,
							(111, 34, 50),
							(
								current_screen_x_PL,
								current_screen_y_PL,
								spot_width_P + 1,
								spot_height_P + 1,
							),
						)
						continue

					if (
						image.state == AbstractStreamedMedia.STATE_READY
						or image.state == AbstractStreamedMedia.STATE_READY_AND_RELOADING
					):

						if (
							current_world_pos_x_P + World.SPOT_SIZE > world_x1_P
							and current_world_pos_x_P < world_x2_P
							and current_world_pos_y_P + World.SPOT_SIZE > world_y1_P
							and current_world_pos_y_P < world_y2_P
						):

							if (
								image.drawn_view_world_x_P
								== self.current_center_world_pos_x_P
								and image.drawn_view_world_y_P
								== self.current_center_world_pos_y_P
								and image.drawn_view_height == self.height
								and image.drawn_view_token == self.redrawtoken
							):
								continue

							image.drawn_view_world_x_P = (
								self.current_center_world_pos_x_P
							)
							image.drawn_view_world_y_P = (
								self.current_center_world_pos_y_P
							)
							image.drawn_view_height = self.height
							image.drawn_view_token = self.redrawtoken

							image_drawing_width_P = spot_width_P
							image_offset_x_P = 0
							image_drawing_height_P = spot_height_P
							image_offset_y_P = 0

							if image.aspect_ratio < 1.0:
								image_drawing_height_P = int(
									spot_height_P * image.aspect_ratio
								)
								image_offset_y_P = int(
									(spot_height_P - image_drawing_height_P) / 2
								)
							else:
								image_drawing_width_P = int(
									spot_width_P / image.aspect_ratio
								)
								image_offset_x_P = int(
									(spot_width_P - image_drawing_width_P) / 2
								)

							pygame.draw.rect(
								display,
								image.average_color,
								(
									current_screen_x_PL,
									current_screen_y_PL,
									spot_width_P,
									spot_height_P,
								),
							)
							if spot_width_P < 5:
								pass
							
							elif spot_width_P <= 32:
								surface :Surface = image.get_surface(AbstractStreamedMedia.QUALITY_THUMB) # type: ignore

								if surface != None:
									scaled_image_surface = pygame.transform.smoothscale(
										surface,
										(image_drawing_width_P, image_drawing_height_P),
									)
									display.blit(
										scaled_image_surface,
										(
											current_screen_x_PL + image_offset_x_P,
											current_screen_y_PL + image_offset_y_P,
										),
									)
									self.performance_images_drawn = (
										self.performance_images_drawn + 1
									)
							else:
								surface :Surface = image.get_surface() # type: ignore
								if surface != None:
									# only smoothscale to small destination size, big dest. sizes take too long
									if spot_width_P < 256: # TODO hard coded pixels
										scaled_image_surface = pygame.transform.smoothscale(
											surface,
											(image_drawing_width_P, image_drawing_height_P),
										)
									else:
										scaled_image_surface = pygame.transform.scale(
											surface,
											(image_drawing_width_P, image_drawing_height_P),
										)
									display.blit(
										scaled_image_surface,
										(
											current_screen_x_PL + image_offset_x_P,
											current_screen_y_PL + image_offset_y_P,
										),
									)
									self.performance_images_drawn = (
										self.performance_images_drawn + 1
									)

		elapsed_time = int((time_ns() - start_time) / 1000000)

		new_max_draw_rounds = 1

		per_round = elapsed_time / self.max_draw_rounds
		if per_round < 1:
			per_round = 1
		fps = 15
		new_max_draw_rounds = int((1000 / fps) / per_round)
		if new_max_draw_rounds < 1:
			new_max_draw_rounds = 1

		self.max_draw_rounds_queue.append(new_max_draw_rounds)
		self.max_draw_rounds_queue.pop(0)

		self.max_draw_rounds = int(
			sum(self.max_draw_rounds_queue) / len(self.max_draw_rounds_queue)
		)

		if self.max_draw_rounds < 1:
			self.max_draw_rounds = 1

		if self.draw_grid:

			grid_step = World.SPOT_SIZE

			grid_start_x_P = math.floor(world_x1_P / grid_step) * grid_step

			for grid_x_P in range(grid_start_x_P, world_x2_P, grid_step):
				grid_x_PL = int((grid_x_P - world_x1_P) / self.height)
				grid_color = (80, 0, 0)
				if (grid_x_P / grid_step) % World.CHUNK_SIZE == 0:
					grid_color = (128, 128, 128)
					pygame.draw.line(
						display,
						grid_color,
						(grid_x_PL, view_surface_top_y),
						(grid_x_PL, view_surface_top_y + view_height),
					)

			grid_start_y_P = math.floor(world_y1_P / grid_step) * grid_step

			for grid_y_P in range(grid_start_y_P, world_y2_P, grid_step):
				grid_y_PL = int((grid_y_P - world_y1_P) / self.height)
				grid_color = (80, 0, 0)
				if (grid_y_P / grid_step) % World.CHUNK_SIZE == 0:
					grid_color = (128, 128, 128)
					pygame.draw.line(
						display,
						grid_color,
						(view_surface_top_x, grid_y_PL),
						(view_surface_top_x + view_width, grid_y_PL),
					)

		if self.selection.is_visible():

			selection_world_pos_x_P = self.selection.x_S * World.SPOT_SIZE
			selection_world_pos_y_P = self.selection.y_S * World.SPOT_SIZE

			current_screen_x_PL = int(
				(selection_world_pos_x_P - world_x1_P) / self.height
			)
			current_screen_y_PL = int(
				(selection_world_pos_y_P - world_y1_P) / self.height
			)

			thickness = 3 + int(6.0 * (1.0 - (self.height / self.max_height)))

			self.selection.colormix += 20

			if self.selection.colormix > 200:
				self.selection.colormix = -200
			green = abs(self.selection.colormix)
			blue = abs(self.selection.colormix) + 127
			if blue > 255:
				blue = 255
			pygame.draw.rect(
				display,
				(255, green, blue),
				(
					current_screen_x_PL - thickness + 1,
					current_screen_y_PL - thickness + 1,
					spot_width_P + thickness + thickness - 1,
					spot_height_P + thickness + thickness,
				),
				thickness,
				thickness,
			)

			self.selection.update_selected_spot()

			# peek

			peek_size = 300
			if self.selection.peek_enabled and peek_size > (
				World.SPOT_SIZE / self.height
			):

				image = self.selection.image
				if image != None:
					if (
						image.state == AbstractStreamedMedia.STATE_READY
						or image.state == AbstractStreamedMedia.STATE_READY_AND_RELOADING
					):

						peek_width_P = peek_size
						peek_height_P = peek_size

						image_drawing_width_P = peek_width_P
						image_drawing_height_P = peek_height_P

						if image.aspect_ratio < 1.0:
							image_drawing_height_P = int(
								peek_height_P * image.aspect_ratio
							)
						else:
							image_drawing_width_P = int(
								peek_width_P / image.aspect_ratio
							)

						surface: pygame.surface.Surface = image.get_surface() # type: ignore
						if surface != None:
							scaled_image_surface = pygame.transform.smoothscale(
								surface, (image_drawing_width_P, image_drawing_height_P)
							)
							display.blit(
								scaled_image_surface,
								(
									current_screen_x_PL + spot_width_P + (thickness * 2),
									current_screen_y_PL,
								),
							)
							self.performance_images_drawn = (
								self.performance_images_drawn + 1
							)

						pygame.draw.rect(
							display,
							(255, green, blue),
							(
								current_screen_x_PL + spot_width_P + thickness,
								current_screen_y_PL - thickness,
								image_drawing_width_P + thickness + thickness,
								image_drawing_height_P + thickness + thickness,
							),
							thickness,
							thickness,
						)
