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

import configparser
import os
import pathlib
import sys

from rugivi.rugivi_configurator import ConfigApp


# Import pygame, hide welcome message because it messes with
# status output
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

from rugivi.crawlers.first_organic.organic_crawler_first_edition import (
	OrganicCrawlerFirstEdition,
)


import pygame

from time import sleep

import math
import psutil
import random

from rugivi.image_service.image_server import *
from rugivi.image_service.streamed_image import StreamedImage

from rugivi.status import *
from rugivi.world_things.world import *

from rugivi.world_database_service.world_database import *
from rugivi.dialogs import *
from rugivi.view import *
from rugivi.fap_table.fap_table_manager import *
from rugivi.fap_table.fap_table_view import *
from rugivi.fap_table.fap_table import *
from rugivi.fap_table.fap_tables import *
from rugivi.selection import *
from rugivi.exports.world_overlook import WorldOverlook

import platform
import subprocess

import getopt  # commandline arg handler

import tkinter
from tkinter import messagebox

from rugivi import config_file_handler as config_file_handler
from rugivi import dir_helper as dir_helper


class RugiviMainApp:

	DOUBLECLICKTIME = 500

	# Maximum possible jump distance is: +/- JUMP_NUMBER_OF_SUBMOVES * JUMP_SUBMOVE_DISTANCE_S for x and y
	JUMP_NUMBER_OF_SUBMOVES = 20
	JUMP_SUBMOVE_DISTANCE_S = 100

	def __init__(self) -> None:
		self.size = self.weight, self.heigth = (
			640,
			480,
		)
		self.display = None
		self.running = False
		self.image_server = None

		self.worldDbFile = "chunks.sqlite"
		self.thumbDbFile = "thumbs.sqlite"
		self.crawlDir = "."
		self.tagDir = ""
		self.cache_base_dir = "./cache"

		configurator_run = False

		self.configured = False

		while not self.configured:
			self.configured = dir_helper.is_config_file_present("RuGiVi","rugivi.conf")

			if self.configured:
				self.configDir = dir_helper.get_config_dir("RuGiVi")
				self.configParser = config_file_handler.ConfigFileHandler(
					os.path.join(self.configDir, "rugivi.conf")
				)

				try:
					self.configured = self.configured and self.configParser.get_boolean("configuration", "configured")
				except configparser.NoSectionError:
					self.configured = False

			if not self.configured and configurator_run:
				sys.exit() # Cancel was pressed in configurator

			if not self.configured and not configurator_run:
				#root = tkinter.Tk()
				#root.withdraw()
				#messagebox.showinfo(
				#	"Not configured",
				#	"Please configure RuGiVi and apply the settings in the following dialog.",
				#)

				app = ConfigApp(apply_and_start=True)
				app.run()

				configurator_run = True


		self.worldDbFile = self.configParser.get_directory_path(
			"world", "worldDB", self.worldDbFile
		)
		self.thumbDbFile = self.configParser.get_directory_path(
			"thumbs", "thumbDB", self.thumbDbFile
		)
		self.crawlDir = self.configParser.get_directory_path(
			"world", "crawlerRootDir", self.crawlDir
		)
		self.cache_base_dir = self.configParser.get_directory_path(
			"cache", "cacherootdir", self.cache_base_dir
		)
		dir_list_str = self.configParser.get("world", "crawlerExcludeDirList")
		if len(dir_list_str) > 0:
			self.excludeDirList = dir_list_str.split(sep=";")
		else:
			self.excludeDirList = []

		self.show_info = self.configParser.get_int("control", "showinfo")

		self.fapTables = FapTables(self.configParser)

		self.parseCommandlineArgs()

		print("World DB  :", self.worldDbFile)
		print("Thumbs DB :", self.thumbDbFile)
		print("Crawl root:", self.crawlDir)

		if self.configParser.get_boolean("control", "reverseScrollWheelZoom"):
			self.zoomDirection = -1
		else:
			self.zoomDirection = 1

		self.cross_shape_grow = self.configParser.get_boolean("world", "crossshapegrow")
		self.no_diagonal_grow = self.configParser.get_boolean("world", "nodiagonalgrow")
		self.organic_grow = self.configParser.get_boolean("world", "organicgrow")
		self.reach_out_ant_mode = self.configParser.get_boolean("world", "reachoutantmode")

		self.vlc_binary = self.configParser.get("videoplayback", "vlcbinary")
		self.video_crawl_enabled = self.configParser.get_boolean("world", "crawlvideos")
		self.video_vlc_enabled = self.configParser.get_boolean(
			"videoplayback", "vlcenabled"
		)
		self.video_vlc_seek_position = self.configParser.get_boolean(
			"videoplayback", "vlcseekposition"
		)
		self.debug_vlc_verbose = self.configParser.get_boolean(
			"debug", "vlcverbose"
		)
		self.debug_cv2_verbose = self.configParser.get_boolean(
			"debug", "cv2verbose"
		)
		self.debug_mockupimages = self.configParser.get_boolean(
			"debug", "mockupimages"
		)

		if not self.debug_cv2_verbose:
			# prevent open cv error messages when video files make problems
			os.environ['OPENCV_LOG_LEVEL'] = 'OFF'
			os.environ['OPENCV_FFMPEG_LOGLEVEL'] = "-8"

		self.video_still_generator_jpg_quality = self.configParser.get_int("videoframe", "jpgquality"
		)
		self.video_still_generator_resize_enabled = self.configParser.get_boolean(
			"videoframe", "maxsizeenabled"
		)
		self.video_still_generator_max_dimension = self.configParser.get_int(
			"videoframe", "maxsize"
		)
		self.video_still_generator_remove_letterbox = self.configParser.get_boolean(
			"videoframe", "removeletterbox"
		)


	def parseCommandlineArgs(self) -> None:
		try:
			options, args = getopt.getopt(
				sys.argv[1:], "?hc:", ["thumb-db=", "world-db="]
			)
		except getopt.GetoptError:
			print("Wrong parameters")
			# TODO show help
			sys.exit(2)

		for opt, arg in options:
			if (opt == "-h") or (opt == "-?"):
				# TODO add some help...
				sys.exit(2)
			elif opt == "-c":
				self.crawlDir = str(arg)
			elif opt == "--thumb-db":
				self.thumbDbFile = str(arg)
			elif opt == "--world-db":
				self.worldDbFile = str(arg)

	def open_file(self, path) -> None:
		if platform.system() == "Windows":
			os.startfile(path)  # type: ignore
		elif platform.system() == "Darwin":
			subprocess.Popen(["open", path])
		else:
			subprocess.Popen(["xdg-open", path])

	def open_video_with_vlc(self, path, position: float = 0.0):
		if position > 2:
			position -= 2
		# position_str = "--start-time=" + str(math.floor(position))
		position_str = "--start-time=" + str(position)
		if not self.debug_vlc_verbose:
			p = subprocess.Popen([self.vlc_binary, position_str, path],shell=False,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL )
		else:
			p = subprocess.Popen([self.vlc_binary, position_str, path])

	def run(self) -> NoReturn:

		pygame.init()

		pygame.display.set_caption("RuGiVi")

		icon = pygame.image.load(dir_helper.get_install_dir() + "/icon.png")
		pygame.display.set_icon(icon)

		self.display = pygame.display.set_mode(
			self.size, pygame.RESIZABLE | pygame.HWSURFACE | pygame.DOUBLEBUF
		)

		self.image_server = ImageServer(32, self.thumbDbFile, self.cache_base_dir, number_of_video_conduits = 8)
		# reconfigure video still generatorl
		self.image_server.video_still_generator.jpg_quality=self.video_still_generator_jpg_quality
		if self.video_still_generator_resize_enabled:
			self.image_server.video_still_generator.max_dimension=(self.video_still_generator_max_dimension,self.video_still_generator_max_dimension)
		self.image_server.video_still_generator.remove_letterbox=self.video_still_generator_remove_letterbox

		self.world = World()

		self.fap_table_manager = FapTableManager(self.image_server)

		clock = pygame.time.Clock()

		initial_height = (
			World.SPOT_SIZE
			/ ImageServer.QUALITY_PIXEL_SIZE[StreamedImage.QUALITY_THUMB]
		)
		view : View = View(self.world, initial_height)

		fap_table_view = FapTableView()

		current_fap_table: FapTable = None  # type: ignore

		for fap_table_dir in self.fapTables.fap_tables_flat:
			current_fap_table = self.fap_table_manager.open_fap_table(fap_table_dir)

		current_fap_table = self.fap_table_manager.get_fap_table_by_dir(
			self.fapTables.get_current_fap_table_dir()
		)
		fap_table_view.set_current_fap_table(current_fap_table)

		self.image_server.add_view(view)
		self.image_server.add_faptable_view(fap_table_view)

		move_view = False
		view_moved = False

		move_card = False
		card_moved = False
		current_edit_card = None
		card_resize_mode = False

		status = Status(self.configParser.get_int("fonts", "statusFontSize"))
		python_executable = self.configParser.get(
			"control", "pythonexecutable"
		)  # to start Fapel System components

		path = self.crawlDir

		self.crawler = OrganicCrawlerFirstEdition(
			self.world,
			self.image_server,
			path,
			self.worldDbFile,
			crawl_videos=self.video_crawl_enabled,
			excludeDirList=self.excludeDirList,
			mockup_mode=self.debug_mockupimages,
			cross_shape_grow = self.cross_shape_grow,
			no_diagonal_grow = self.no_diagonal_grow,
			organic_grow = self.organic_grow,
			reach_out_ant_mode = self.reach_out_ant_mode,
		)
		self.crawler.run()

		self.image_server.start()

		self.running = True

		view_w_old_PL = -1
		view_h_old_PL = -1

		xy_dialog = None

		doubleclick_clock = pygame.time.Clock()  # clock for doubleclick left
		selection_clock = pygame.time.Clock()  # clock for last willfull selection click
		selection_clock_click_done = False

		self.world_overlook = None
		self.save_dialog = None

		while self.running:
			info = pygame.display.Info()
			view_w_PL, view_h_PL = info.current_w, info.current_h

			redraw = False

			for event in pygame.event.get():
				if event.type == pygame.QUIT:

					self.running = False

				if fap_table_view.edit_mode_enabled:
					if event.type == pygame.MOUSEMOTION and move_card:
						motion = pygame.mouse.get_rel()
						if current_edit_card != None:
							card = current_edit_card
						else:
							card = fap_table_view.get_card_at_pixel_pos(
								pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1]
							)
							current_edit_card = card
							if card != None:
								if fap_table_view.is_card_lower_corner(
									card,
									pygame.mouse.get_pos()[0],
									pygame.mouse.get_pos()[1],
								):
									card_resize_mode = True
						if card != None:
							current_fap_table.status_sync = FapTable.STATUS_CHANGED
							if card_resize_mode:
								width = card.width + (
									motion[0] * fap_table_view.card_step_per_pixel
								)
								if width >= FapTableCard.CARD_MINIMUM_SIZE:
									card.width = width
							else:
								card.x = card.x + (
									motion[0] * fap_table_view.card_step_per_pixel
								)
								card.y = card.y + (
									motion[1] * fap_table_view.card_step_per_pixel
								)
						card_moved = True
						redraw = True

					elif event.type == pygame.MOUSEBUTTONDOWN:
						if event.button == 1:

							if doubleclick_clock.tick() < RugiviMainApp.DOUBLECLICKTIME:
								pass

							motion = pygame.mouse.get_rel()  # clear relative movement
							move_card = True

						elif event.button == 2:
							fap_table_view.edit_mode_enabled = False
							redraw = True

					elif event.type == pygame.MOUSEBUTTONUP:
						if event.button == 1:
							move_card = False
							if card_moved:
								card_moved = False
								current_edit_card = None
								card_resize_mode = False
							else:
								pass

				else:
					if event.type == pygame.MOUSEMOTION and move_view:
						motion = pygame.mouse.get_rel()
						view.current_center_world_pos_x_P = (
							view.current_center_world_pos_x_P
							- int(motion[0] * view.height)
						)
						view.current_center_world_pos_y_P = (
							view.current_center_world_pos_y_P
							- int(motion[1] * view.height)
						)
						view_moved = True

					elif event.type == pygame.MOUSEBUTTONDOWN:
						if event.button == 1:
							if doubleclick_clock.tick() < RugiviMainApp.DOUBLECLICKTIME:
								view.selection.peek_enabled = (
									not view.selection.peek_enabled
								)
							motion = pygame.mouse.get_rel()  # clear relative movement
							move_view = True
						elif event.button == 3:
							# select clicked spot
							click_x_P = view.current_center_world_pos_x_P + int(
								(pygame.mouse.get_pos()[0] - int(view_w_PL / 2))
								* view.height
							)
							click_y_P = view.current_center_world_pos_y_P + int(
								(pygame.mouse.get_pos()[1] - int(view_h_PL / 2))
								* view.height
							)
							clicked_spot_x_S = int(click_x_P / World.SPOT_SIZE)
							if click_x_P < 0:
								clicked_spot_x_S -= 1
							clicked_spot_y_S = int(click_y_P / World.SPOT_SIZE)
							if click_y_P < 0:
								clicked_spot_y_S -= 1
							view.selection.x_S = clicked_spot_x_S
							view.selection.y_S = clicked_spot_y_S
							view.selection.update_selected_spot()
							redraw = True

							selection_clock.tick()
							selection_clock_click_done = True

							view.current_center_world_pos_x_P = (
								view.current_center_world_pos_x_P
								+ int(
									(pygame.mouse.get_pos()[0] - int(view_w_PL / 2))
									* view.height
								)
							)
							view.current_center_world_pos_y_P = (
								view.current_center_world_pos_y_P
								+ int(
									(pygame.mouse.get_pos()[1] - int(view_h_PL / 2))
									* view.height
								)
							)
						elif event.button == 2:
							fap_table_view.edit_mode_enabled = True

					elif event.type == pygame.MOUSEBUTTONUP:
						if event.button == 1:
							move_view = False
							if view_moved:
								view_moved = False
							else:
								# select clicked spot
								click_x_P = view.current_center_world_pos_x_P + int(
									(pygame.mouse.get_pos()[0] - int(view_w_PL / 2))
									* view.height
								)
								click_y_P = view.current_center_world_pos_y_P + int(
									(pygame.mouse.get_pos()[1] - int(view_h_PL / 2))
									* view.height
								)
								clicked_spot_x_S = int(click_x_P / World.SPOT_SIZE)
								if click_x_P < 0:
									clicked_spot_x_S -= 1
								clicked_spot_y_S = int(click_y_P / World.SPOT_SIZE)
								if click_y_P < 0:
									clicked_spot_y_S -= 1
								view.selection.x_S = clicked_spot_x_S
								view.selection.y_S = clicked_spot_y_S
								view.selection.update_selected_spot()
								redraw = True

								selection_clock.tick()
								selection_clock_click_done = True

					elif event.type == pygame.MOUSEWHEEL:
						if event.y != 0:
							if event.y * self.zoomDirection > 0:
								view.height = view.height / (
									1.2 + ((view.height / 20) * 0.1)
								)

								if selection_clock.tick() > 500:
									selection_clock_click_done = False

								if (
									(World.SPOT_SIZE / view.height < view_h_PL * 0.3)
									and (
										World.SPOT_SIZE / view.height < view_w_PL * 0.3
									)
								) or selection_clock_click_done:
									# move view further to the selection when zooming in
									center_of_selection_x_P = int(
										view.selection.x_S * World.SPOT_SIZE
										+ (World.SPOT_SIZE / 2)
									)
									center_of_selection_y_P = int(
										view.selection.y_S * World.SPOT_SIZE
										+ (World.SPOT_SIZE / 2)
									)
									if (
										view.selection.x_S
										!= view.current_center_world_pos_x_P
										/ World.SPOT_SIZE
										or view.selection.y_S
										!= view.current_center_world_pos_y_P
										/ World.SPOT_SIZE
									):
										move_x_PL = int(
											(
												center_of_selection_x_P
												- view.current_center_world_pos_x_P
											)
											/ (
												1
												+ (
													0.3
													* (
														1
														- (
															view.height
															/ view.max_height
														)
													)
												)
											)
										)
										move_y_PL = int(
											(
												center_of_selection_y_P
												- view.current_center_world_pos_y_P
											)
											/ (
												1
												+ (
													0.3
													* (
														1
														- (
															view.height
															/ view.max_height
														)
													)
												)
											)
										)
										view.current_center_world_pos_x_P = (
											view.current_center_world_pos_x_P
											+ move_x_PL
										)
										view.current_center_world_pos_y_P = (
											view.current_center_world_pos_y_P
											+ move_y_PL
										)

							else:
								view.height = view.height * (
									1.2 + ((view.height / 20) * 0.1)
								)

							redraw = True

						if view.height < 1.0:
							view.height = 1.0
						if view.height > view.max_height:
							view.height = view.max_height

				if event.type == pygame.KEYDOWN:
					if event.key == pygame.K_1:
						view.height = 1.0
						redraw = True
					elif event.key == pygame.K_2:
						view.height = (
							World.SPOT_SIZE
							/ ImageServer.QUALITY_PIXEL_SIZE[
								StreamedImage.QUALITY_SCREEN
							]
						)
						redraw = True
					elif event.key == pygame.K_3:
						view.height = (
							World.SPOT_SIZE
							/ ImageServer.QUALITY_PIXEL_SIZE[StreamedImage.QUALITY_GRID]
						)
						redraw = True
					elif event.key == pygame.K_4:
						view.height = (
							World.SPOT_SIZE
							/ ImageServer.QUALITY_PIXEL_SIZE[
								StreamedImage.QUALITY_THUMB
							]
						)
						redraw = True
					elif event.key == pygame.K_5:
						view.height = 190.0
						redraw = True
					elif event.key == pygame.K_6:
						view.height = 280.0
						redraw = True
					elif event.key == pygame.K_7:
						view.height = view.max_height
						redraw = True
					elif event.key == pygame.K_0:
						view.height = World.SPOT_SIZE / view_h_PL
						redraw = True
					elif event.key == pygame.K_p:
						self.crawler.pause_crawling = not self.crawler.pause_crawling
					elif event.key == pygame.K_o:
						self.image_server.paused = not self.image_server.paused
					elif event.key == pygame.K_i:
						self.show_info += 1
						if self.show_info > 2:
							self.show_info = 0
						redraw = True
					elif event.key == pygame.K_g:
						xy_dialog = Dialog_xy()
					elif event.key == pygame.K_c:
						infotext = ""
						if view.selection.get_selected_file() != None:
							if view.selection.image != None:
								if (
									view.selection.image.get_extended_attribute(
										"video_file"
									)
									!= None
								):
									video_filename = (
										view.selection.image.get_extended_attribute(
											"video_file"
										)
									)
									video_position = float(view.selection.image.get_extended_attribute("video_position"))  # type: ignore
									infotext = infotext + "Video file:\n"
									infotext = infotext + video_filename + "\n" # type: ignore
									infotext = infotext + "Parent directory of video file:\n"
									infotext = infotext + str(pathlib.Path(video_filename).parent.resolve()) + "\n" # type: ignore
									infotext = infotext + "Position (sec):\n"
									infotext = infotext + str(video_position) + "\n"
									infotext = infotext + "Still image in cache:\n"
									infotext = infotext + view.selection.image.original_file_path + "\n"
									infotext = infotext + "Parent directory of still image in cache:\n"
									infotext = infotext + str(pathlib.Path(view.selection.image.original_file_path).parent.resolve()) + "\n" # type: ignore
								else:
									infotext = infotext + "Image file:\n"
									infotext = infotext + view.selection.get_selected_file() + "\n"
									infotext = infotext + "Parent directory of image file:\n"
									infotext = infotext + str(pathlib.Path(view.selection.get_selected_file()).parent.resolve()) + "\n" # type: ignore

								infotext = infotext +"Selected Spot:\n"
								infotext = infotext + str(view.selection.x_S)
								infotext = infotext + ","
								infotext = infotext + str(view.selection.y_S) + "\n"
								infotext = infotext + "Ordered Quality: " + str(view.selection.image.get_ordered_quality()) + ", Available Quality: " + str(view.selection.image.get_available_quality()) + "\n"
								infotext = infotext + "State: " + view.selection.image.state + "\n"

							clipboard_dialog = Dialog_copy_clipboard("Info about selection",infotext)
					elif event.key == pygame.K_j:
						last_x_S = math.floor(
							view.current_center_world_pos_x_P / World.SPOT_SIZE
						)
						last_y_S = math.floor(
							view.current_center_world_pos_y_P / World.SPOT_SIZE
						)

						next_x_S = last_x_S
						next_y_S = last_y_S
						number_of_sub_moves = RugiviMainApp.JUMP_NUMBER_OF_SUBMOVES
						while number_of_sub_moves > 0:
							number_of_sub_moves = number_of_sub_moves - 1
							next_x_S = last_x_S + random.randint(
								-1 * RugiviMainApp.JUMP_SUBMOVE_DISTANCE_S,
								RugiviMainApp.JUMP_SUBMOVE_DISTANCE_S,
							)
							next_y_S = last_y_S + random.randint(
								-1 * RugiviMainApp.JUMP_SUBMOVE_DISTANCE_S,
								RugiviMainApp.JUMP_SUBMOVE_DISTANCE_S,
							)
							frame = self.world.get_frame_at_S(next_x_S, next_y_S)
							if frame != None:
								last_x_S = next_x_S
								last_y_S = next_y_S
						view.current_center_world_pos_x_P = (
							last_x_S * World.SPOT_SIZE + int(World.SPOT_SIZE / 2)
						)
						view.current_center_world_pos_y_P = (
							last_y_S * World.SPOT_SIZE + int(World.SPOT_SIZE / 2)
						)
						redraw = True

					elif event.key == pygame.K_n:
						if view.selection.get_selected_file() != None:
							if view.selection.image != None:
								if (
									view.selection.image.get_extended_attribute(
										"video_file"
									)
									!= None
								):
									video_filename = (
										view.selection.image.get_extended_attribute(
											"video_file"
										)
									)
									video_position = float(view.selection.image.get_extended_attribute("video_position"))  # type: ignore
									if self.video_vlc_enabled:
										if self.video_vlc_seek_position:
											self.open_video_with_vlc(
												video_filename, position=video_position
											)
										else:
											self.open_video_with_vlc(video_filename)
									else:
										self.open_file(video_filename)
								else:
									self.open_file(view.selection.get_selected_file())

					elif event.key == pygame.K_t:
						if view.selection.get_selected_file() != None:
							fapelsystem_dir = dir_helper.get_module_dir("fapelsystem")
							if fapelsystem_dir != None:
								subprocess.Popen(
									[
										python_executable,
										fapelsystem_dir + "/fapel_tagger.py",
										view.selection.get_selected_file(),  # type: ignore
									]
								)
					elif event.key == pygame.K_s:
						if view.selection.get_selected_file() != None:
							fapelsystem_dir = dir_helper.get_module_dir("fapelsystem")
							if fapelsystem_dir != None:
								subprocess.Popen(
									[
										python_executable,
										fapelsystem_dir + "/fapel_fap_set.py",
										view.selection.get_selected_file(),  # type: ignore
									]
								)

					elif event.key == pygame.K_e:
						if self.world_overlook == None:
							self.save_dialog = Dialog_save_file()

					elif event.key == pygame.K_LEFT:
						self.fapTables.switch_previous()
						current_fap_table = self.fap_table_manager.get_fap_table_by_dir(
							self.fapTables.get_current_fap_table_dir()
						)
						fap_table_view.set_current_fap_table(current_fap_table)
						redraw = True
					elif event.key == pygame.K_RIGHT:
						self.fapTables.switch_next()
						current_fap_table = self.fap_table_manager.get_fap_table_by_dir(
							self.fapTables.get_current_fap_table_dir()
						)
						fap_table_view.set_current_fap_table(current_fap_table)
						redraw = True
					elif event.key == pygame.K_UP:
						self.fapTables.switch_up()
						current_fap_table = self.fap_table_manager.get_fap_table_by_dir(
							self.fapTables.get_current_fap_table_dir()
						)
						fap_table_view.set_current_fap_table(current_fap_table)
						redraw = True
					elif event.key == pygame.K_DOWN:
						self.fapTables.switch_down()
						current_fap_table = self.fap_table_manager.get_fap_table_by_dir(
							self.fapTables.get_current_fap_table_dir()
						)
						fap_table_view.set_current_fap_table(current_fap_table)
						redraw = True

			if (view_h_PL != view_h_old_PL) or (view_w_PL != view_w_old_PL):
				view_h_old_PL = view_h_PL
				view_w_old_PL = view_w_PL
				redraw = True

			if xy_dialog != None and xy_dialog.result != None:
				print("Going to", xy_dialog.result)
				view.current_center_world_pos_x_P = xy_dialog.result[
					0
				] * World.SPOT_SIZE + int(World.SPOT_SIZE / 2)
				view.current_center_world_pos_y_P = xy_dialog.result[
					1
				] * World.SPOT_SIZE + int(World.SPOT_SIZE / 2)
				xy_dialog = None

			if self.save_dialog != None and self.save_dialog.result != None:
				self.world_overlook_filename = str(self.save_dialog.result)
				self.save_dialog = None
				if self.world_overlook_filename != "":
					print("Filename for world map:", self.world_overlook_filename)
					self.world_overlook = WorldOverlook(
						self.world, self.world_overlook_filename
					)
					self.world_overlook.run()

			if (
				(not view.selection.is_visible())
				or (not World.SPOT_SIZE / view.height < view_h_PL * 0.7)
				or (not World.SPOT_SIZE / view.height < view_w_PL * 0.7)
			):
				# move selection to center when it's out of view or the image is almost full screen
				click_x_P = view.current_center_world_pos_x_P
				click_y_P = view.current_center_world_pos_y_P

				clicked_spot_x_S = int(click_x_P / World.SPOT_SIZE)
				if click_x_P < 0:
					clicked_spot_x_S -= 1
				clicked_spot_y_S = int(click_y_P / World.SPOT_SIZE)
				if click_y_P < 0:
					clicked_spot_y_S -= 1

				view.selection.x_S = clicked_spot_x_S
				view.selection.y_S = clicked_spot_y_S
				view.selection.update_selected_spot()

				# and switch off peek, when selection moves by itself
				view.selection.peek_enabled = False

				redraw = True

			if redraw:
				view.redrawtoken += 1
				if view.redrawtoken == 256:
					view.redrawtoken = 0

			view.draw_grid = self.show_info > 1

			if not fap_table_view.edit_mode_enabled:
				view.draw_view(self.display, 0, 0, view_w_PL, view_h_PL)
			else:
				self.display.fill((0, 0, 0, 0))
			fap_table_view.draw_fap_table_view(self.display, 0, 0, view_w_PL, view_h_PL)

			if self.show_info > 0:
				memory_usage_system = int(
					psutil.Process().memory_info().rss / (1024 * 1024)
				)
				memory_usage_image_server = int(
					self.image_server.calculate_memory_usage() / (1024 * 1024)
				)

				if self.show_info > 1:
					status.writeln("FPS: " + str(int(clock.get_fps())))
					status.writeln(
						"Center: "
						+ str(int(view.current_center_world_pos_x_P))
						+ ","
						+ str(int(view.current_center_world_pos_y_P))
						+ " Pixel; Spot: "
						+ str(
							math.floor(
								view.current_center_world_pos_x_P / World.SPOT_SIZE
							)
						)
						+ ","
						+ str(
							math.floor(
								view.current_center_world_pos_y_P / World.SPOT_SIZE
							)
						)
						+ " Height: "
						+ str(view.height)
					)

				status.writeln(
					"Selected Spot: "
					+ str(view.selection.x_S)
					+ ","
					+ str(view.selection.y_S)
				)

				if self.show_info > 1:
					status.writeln(
						"Disk Access Total Loaded: File: "
						+ str(self.image_server._total_disk_loaded)
						+ " DB: "
						+ str(self.image_server._total_database_loaded)
					)
					status.writeln(
						"DB Size: "
						+ str(self.image_server.image_server_database.image_db_size)
					)
					status.writeln(
						"ImgDrawn: "
						+ str(view.performance_images_drawn)
						+ " maxDrawRounds:"
						+ str(view.max_draw_rounds)
					)
					status.writeln("MemP: " + str(memory_usage_system) + " MB")
					status.writeln("MemI: " + str(memory_usage_image_server) + " MB")
					status.writeln("ImgServer: " + self.image_server.get_status_line())
					status.writeln(
						"World loaded: Chunks: "
						+ str(self.world.count_chunks_in_memory())
						+ " Frames: "
						+ str(self.world.count_frames())
					)
					status.writeln("Crawler Status: " + self.crawler.status)
					status.writeln("Crawler Dir: " + self.crawler.current_dir)
				if view.selection.get_selected_file() != None:
					status.writeln(
						"Selected Media: " + view.selection.get_selected_file()  # type: ignore
					)
				else:
					status.writeln("Selected Image: -none-")
				status.writeln("Queue: " + str(self.image_server.get_queue_size()))

				if self.world_overlook != None:
					status.writeln("World Overlook: " + self.world_overlook.status)

				if self.show_info > 1:
					status.writeln("")
					status.writeln("Keys: 1-7 zoom, 0 zoom fit, n open file")
					status.writeln("      i toggle info, o/p pause imgserver/crawl")
					status.writeln("      t tag, s add to set, e generate map png")

				status.draw(self.display)

			if (
				self.image_server._total_database_loaded
				+ self.image_server._total_disk_loaded
				< 10 and not self.debug_mockupimages
			):

				font = pygame.font.SysFont("monospace", 40)
				label = font.render("starting... please wait!", True, (255, 255, 255))
				self.display.blit(label, (30, 30))
				mp = int(time() % 4)
				label2 = font.render((" " * mp) + ".", True, (255, 80, 207))
				self.display.blit(label2, (30, 80))
				# pygame.display.flip()

			if self.running == False:
				self.display.fill((100, 100, 100, 0))

				font = pygame.font.SysFont("monospace", 50)
				label = font.render(
					"closing databases... please wait!", True, (0, 0, 0)
				)
				self.display.blit(label, (30, 30))

			pygame.display.flip()

			if (
				self.image_server.get_queue_size() > 200
				and not move_view
				and not fap_table_view.edit_mode_enabled
			):
				sleep(0.08)

			clock.tick(80)  # limits fps

		font = pygame.font.SysFont("monospace", 50)
		# label = font.render(".", 1, (0, 0, 0))
		label = font.render(".", True, (0, 0, 0))
		self.display.blit(label, (30, 80))
		pygame.display.flip()

		if self.world_overlook != None:
			print("Stopping world overlook")
			self.world_overlook.stop()

		print("Stopping image crawler")
		self.crawler.stop()
		self.display.blit(label, (30 + 40 * 1, 80))
		pygame.display.flip()

		print("Stopping FapTableManager")
		self.fap_table_manager.stop()
		self.display.blit(label, (30 + 40 * 2, 80))
		pygame.display.flip()

		print("Stopping image server")
		self.image_server.stop()
		self.display.blit(label, (30 + 40 * 3, 80))
		pygame.display.flip()
		print("Closing pygame window")
		pygame.quit()
		print("Bye bye")
		sys.exit(0)


print("RuGiVi Image World Viewer")

if __name__ == "__main__":
	app = RugiviMainApp()
	app.run()


def main() -> NoReturn:
	app = RugiviMainApp()
	app.run()
