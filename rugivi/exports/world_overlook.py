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

import threading
from PIL import Image

from time import sleep, time

from ..world_things.world import *
from rugivi import dir_helper as dir_helper
from ..image_service.image_server import *


class WorldOverlook:

	ANALYSIS_STATUS_NONE = "none"
	ANALYSIS_STATUS_RUNNING = "running"
	ANALYSIS_STATUS_DONE = "done"

	def __init__(self, world, filename: str) -> None:
		self.world: World = world
		self.filename: str = filename
		self.analysis_status = WorldOverlook.ANALYSIS_STATUS_NONE
		self.status = ""

	def _analyze_world(self) -> None:
		if self.analysis_status != WorldOverlook.ANALYSIS_STATUS_NONE:
			return

		self.analysis_status = WorldOverlook.ANALYSIS_STATUS_RUNNING

		self.max_x_C = 0
		self.max_y_C = 0
		self.min_x_C = 0
		self.min_y_C = 0

		chunk_stack = [self.world.get_chunk_at_C(0, 0)]
		visited_chunks = []
		while len(chunk_stack) > 0:
			current_chunk: Chunk = chunk_stack.pop()
			self.set_status(
				"Analysing Chunk:"
				+ str(current_chunk.x_C)
				+ ","
				+ str(current_chunk.y_C)
				+ " Stack Size:"
				+ str(len(chunk_stack))
				+ " Visited Size:"
				+ str(len(visited_chunks))
			)

			visited_chunks.append(current_chunk)

			if current_chunk.x_C > self.max_x_C:
				self.max_x_C = current_chunk.x_C
			if current_chunk.y_C > self.max_y_C:
				self.max_y_C = current_chunk.y_C
			if current_chunk.x_C < self.min_x_C:
				self.min_x_C = current_chunk.x_C
			if current_chunk.y_C < self.min_y_C:
				self.min_y_C = current_chunk.y_C

			for x in range(current_chunk.x_C - 1, current_chunk.x_C + 2):
				for y in range(current_chunk.y_C - 1, current_chunk.y_C + 2):
					if current_chunk.x_C == x and current_chunk.y_C == y:
						continue
					neighbourChunk = self.world.get_chunk_at_C(x, y)
					if neighbourChunk in visited_chunks:
						continue
					if neighbourChunk.is_empty():
						visited_chunks.append(neighbourChunk)
						continue
					chunk_stack.append(neighbourChunk)

		print("World size in chunks:")
		print("X:", self.min_x_C, "to", self.max_x_C)
		print("Y:", self.min_y_C, "to", self.max_y_C)

		self.analysis_status = WorldOverlook.ANALYSIS_STATUS_DONE

	def _export_as_image(self):
		size_x_C = self.max_x_C - self.min_x_C + 1
		size_y_C = self.max_y_C - self.min_y_C + 1

		offset_x_S = self.min_x_C * World.CHUNK_SIZE * -1
		offset_y_S = self.min_y_C * World.CHUNK_SIZE * -1

		world_image = Image.new(
			"RGB", (size_x_C * World.CHUNK_SIZE, size_y_C * World.CHUNK_SIZE)
		)

		loader_stack = []

		self.set_status("Parsing all frames...")
		for x_S in range(
			self.min_x_C * World.CHUNK_SIZE, (self.max_x_C + 1) * World.CHUNK_SIZE
		):
			for y_S in range(
				self.min_y_C * World.CHUNK_SIZE, (self.max_y_C + 1) * World.CHUNK_SIZE
			):
				frame = self.world.get_frame_at_S(x_S, y_S)
				if frame != None:
					loader_stack.append(frame)
			sleep(0.002)
			if not self.running:
				return

		status_next = 10000
		pause_every = 100
		while len(loader_stack) > 0:
			frame: Frame = loader_stack.pop(0)
			image = frame.image
			if image != None:
				if (
					image.state == StreamedImage.STATE_READY
					or image.state == StreamedImage.STATE_READY_AND_RELOADING
				):

					color = image.average_color

					world_image.putpixel(
						(frame.x_S + offset_x_S, frame.y_S + offset_y_S), color
					)

				elif image.state == StreamedImage.STATE_ERROR_ON_LOAD:
					pass
				else:
					loader_stack.append(frame)

			pause_every -= 1
			if pause_every < 1:
				pause_every = 100
				sleep(0.01)

			status_next -= 1

			if status_next < 1:
				self.set_status("Remaining Thumbs: " + str(len(loader_stack)))
				status_next = 10000
				sleep(1)  # let the image server have time to load more
				world_image.save(self.filename, "PNG")

			if not self.running:
				break
		world_image.save(self.filename, "PNG")
		self.set_status("finished")

	def run(self):
		self.running = True
		self.thread = threading.Thread(target=self.world_overlook_loop, args=())
		self.thread.daemon = True  # so these threads get killed when program exits
		self.thread.start()

	def world_overlook_loop(self):

		self.world_overlook_loop_running = True
		print("WorldOverlook started")

		self._analyze_world()
		self._export_as_image()
		self.running = False

		print("WorldOverlook loop exited")
		self.world_overlook_loop_running = False

	def stop(self):
		self.running = False

		while self.world_overlook_loop_running:
			sleep(0.06)

	def set_status(self, status):
		self.status = status
		print("World Overlook:", status)
