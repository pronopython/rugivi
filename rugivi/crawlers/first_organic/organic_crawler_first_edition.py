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

import math
from rugivi.image_service.image_server import (
	Frame,
	ImageServer,
	StreamedImage,
	World,
	sleep,
	threading,
)
from rugivi.image_service.streamed_image import StreamedImage
from rugivi.world_database_service.world_database import (
	WorldDatabase,
)
from rugivi.world_things.frame import Frame
from rugivi.world_things.world import Frame, World


import os
import random
import threading
from pathlib import Path
from time import sleep
from time import time


class OrganicCrawlerFirstEdition:

	START_SPOT_SEARCH_RANDOM = 0
	START_SPOT_SEARCH_NEAR_WORLD_CENTER = 1
	START_SPOT_SEARCH_NEAR_PARENT = 2

	START_SPOT_SEARCH: int = START_SPOT_SEARCH_NEAR_PARENT

	SAVE_EVERY_SECONDS = 60 * 10  # 10 minutes

	def __init__(
		self,
		world: World,
		image_server: ImageServer,
		basedir: str,
		crawler_db_file_path: str,
		crawl_videos=True,
		excludeDirList=[],
		mockup_mode=True,
		cross_shape_grow = False,
		no_diagonal_grow = True,
		organic_grow = True,
		reach_out_ant_mode = True,
	) -> None:

		self.db = WorldDatabase(crawler_db_file_path, world, image_server)

		self.world: World = world
		self.world.set_chunk_loader(self.db)  # set world_db as the chunk loader

		self.imageServer: ImageServer = image_server
		self.current_dir: str = ""
		self.status: str = "new"
		self.basedir: str = self.db.get_and_put_if_none(
			WorldDatabase.KEY_BASEDIR, basedir
		)
		self.excludeDirList=excludeDirList

		self.mockup_mode = mockup_mode

		self.pause_crawling: bool = False
		""" can be set externally to True to halt crawling until this is set to False again"""

		self.start_spot_search_method: int = (
			OrganicCrawlerFirstEdition.START_SPOT_SEARCH_NEAR_PARENT
		)

		# organic grow will sponge-like grow the bioms and not more rectangular
		self.ORGANIC_GROW: bool = organic_grow

		# only grow up/down, left/right and not diagonal
		#   .o.
		#   oxo   x=start pos
		#   .o.   o=ok
		self.NO_DIAGONAL_GROW: bool = no_diagonal_grow

		# Ant mode will create diagonal corridors from time to time
		self.REACH_OUT_ANT_MODE: bool = reach_out_ant_mode
		self.ANT_CORRIDOR_PROB: float = 1  # 0.5..1 less..more

		self.CROSS_SHAPE_GROW = cross_shape_grow

		self.running: bool = True
		self.crawler_loop_running: bool = False

		self.crawl_videos = crawl_videos

	def run(self) -> None:
		self.thread = threading.Thread(target=self.crawler_loop, args=())
		self.thread.daemon = True  # so these threads get killed when program exits
		self.thread.start()

	def stop(self) -> None:
		self.running = False
		print("Waiting for crawler to finish current dir...")
		while self.crawler_loop_running:
			sleep(0.05)

	def crawler_loop(self) -> None:

		##############################################################################
		# Retrieve initial values from db or create new if run for first time
		##############################################################################

		status = self.db.get_and_put_if_none(
			WorldDatabase.KEY_STATUS,
			WorldDatabase.VALUE_STATUS_CRAWLING,
		)

		if (
			status == WorldDatabase.VALUE_STATUS_CRAWL_COMPLETED
		):  # TODO craw completed is not used yet!
			return

		self.border_spots: set = self.db.get(
			WorldDatabase.KEY_BORDERSPOTS
		)  # a set of *all* empty spots directly neighbouring to used spots

		if self.border_spots == None:
			self.border_spots = set()
			self.border_spots.add((0, 0))

		basedir_path = Path(self.basedir)
		basedir_parent_path = basedir_path.parent.absolute()

		self.dir_and_start_spot: dict = self.db.get(WorldDatabase.KEY_DIRANDSTARTSPOT)
		if self.dir_and_start_spot == None:
			self.dir_and_start_spot = {}

		next_save_at_number_of_frames = 10000
		last_save_time = time()

		##############################################################################
		# Crawl directory by directory
		##############################################################################

		self.crawler_loop_running = True
		for current_dir, d_names, f_names in os.walk(self.basedir):

			##############################################################################
			# Reasons to make a pause
			##############################################################################

			while self.pause_crawling and self.running == True:
				sleep(1)
				self.status = "paused"

			self.__pause_for_image_queue()

			##############################################################################
			# Directory known?
			##############################################################################

			self.status = "crawling for next dir"

			current_dir_absolute_path = Path(current_dir).absolute()
			if str(current_dir_absolute_path) in self.dir_and_start_spot:
				# already visited according to database
				sleep(0.2)
				continue

			skip_dir = False
			for exdir in self.excludeDirList:
				#print(current_dir_absolute_path," ?= ",exdir)
				if str(current_dir_absolute_path).startswith(exdir):
					print("Excluded dir",current_dir_absolute_path,"is skipped")
					skip_dir = True
					break
			if skip_dir:
				sleep(0.2)
				continue

			# populating dirAndStartSpot when this is crawler is run for the first time
			if len(self.dir_and_start_spot) == 0:
				self.dir_and_start_spot[str(basedir_path.absolute())] = (0, 0)
				self.dir_and_start_spot[str(basedir_parent_path)] = (0, 0)

			##############################################################################
			# HANDLE IMAGES
			##############################################################################

			self.status = "filter files"

			image_f_names = [
				file
				for file in f_names
				if file.lower().endswith((".jpg", ".jpeg", ".gif", ".png", ".tif"))
			]

			##############################################################################
			# Find empty spots
			##############################################################################

			neededSpots = len(image_f_names)  # TODO only count images

			start_spot = None  # if something was added, this will be not None

			if neededSpots > 0:

				self.current_dir = os.path.basename(current_dir)

				start_spot, found_empty_spots = self.__find_empty_spots(
					current_dir, neededSpots
				)

				# __find_empty_spots returns with None,None if shutdown is initiated, so follow along
				if self.running == False:
					self.crawler_loop_running = False
					return

				##############################################################################
				# Found enough empty spots, now these will be populated with images of dir
				##############################################################################

				self.status = "creating frames"

				for file_number, filename in enumerate(image_f_names):
					file_path = os.path.join(current_dir, filename)

					if not self.mockup_mode:
						streamed_image = self.imageServer.create_streamed_image(
							file_path, StreamedImage.QUALITY_THUMB
						)
					else:
						streamed_image = self.imageServer.create_streamed_mockup(file_path, color_string=self.current_dir)

					(start_spot_x_S, start_spot_y_S) = found_empty_spots[file_number]

					self.world.set_frame_at_S(
						Frame(streamed_image), start_spot_x_S, start_spot_y_S
					)

			##############################################################################
			# HANDLE VIDEOS
			##############################################################################

			if self.crawl_videos:
				video_f_names = [
					file
					for file in f_names
					if file.lower().endswith(
						(
							".mp4",
							".mkv",
							".webm",
							".mov",
							".rm",
							".avi",
							".flv",
							".wmv",
							".asf",
						)
					)  # TODO do all of the video formats work? All tested?
				]
			else:
				video_f_names = []

			for video_filename in video_f_names:

				self.__pause_for_image_queue()

				video_file_path = os.path.join(current_dir, video_filename)

				if str(Path(video_file_path).absolute()) in self.dir_and_start_spot:
					# already visited according to database
					sleep(0.2)
					continue

				positions = (
					self.imageServer.video_still_generator.analyze_and_get_positions(
						video_file_path
					)
				)

				##############################################################################
				# Find empty spots for video stills
				##############################################################################

				neededSpots = len(positions)

				if neededSpots == 0:
					continue  # next video

				self.current_dir = os.path.basename(current_dir)

				video_start_spot, found_empty_spots = self.__find_empty_spots(
					current_dir, neededSpots
				)

				# __find_empty_spots returns with None,None if shutdown is initiated, so follow along
				if self.running == False:
					self.crawler_loop_running = False
					return

				if start_spot == None:
					# only use video start spot when no images had been added
					# (dir has ONLY videos)
					start_spot = video_start_spot

				##############################################################################
				# Found enough empty spots, now these will be populated with images of dir
				##############################################################################

				self.status = "creating frames for video file"

				for position_number, position in enumerate(positions):
					(
						uuid_name,
						file_path,
					) = (
						self.imageServer.image_cache.generate_new_cache_uuid_and_filename()
					)

					if not self.mockup_mode:
						streamed_image = self.imageServer.create_streamed_image(
							file_path, StreamedImage.QUALITY_THUMB
						)
					else:
						streamed_image = self.imageServer.create_streamed_mockup(file_path, color_string=video_file_path)

					streamed_image.set_extended_attribute("video_still_uuid", uuid_name)
					streamed_image.set_extended_attribute("video_file", video_file_path)
					streamed_image.set_extended_attribute("video_position", position)

					(start_spot_x_S, start_spot_y_S) = found_empty_spots[
						position_number
					]

					self.world.set_frame_at_S(
						Frame(streamed_image), start_spot_x_S, start_spot_y_S
					)
				if video_start_spot != None:

					##############################################################################
					# remember current position for video
					##############################################################################

					self.status = "remember video start spot"
					# remember startSpot of this dir
					video_file_path = Path(video_file_path).absolute()
					self.dir_and_start_spot[str(video_file_path)] = video_start_spot


				if start_spot != None:

					##############################################################################
					# remember current position and (sometimes) save everything to db / disk
					##############################################################################

					self.status = "remember start spot"
					# remember startSpot of this dir
					basedir_path = Path(current_dir).absolute()
					self.dir_and_start_spot[str(basedir_path)] = start_spot

					if (
						self.world.count_frames() > next_save_at_number_of_frames
						or last_save_time
						+ OrganicCrawlerFirstEdition.SAVE_EVERY_SECONDS
						< time()
					):
						next_save_at_number_of_frames = (
							self.world.count_frames() + 10000
						)
						last_save_time = time()
						self.__save_to_db(self.border_spots, self.dir_and_start_spot)

			if start_spot != None:

				##############################################################################
				# remember current position and (sometimes) save everything to db / disk
				##############################################################################

				self.status = "remember start spot"
				# remember startSpot of this dir
				basedir_path = Path(current_dir).absolute()
				self.dir_and_start_spot[str(basedir_path)] = start_spot

				if (
					self.world.count_frames() > next_save_at_number_of_frames
					or last_save_time + OrganicCrawlerFirstEdition.SAVE_EVERY_SECONDS
					< time()
				):
					next_save_at_number_of_frames = self.world.count_frames() + 10000
					last_save_time = time()
					self.__save_to_db(self.border_spots, self.dir_and_start_spot)

				self.status = "fetching next dir"

				if self.running == False:
					print("Crawler loop stopped")
					self.crawler_loop_running = False
					return

		self.db.put(
			WorldDatabase.KEY_STATUS,
			WorldDatabase.VALUE_STATUS_CRAWLING,
		)
		self.__save_to_db(self.border_spots, self.dir_and_start_spot)
		self.status = "crawl completed, chunk database finalized"
		self.crawler_loop_running = False
		print(self.status)

	def __save_to_db(self, borderSpots, dirAndStartSpot):

		print("saving to db")
		self.status = "saving to db"
		self.db.put(WorldDatabase.KEY_BORDERSPOTS, borderSpots)
		self.db.put(WorldDatabase.KEY_DIRANDSTARTSPOT, dirAndStartSpot)

		"""
		allChunks = self.world.get_all_chunks_in_memory_as_list()
		for chunk in allChunks:
			if chunk.is_empty():
				continue
			cso = ChunkSaveObject()
			cso.from_chunk(chunk)
			k = str((chunk.x_C, chunk.y_C))
			# print("inserting chunk",k)
			# storing in same as all the other keys is so hacky...
			# but commits are per table sadly...
			# and if program crashes between two commits...
			self.db.db[str((chunk.x_C, chunk.y_C))] = cso.to_tuple()

		self.db.commit_db()
		"""

		self.db.save_world_to_database()

	def __pause_for_image_queue(self):
		if self.imageServer.get_queue_size() > 500:
			while self.imageServer.get_queue_size() > 100 and self.running == True:
				self.status = "sleeping"
				sleep(0.2)

	def __find_empty_spots(self, current_dir, neededSpots):

		found_enough_empty_spots: bool = False

		found_empty_spots: list = []

		list_of_unsuccessful_border_spots = []

		start_spot = None

		self.status = "finding biome"
		while not found_enough_empty_spots:

			sleep(0.02)

			if self.running == False:
				print("Crawler loop stopped")
				self.crawler_loop_running = False
				return None, None

			found_empty_spots = []

			##############################################################################
			# Looking for a start spot
			# Start spots are selected out of border spots (these are always empty)
			##############################################################################

			# fallback: fill start_spot no matter what will happen
			start_spot = random.choice(tuple(self.border_spots))

			#print("Trying start spot",start_spot)

			if (
				self.start_spot_search_method
				== OrganicCrawlerFirstEdition.START_SPOT_SEARCH_NEAR_PARENT
			):

				# Find a parent dir of the current dir that is already placed in the world.
				# This can also be a grandparent dir etc if the parent dir is empty!
				basedir_path = Path(current_dir)

				basedir = Path(self.basedir).absolute()
				# error: 2 times going to parent dir!
				# parentPath = path.parent.absolute()
				basedir_parent_path = basedir_path.absolute()
				# Going down the parent line
				while len(str(basedir_parent_path)) > len(str(basedir)):
					basedir_parent_path = basedir_parent_path.parent.absolute()
					if str(basedir_parent_path) in self.dir_and_start_spot:
						break

				parent_spot = self.dir_and_start_spot[str(basedir_parent_path)]
				(parent_spot_x_S, parent_spot_y_S) = parent_spot

				# try x times to find an empty border spot closer and closer to the parent spot
				for current_round in range(
					0, 30
				):  #  was 300 -> more time needed for that (bad), but 30 is inaccurate
					sleep(0.0002)
					candidate = random.choice(tuple(self.border_spots))
					#print("border spot candidate",candidate)
					if candidate in list_of_unsuccessful_border_spots:
						#print("Border candiate",candidate, "already checked and it is not good")
						continue
					#print("Border candiate",candidate)
					(candidate_x_S, candidate_y_S) = candidate
					(start_spot_x_S, start_spot_y_S) = start_spot
					# changed "or" to "and"
					if self.CROSS_SHAPE_GROW:
						if abs(candidate_x_S - parent_spot_x_S) < abs(
							start_spot_x_S - parent_spot_x_S
							) and abs(candidate_y_S - parent_spot_y_S) < abs(
							start_spot_y_S - parent_spot_y_S
						):
							start_spot = candidate
					elif math.dist((candidate_x_S,candidate_y_S),(parent_spot_x_S,parent_spot_y_S)) < math.dist((start_spot_x_S,start_spot_y_S),(parent_spot_x_S,parent_spot_y_S)):
						start_spot = candidate

			elif (
				self.start_spot_search_method
				== OrganicCrawlerFirstEdition.START_SPOT_SEARCH_NEAR_WORLD_CENTER
			):
				for current_round in range(0, 50):
					sleep(0.0002)
					candidate = random.choice(tuple(self.border_spots))
					#print("border spot candidate",candidate)
					if candidate in list_of_unsuccessful_border_spots:
						continue
					(candidate_x_S, candidate_y_S) = candidate
					(start_spot_x_S, start_spot_y_S) = start_spot
					if abs(candidate_x_S) < abs(start_spot_x_S) or abs(
						candidate_y_S
					) < abs(start_spot_y_S):
						start_spot = candidate

			"""
			if True:   # TODO insert "far away" code, do this from while to while
				# also grow not around center but around start point of parent dir!!!!!
				for i in range (0,50):
					candidate = random.choice(borderSpots)
					(cx,cy) = candidate
					(sx,sy) = startSpot
					if abs(cx) > abs(sx) or abs(cy) > abs(sy):
						startSpot = candidate

			"""

			##############################################################################
			# See if enough empty spots are next to the start spot
			##############################################################################

			stack_with_empty_spots_to_check: list = [start_spot]
			# stack always holds neighbouring empty spots to be checked
			# if they are not that far away so that spots are grouped together
			# and not so far away from another
			#print("checking enough empty spots")
			while (
				len(stack_with_empty_spots_to_check) > 0
				and not found_enough_empty_spots
			):
				#print("size of stack_with_empty_spots_to_check:",len(stack_with_empty_spots_to_check))
				sleep(0.0002)
				if self.running == False:
					print("Crawler loop stopped")
					self.crawler_loop_running = False
					return None, None

				##############################################################################
				# Select one of the empty 8 (or less) neighbours of the start_spot
				##############################################################################
				#print("select one empty neighbour")
				if not self.ORGANIC_GROW:
					currentSpot = stack_with_empty_spots_to_check.pop(0)
				else:  # organic grow
					(start_spot_x_S, start_spot_y_S) = start_spot
					currentSpot = random.choice(stack_with_empty_spots_to_check)

					# calculate if the next empty spot should "reach out",
					# that means, should be farest instead of nearest neighbour

					reach_out = False

					if (
						self.REACH_OUT_ANT_MODE
						and neededSpots - len(found_empty_spots) != 0
					):
						reach_out = (
							random.random()
							< ((neededSpots - len(found_empty_spots)) / neededSpots)
							* self.ANT_CORRIDOR_PROB
						)

					no_of_same_result = 0
					if neededSpots > 100:
						max_same_result = 1
					else:
						max_same_result = 3
					if reach_out:
						max_same_result = 8
					for current_round in range(0, 50):
						if no_of_same_result >= max_same_result:
							break
						candidate = random.choice(stack_with_empty_spots_to_check)
						#print("current_round", current_round,"currentspot:",currentSpot,"candidate", candidate)						
						if candidate == currentSpot:
							no_of_same_result += 1
							continue
						else:
							sleep(0.0001)
						(candidate_x_S, candidate_y_S) = candidate
						(ux, uy) = currentSpot
						# if abs(cx-sx) < abs(ux-sx) or abs(cy-sy) < abs(uy-sy):

						# was both "or", now "and"
						if reach_out:
							# changed "or" to "and"
							if abs(candidate_x_S - start_spot_x_S) > abs(
								ux - start_spot_x_S
							) and abs(candidate_y_S - start_spot_y_S) > abs(
								uy - start_spot_y_S
							):
								currentSpot = candidate
								no_of_same_result = 0
							else:
								no_of_same_result += 1
						else:
							# changed "or" to "and"
							if abs(candidate_x_S - start_spot_x_S) < abs(
								ux - start_spot_x_S
							) and abs(candidate_y_S - start_spot_y_S) < abs(
								uy - start_spot_y_S
							):
								no_of_same_result = 0
								currentSpot = candidate
							else:
								no_of_same_result += 1

					stack_with_empty_spots_to_check.remove(currentSpot)

				# the current spot is taken...
				found_empty_spots.append(currentSpot)

				if len(found_empty_spots) >= neededSpots:
					found_enough_empty_spots = True
					break

				# ... and now look for its neighbours
				(start_spot_x_S, start_spot_y_S) = currentSpot

				##############################################################################
				# Fill stack with all empty neighbours (up to 8 neighbours)
				##############################################################################
				#print("add all empty adjacent spots of the neighbour")
				for x_S in range(start_spot_x_S - 1, start_spot_x_S + 2):
					for y_S in range(start_spot_y_S - 1, start_spot_y_S + 2):
						if start_spot_x_S == x_S and start_spot_y_S == y_S:
							# not the center spot (not a neighbour)
							continue

						if (
							self.NO_DIAGONAL_GROW
							and abs(x_S - start_spot_x_S) - abs(y_S - start_spot_y_S)
							== 0
						):
							continue
						if (x_S, y_S) in found_empty_spots:
							continue
						if (x_S, y_S) in stack_with_empty_spots_to_check:
							continue
						if self.world.get_frame_at_S(x_S, y_S) != None:
							continue
						else:
							stack_with_empty_spots_to_check.append((x_S, y_S))

			if not found_enough_empty_spots:
				list_of_unsuccessful_border_spots.append(start_spot)

		##############################################################################
		# correct border spots (add new border spots of the new now filled spots and
		# remove the border spots that now contain new frames)
		##############################################################################

		self.status = (
			"correcting border, " + str(len(found_empty_spots)) + " spots to check"
		)
		# correct border spots
		for currentSpot in found_empty_spots:
			(start_spot_x_S, start_spot_y_S) = currentSpot
			#sleep(0.00003)
			sleep(0.00002)
			# go through all 8 neighbours and check changes in "border status"
			for x_S in range(start_spot_x_S - 1, start_spot_x_S + 2):
				for y_S in range(start_spot_y_S - 1, start_spot_y_S + 2):
					if self.world.get_frame_at_S(x_S, y_S) != None or (x_S, y_S) in found_empty_spots:
						if (x_S, y_S) in self.border_spots:
							#print("removing border spot",(x_S, y_S))
							self.border_spots.remove((x_S, y_S))  # no border anymore
					else:
						if (x_S, y_S) not in self.border_spots:
							self.border_spots.add((x_S, y_S))  # a new border spot

		#for bs in self.border_spots:
		#	if self.world.get_frame_at_S(bs[0],bs[1]) != None:
		#		print("BORDER SPOTS CONTAIN NON EMPTY SPOT:",bs)

		#print("found empty spots",found_empty_spots)
		#print("border spots", self.border_spots)

		return start_spot, found_empty_spots
