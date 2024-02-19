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

import hashlib
import math
import os
from typing import NoReturn
import pygame

import threading
from time import sleep, time
from queue import Queue

from rugivi.fap_table.fap_table import FapTable
from rugivi.image_service.image_cache import ImageCache
from rugivi.image_service.streamed_mockup import StreamedMockup
from rugivi.image_service.video_still_generator import VideoStillGenerator
from .abstract_streamed_media import AbstractStreamedMedia

from .streamed_image import StreamedImage

from ..world_things.chunk import Chunk
from ..thread_safe_list import *
from ..view import View
from ..world_things.world import *
from ..image_database_service.image_server_database import *


class ImageServerConduit:
	def __init__(self, name, image_server) -> None:
		self.name = name
		self.thread: threading.Thread = None  # type: ignore
		self.media: AbstractStreamedMedia = None  # type: ignore
		self.waiting = True
		self.image_server: ImageServer = image_server
		self.image_server_database: ImageServerDatabase = None  # type: ignore
		self.video_still_generator: VideoStillGenerator = None  # type: ignore
		self.image_cache: ImageCache = None  # type: ignore

	def conduit_loader_loop(self) -> NoReturn:
		original_surface: pygame.surface.Surface = None  # type: ignore
		while True:
			sleep(0.01)

			if not self.waiting and self.media != None:

				if (
					self.media.state == StreamedImage.STATE_NEW
					or self.media.state == StreamedImage.STATE_READY_AND_RELOADING
				):

					# only when thumb not already available (on reload job) AND ordered == thumb and not higher!!!
					if (
						self.media.get_available_quality() < StreamedImage.QUALITY_THUMB
						and self.media.get_ordered_quality()
						<= StreamedImage.QUALITY_THUMB
					):

						if self.image_server_database != None:
							image_proxy = (
								self.image_server_database.get_image_proxy_by_path(
									self.media.original_file_path
								)
							)
							if image_proxy != None:

								self.media.width = image_proxy.width
								self.media.height = image_proxy.height
								self.media.aspect_ratio = image_proxy.aspect_ratio
								self.media.bytes_per_pixel = image_proxy.bytes_per_pixel
								self.media._surfaces[StreamedImage.QUALITY_THUMB][
									StreamedImage.SURFACE_SURFACE
								] = image_proxy.image_surface
								self.media._surfaces[StreamedImage.QUALITY_THUMB][
									StreamedImage.SURFACE_BYTES
								] = (
									image_proxy.thumb_width
									* image_proxy.thumb_height
									* self.media.bytes_per_pixel
								)

								self.media.average_color = image_proxy.average_color

								self.image_server._total_database_loaded += 1
								self.waiting = True
								self.media.drawn_view_height = -1
								self.media._available_quality = (
									StreamedImage.QUALITY_THUMB
								)
								self.media.state = StreamedImage.STATE_READY

				if not self.waiting and (
					self.media.state == StreamedImage.STATE_NEW
					or self.media.state == StreamedImage.STATE_READY_AND_RELOADING
				):

					# image is a surrogate for a video file
					if self.media.get_extended_attribute("video_still_uuid") != None:
						# print("Creating cached file for",self.media.get_extended_attribute("video_file"))
						uuid_name = self.media.get_extended_attribute(
							"video_still_uuid"
						)

						if not self.image_cache.file_exists(uuid_name):

							# cache miss, create a video still frame

							# The cache name was already generated through the crawler (along with the uuid),
							# so that the image already has original_file_path set to the cache file (the
							# surrogate file).
							# Here it is *again* calculated, to make absolutly sure that cache_filename
							# will *always* contain a cache-dir filename. Writing over
							# original_file_path can destroy original collection images if somehow
							# there is a bug.
							cache_filename = self.image_cache.get_filename_for_uuid(
								uuid_name
							)
							self.image_cache.generate_path_for_uuid(
								uuid_name
							)  # make sure path exists
							video_still_created = (
								self.video_still_generator.create_and_write_still_image(
									self.media.get_extended_attribute("video_file"),
									self.media.get_extended_attribute("video_position"),
									cache_filename,
								)
							)
							if video_still_created:
								self.media.original_file_path = cache_filename
							else:
								self.media.state = StreamedImage.STATE_ERROR_ON_LOAD
								self.waiting = True

					if self.media.state != StreamedImage.STATE_ERROR_ON_LOAD:

						# load image from disk

						try:
							original_surface = pygame.image.load(
								self.media.original_file_path
							).convert()

							self.media.state = StreamedImage.STATE_LOADED

							self.image_server._total_disk_loaded += 1
						except pygame.error as message:
							print(
								"Conduit " + str(self.name) + " cannot load ",
								self.media.original_file_path,
							)
							self.media.state = StreamedImage.STATE_ERROR_ON_LOAD
							self.waiting = True
						except FileNotFoundError as e:
							print(
								"Conduit " + str(self.name) + " cannot load ",
								self.media.original_file_path,
							)
							self.media.state = StreamedImage.STATE_ERROR_ON_LOAD
							self.waiting = True

				if not self.waiting and self.media.state == StreamedImage.STATE_LOADED:
					# gather info
					self.media.width, self.media.height = original_surface.get_size()
					self.media.aspect_ratio = self.media.height / self.media.width
					self.media.bytes_per_pixel = original_surface.get_bytesize()

					# QUALITY_COLOR
					self.media.average_color = pygame.transform.average_color(original_surface)  # type: ignore

					# TODO change load + available quality based on size of image (e.g. image smaller than ordered "screen" size => keep original

					# QUALITY_THUMB ... QUALITY_SCREEN
					if self.media._load_quality >= StreamedImage.QUALITY_THUMB:
						qmax = self.media._load_quality
						if qmax > StreamedImage.QUALITY_SCREEN:
							qmax = StreamedImage.QUALITY_SCREEN
						for q in range(0, qmax + 1):
							w = ImageServer.QUALITY_PIXEL_SIZE[q]
							h = int(w * self.media.aspect_ratio)
							self.media._surfaces[q][
								StreamedImage.SURFACE_SURFACE
							] = pygame.transform.smoothscale(original_surface, (w, h))
							self.media._surfaces[q][StreamedImage.SURFACE_BYTES] = (
								w * h * self.media.bytes_per_pixel
							)

					# QUALITY_ORIGINAL
					if self.media._load_quality == StreamedImage.QUALITY_ORIGINAL:
						self.media._surfaces[StreamedImage.QUALITY_ORIGINAL][
							StreamedImage.SURFACE_SURFACE
						] = original_surface
						self.media._surfaces[StreamedImage.QUALITY_ORIGINAL][
							StreamedImage.SURFACE_BYTES
						] = (
							self.media.width
							* self.media.height
							* self.media.bytes_per_pixel
						)
					original_surface = None  # type: ignore

					self.media._available_quality = self.media._load_quality

					if self.image_server_database != None:
						image_proxy = (
							self.image_server_database.get_image_proxy_by_path(
								self.media.original_file_path
							)
						)
						if (
							image_proxy == None
							and self.media.get_available_quality()
							>= StreamedImage.QUALITY_THUMB
						):
							self.image_server_database.add_image_thumb(self.media)  # type: ignore

					self.waiting = True
					self.media.drawn_view_height = -1
					self.media.state = StreamedImage.STATE_READY

				if self.media.state == StreamedImage.STATE_RESCALE:

					self.waiting = True
					self.media.state = StreamedImage.STATE_READY

	def run(self) -> None:
		self.thread = threading.Thread(target=self.conduit_loader_loop, args=())
		self.thread.daemon = True  # so these threads get killed when program exits
		self.thread.start()

	def is_busy(self) -> bool:
		return self.media != None

	def set_media(self, job) -> None:
		self.media = job
		self.waiting = False

	def is_running(self) -> bool:
		return self.thread.is_alive()

	def close(self) -> None:
		if not self.is_running():
			print("Close", self.name)
			self.thread.join()


class ImageServer:

	HOUSEKEEPING_EVERY_SECONDS = 300
	MEMCHECK_EVERY_SECONDS = 120
	HOUSEKEEPING_THRESHOLD = [-1, 5000, 150, 20]
	HOUSEKEEPING_MAX_MEM_MB_THRESHOLD = (
		2000  # TODO needs to be implemented, see further down
	)
	QUALITY_PIXEL_SIZE = [32, 128, 1000]  # thumb, grid, screen

	def __init__(
		self,
		number_of_conduits,
		thumbDbFile,
		cache_base_dir,
		number_of_video_conduits=-1,
	) -> None:
		self.conduits: list[ImageServerConduit] = []
		for c in range(0, number_of_conduits):
			self.conduits.append(ImageServerConduit(c, self))
		if number_of_video_conduits == -1:
			self.number_of_video_conduits = number_of_conduits
		else:
			self.number_of_video_conduits = number_of_video_conduits
		self.thread_loader = None
		self.thread_view_fetcher = None
		self.media_queue: Queue[AbstractStreamedMedia] = Queue()
		# self.surface_queue = Queue() TODO not used, right?
		self.streamed_images: ThreadSafeList = ThreadSafeList()
		self._bytes_used_total = 0

		self._bytes_used_sizes = [0, 0, 0, 0]
		self._surfaces_present = [0, 0, 0, 0]
		self._status_line = "---"
		self._total_disk_loaded = 0
		self._total_database_loaded = 0

		self.running = True
		self.loader_loop_running = False
		self.fetcher_loop_running = False

		self.views: list[View] = []
		self.fap_table_views = []

		self.paused = False

		self.image_cache = ImageCache(cache_base_dir)

		# self.video_still_generator = VideoStillGenerator(jpg_quality=65, max_dimension=(800,800),remove_letterbox=True)
		self.video_still_generator = VideoStillGenerator()
		# self.video_still_generator = VideoStillGenerator(jpg_quality=95,remove_letterbox=True)

		self.image_server_database = ImageServerDatabase(thumbDbFile)
		for conduit in self.conduits:
			conduit.image_server_database = self.image_server_database
			conduit.video_still_generator = self.video_still_generator
			conduit.image_cache = self.image_cache

	def start(self) -> None:
		for conduit in self.conduits:
			conduit.run()

		self.run()

	def server_loader_loop(self) -> None:

		next_housekeeping = time() + ImageServer.HOUSEKEEPING_EVERY_SECONDS
		next_memory_check = time()

		self.loader_loop_running = True
		while self.running:
			if self.media_queue.qsize() > 0:

				sleep(0.00001)
			else:
				sleep(0.1)

			for conduit in self.conduits:
				if conduit.is_busy():
					if conduit.media.state == StreamedImage.STATE_READY:
						conduit.media = None  # type: ignore
					elif conduit.media.state == StreamedImage.STATE_ERROR_ON_LOAD:
						conduit.media = None  # type: ignore

			if not self.paused:
				if self.media_queue.qsize() > 0:
					for conduit_number, conduit in enumerate(self.conduits):
						if not conduit.is_busy():
							media = self.media_queue.get()

							if (
								media.get_extended_attribute("video_still_uuid") != None
								and not self.image_cache.file_exists(
									media.get_extended_attribute("video_still_uuid")
								)
								and conduit_number >= self.number_of_video_conduits
							):
								self.media_queue.put(media)
								continue

							# TODO make dependend on ram
							media._load_quality = media._ordered_quality

							conduit.set_media(media)
							if self.media_queue.qsize() == 0:
								break

			housekeeping_now = False
			if next_memory_check < time() or next_housekeeping < time():
				next_memory_check = time() + ImageServer.MEMCHECK_EVERY_SECONDS
				self._calculate_memory_usage()

				if (
					self._bytes_used_total
					> ImageServer.HOUSEKEEPING_MAX_MEM_MB_THRESHOLD * 1024 * 1024
				):
					pass
					# housekeepingNow = True
					# TODO when more than MB RAM => panic if it will not go down after gc => then housekeeping IS ALWAYS RUNNING

				self.print_statistic()

			if next_housekeeping < time() or housekeeping_now:
				next_housekeeping = time() + ImageServer.HOUSEKEEPING_EVERY_SECONDS

				for i in range(0, 4):
					if (
						ImageServer.HOUSEKEEPING_THRESHOLD[i] > 0
						and ImageServer.HOUSEKEEPING_THRESHOLD[i]
						< self._surfaces_present[i]
					):
						housekeeping_now = True

				if housekeeping_now:
					print("Image Server does Housekeeping now")

					for image in self.streamed_images.getCopyOfList():

						if image._surfaces[1][StreamedImage.SURFACE_AGE] >= 5:
							image.unload_except_thumb()

						image.increment_age()
				else:
					print("No housekeeping needed for Image Server")

		print("ImageServer loader loop exited")
		self.loader_loop_running = False

	def add_view(self, view) -> None:
		self.views.append(view)

	def add_faptable_view(self, fapTableView) -> None:
		self.fap_table_views.append(fapTableView)

	def server_view_fetcher_loop(self) -> None:

		self.fetcher_loop_running = True
		while self.running:
			sleep(0.2)
			# print("server view fetcher loop")
			for view in self.views:
				sleep(1)

				spot_width = math.ceil(World.SPOT_SIZE / view.height)

				if (
					# view.height / 4
					# <= World.SPOT_SIZE
					spot_width
					>= ImageServer.QUALITY_PIXEL_SIZE[StreamedImage.QUALITY_GRID]
				):

					view_chunk_x1_C = view.world.convert_S_to_C(view.world_x1_S)
					view_chunk_y1_C = view.world.convert_S_to_C(view.world_y1_S)
					view_chunk_x2_C = view.world.convert_S_to_C(view.world_x2_S)
					view_chunk_y2_C = view.world.convert_S_to_C(view.world_y2_S)

					# based on height, fetch surrounding chunks also
					# print(view_chunk_x1_C,view_chunk_y1_C,"-",view_chunk_x2_C,view_chunk_y2_C)
					for x_C in range(view_chunk_x1_C, view_chunk_x2_C + 1):
						for y_C in range(view_chunk_y1_C, view_chunk_y2_C + 1):
							chunk: Chunk = view.world.get_chunk_at_C(x_C, y_C)
							# print("view fetcher: chunk",chunk.x_C,chunk.y_C)
							# sleep(0.02)
							for x_SL in range(0, World.CHUNK_SIZE):
								# sleep(0.002)
								for y_SL in range(0, World.CHUNK_SIZE):
									# sleep(0.00001)
									frame = chunk.get_frame_at_SL(x_SL, y_SL)

									if frame != None:
										image = frame.image

										if isinstance(image, StreamedMockup):
											continue

										# needed_quality = StreamedImage.QUALITY_THUMB
										needed_quality = StreamedImage.QUALITY_GRID

										# if (
										# 	view.height / 4
										# 	< World.SPOT_SIZE
										# 	/ ImageServer.QUALITY_PIXEL_SIZE[
										# 		StreamedImage.QUALITY_THUMB
										# 	]
										# ):
										# 	needed_quality = StreamedImage.QUALITY_GRID
										x_S = x_SL + chunk.top_spot_x_S
										y_S = y_SL + chunk.top_spot_y_S
										is_on_screen = (
											(view.world_x1_S <= x_S)
											and (x_S <= view.world_x2_S)
											and (view.world_y1_S <= y_S)
											and (y_S <= view.world_y2_S)
										)
										if (
											is_on_screen
											and spot_width
											> ImageServer.QUALITY_PIXEL_SIZE[
												StreamedImage.QUALITY_SCREEN
											]
											/ 2
										):
											needed_quality = (
												StreamedImage.QUALITY_SCREEN
											)

										if (
											is_on_screen
											and spot_width
											> ImageServer.QUALITY_PIXEL_SIZE[
												StreamedImage.QUALITY_SCREEN
											]
										):
											needed_quality = (
												StreamedImage.QUALITY_ORIGINAL
											)

										if (
											image.state == StreamedImage.STATE_READY
											and image.get_available_quality()
											< needed_quality
										):
											image.set_ordered_quality(needed_quality)

											if (
												image.get_ordered_quality()
												> image.get_available_quality()
											):
												image.state = (
													StreamedImage.STATE_READY_AND_RELOADING
												)
												self.media_queue.queue.insert(0, image)

				# load peek
				frame = view.world.get_frame_at_S(
					view.selection.x_S, view.selection.y_S
				)
				if frame != None:
					image = frame.image
					if image != None:
						if isinstance(image, StreamedMockup):
							continue
						if (
							image.state == StreamedImage.STATE_READY
							and image.get_available_quality()
							< StreamedImage.QUALITY_ORIGINAL
						):
							image.set_ordered_quality(StreamedImage.QUALITY_ORIGINAL)

							if (
								image.get_ordered_quality()
								> image.get_available_quality()
							):
								image.state = StreamedImage.STATE_READY_AND_RELOADING
								self.media_queue.queue.insert(0, image)

			# load current Fap Table in HiRes
			for fapTable_view in self.fap_table_views:

				current_fapTable: FapTable = fapTable_view.fap_table
				if current_fapTable != None and current_fapTable.is_displayed:
					for card in current_fapTable.cards:
						if card.image != None:
							image: AbstractStreamedMedia = card.image
							if (
								image.state == StreamedImage.STATE_READY
								and image.get_available_quality()
								< StreamedImage.QUALITY_ORIGINAL
							):
								image.set_ordered_quality(
									StreamedImage.QUALITY_ORIGINAL
								)

								if (
									image.get_ordered_quality()
									> image.get_available_quality()
								):
									image.state = (
										StreamedImage.STATE_READY_AND_RELOADING
									)

									self.media_queue.queue.insert(0, image)

		print("ImageServer fetcher loop exited")
		self.fetcher_loop_running = False

	def run(self) -> None:
		self.thread_loader = threading.Thread(target=self.server_loader_loop, args=())
		self.thread_loader.daemon = (
			True  # so these threads get killed when program exits
		)
		self.thread_loader.start()

		self.thread_view_fetcher = threading.Thread(
			target=self.server_view_fetcher_loop, args=()
		)
		self.thread_view_fetcher.daemon = (
			True  # so these threads get killed when program exits
		)
		self.thread_view_fetcher.start()

	def stop(self) -> None:
		self.running = False
		for conduit in self.conduits:
			conduit.close()

		while (self.fetcher_loop_running) or (self.loader_loop_running):
			sleep(0.06)

		self.image_server_database.stop()

	def create_streamed_image(
		self, path, quality=StreamedImage.QUALITY_ORIGINAL
	) -> AbstractStreamedMedia:
		image = StreamedImage()
		image.set_original_file_path(path)
		image.set_ordered_quality(quality)
		self.streamed_images.append(image)
		self.media_queue.put(image)
		return image

	def create_streamed_mockup(self, path, color_string="", color=None):
		image = StreamedMockup()
		image.set_original_file_path(path)
		# self.media_queue.put(image)
		if color != None:
			image.average_color = color
		else:
			md5 = hashlib.md5(str(color_string).encode()).hexdigest()
			r = int(md5[0:2], 16)
			g = int(md5[2:4], 16)
			b = int(md5[4:6], 16)
			image.average_color = (r, g, b)  # type: ignore

		image.state = AbstractStreamedMedia.STATE_READY
		self._available_quality = AbstractStreamedMedia.QUALITY_COLOR
		self.streamed_images.append(image)
		return image

	def get_number_of_images(self) -> int:
		return self.streamed_images.length()

	def get_queue_size(self) -> int:
		return self.media_queue.qsize()

	def _calculate_memory_usage(self) -> None:
		self._bytes_used_total = 0
		self._bytes_used_sizes = [0, 0, 0, 0]
		self._surfaces_present = [0, 0, 0, 0]

		for image in self.streamed_images.getCopyOfList():
			self._bytes_used_total += image.get_memory_usage_in_bytes()

			for q in range(
				AbstractStreamedMedia.QUALITY_THUMB,
				AbstractStreamedMedia.QUALITY_ORIGINAL + 1,
			):
				self._bytes_used_sizes[q] += image.get_memory_usage_in_bytes(quality=q)
				self._surfaces_present[q] += image.get_number_of_surfaces_loaded_in_ram(
					quality=q
				)

			p = ""
			if self.paused:
				p = " PAUSED"
			self._status_line = (
				"T "
				+ str(self._surfaces_present[0])
				+ " G "
				+ str(self._surfaces_present[1])
				+ " S "
				+ str(self._surfaces_present[2])
				+ " O "
				+ str(self._surfaces_present[3])
				+ p
			)

	def get_status_line(self) -> str:
		return self._status_line

	def print_statistic(self) -> None:
		mb = 1024 * 1024
		print("Total:", int(self._bytes_used_total / mb))
		print(
			"Thumbs   ",
			self._surfaces_present[0],
			"using",
			int(self._bytes_used_sizes[0] / mb),
			"MB",
		)
		print(
			"Grid     ",
			self._surfaces_present[1],
			"using",
			int(self._bytes_used_sizes[1] / mb),
			"MB",
		)
		print(
			"Screen   ",
			self._surfaces_present[2],
			"using",
			int(self._bytes_used_sizes[2] / mb),
			"MB",
		)
		print(
			"Original ",
			self._surfaces_present[3],
			"using",
			int(self._bytes_used_sizes[3] / mb),
			"MB",
		)

	def calculate_memory_usage(self) -> int:
		return self._bytes_used_total
