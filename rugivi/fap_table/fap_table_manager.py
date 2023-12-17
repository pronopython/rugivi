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
from time import sleep, time

from rugivi.thread_safe_list import *
from rugivi.fap_table.fap_table import *
import random
from pathlib import Path
import json

from rugivi.image_service.streamed_image import StreamedImage
from rugivi.image_service.image_server import ImageServer


class FapTableManager:

	SYNC_TABLE_EVERY_SECONDS = 5

	def __init__(self, image_server: ImageServer):

		self.fap_tables = ThreadSafeList()

		self.image_server = image_server
		self.running = True
		self.run()

	def run(self):
		self.thread = threading.Thread(target=self.manager_loop, args=())
		self.thread.daemon = True  # so these threads get killed when program exits
		self.thread.start()

	def open_fap_table(self, path) -> FapTable:
		# TODO check if already loaded in manager
		path = Path(path).absolute()
		fap_table = FapTable(path)
		self.fap_tables.append(fap_table)
		# is there a faptable.pos?
		return fap_table

	def open_fap_table_parent_dir(self, path) -> FapTable:
		last_fap_table = None
		for root, d_names, f_names in os.walk(path):

			for d_name in d_names:
				last_fap_table = self.open_fap_table(os.path.join(root, d_name))

			break
		return last_fap_table  # type: ignore

	def get_fap_table_by_dir(self, path) -> FapTable:
		if path == None:
			return None  # type: ignore
		path = Path(path).absolute()
		for fap_table in self.fap_tables.getCopyOfList():
			if fap_table.table_dir == path:
				return fap_table
		return None  # type: ignore

	def get_previous_fap_table(self, currentFapTable) -> FapTable:
		fap_table = self.fap_tables.getCopyOfList()
		i = fap_table.index(currentFapTable)
		i = i - 1
		if i == -1:
			# wrap around
			i = len(fap_table) - 1
		return fap_table[i]

	def get_next_fap_table(self, current_fap_table) -> FapTable:
		fap_table = self.fap_tables.getCopyOfList()
		i = fap_table.index(current_fap_table)
		i = i + 1
		if i == len(fap_table):
			# wrap around
			i = 0
		return fap_table[i]

	def manager_loop(self):

		self.manager_loop_running = True
		print("FapTableManager started")
		while self.running:

			sleep(3)
			fap_table : FapTable = None # type: ignore
			for fap_table in self.fap_tables.getCopyOfList() :

				# TODO in view??? displayed?

				if fap_table.status_sync == FapTable.STATUS_SAVED:
					pass  # TODO anything??
				elif fap_table.status_sync == FapTable.STATUS_NEW:
					pass  # TODO anything??
				elif fap_table.status_sync == FapTable.STATUS_LOAD:

					cards_json = []
					json_filename = os.path.join(fap_table.table_dir, "ftpositions.json")

					if os.path.isfile(json_filename):
						print("Loading fapTable json:", json_filename)
						with open(json_filename, encoding="utf-8") as f:
							cards_json = json.load(f)
						for cardJson in cards_json:
							card = FapTableCard()
							card.load_from_json_dictionary(cardJson, fap_table.table_dir)
							card.image = self.image_server.create_streamed_image(
								card.image_path, StreamedImage.QUALITY_ORIGINAL
							)
							fap_table.cards.append(card)
							fap_table.status_sync = FapTable.STATUS_SAVED
					else:
						fap_table.status_sync = FapTable.STATUS_NEW

				if (
					fap_table.last_sync_time + FapTableManager.SYNC_TABLE_EVERY_SECONDS
					< time()
				):

					fap_table.last_sync_time = time()

					if fap_table.status_sync == FapTable.STATUS_CHANGED:
						save_cards = fap_table.cards.copy()
						cards_json = []
						for card in save_cards:
							cards_json.append(card.get_json_dictionary())

						json_filename = os.path.join(
							fap_table.table_dir, "ftpositions.json"
						)

						print("Saving fapTable json:", json_filename)
						with open(json_filename, "w", encoding="utf-8") as f:
							json.dump(cards_json, f, ensure_ascii=False, indent=4)

						fap_table.status_sync = FapTable.STATUS_SAVED

					if fap_table.is_displayed:
						# loadsync
						# print("Syncing FT:",fapTable.tableDir)
						for root, d_names, f_names in os.walk(fap_table.table_dir):

							f_names = [
								file
								for file in f_names
								if file.lower().endswith(
									(".jpg", ".jpeg", ".gif", ".png", ".tif")
								)
							]

							previous_cards = fap_table.cards.copy()
							new_files = []
							found_cards = []

							for f_name in f_names:
								found = False
								card : FapTableCard = None # type: ignore
								for card in fap_table.cards:
									f_path = os.path.join(root, f_name)
									if card.image_path == f_path:
										found_cards.append(card)
										previous_cards.remove(card)
										found = True
										break
								if not found:
									new_files.append(f_name)

							if len(new_files) > 0 or len(previous_cards) > 0:
								print(
									"Syncing FT: "
									+ str(fap_table.table_dir)
									+ " adding "
									+ str(len(new_files))
									+ " and removing "
									+ str(len(previous_cards))
								)
								fap_table.status_sync = FapTable.STATUS_CHANGED

							# add new cards
							for filename in new_files:
								f_path = os.path.join(root, filename)
								card = FapTableCard(f_path)
								fap_table.cards.append(card)

								card.image = self.image_server.create_streamed_image(
									f_path, StreamedImage.QUALITY_ORIGINAL
								)
								card.x = random.uniform(
									0.01, 0.99 - FapTableCard.CARD_INITIAL_SIZE
								)
								card.y = random.uniform(
									0.01,
									FapTable.TABLE_INITIAL_MAXIMUM_HEIGHT
									- FapTableCard.CARD_INITIAL_SIZE,
								)

							# TODO remove vacant cards

							break

				# new? then init table
				# saved? load positions + thumbs
				# displayed? load images hi res
				# 		AND sync dir every 5 sec if new image present (or one deleted)!
				# changed? save positions from time to time
				# out of display save positions now

				# also watch tables:
				# =====SETS============
				# |   |   |   |   |   |
				# =====ct============     NO too many images!!!

		print("FapTableManager loop exited")
		self.manager_loop_running = False

	def stop(self):
		self.running = False

		while self.manager_loop_running:
			sleep(0.06)
