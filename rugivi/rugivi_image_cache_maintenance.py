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


import time
import os

# Import pygame, hide welcome message because it messes with
# status output
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "hide"

import pathlib
import sys
from typing import NoReturn
from sqlitedict import SqliteDict

from rugivi.world_database_service.world_database import ChunkSaveObject
from rugivi import config_file_handler as config_file_handler
from rugivi import dir_helper as dir_helper

class ImageCacheMaintenance():



	def __init__(self) -> None:
		self.db :  SqliteDict= None # type: ignore
		self.worldDbFile = "chunks.sqlite"
		self.cache_base_dir = "./cache"
		self.cache_files_total_size = 0

		self.worldDbFiles = []

		self.cache_files = []

		self.orphant_files = []




	def run(self):
		self.configDir = dir_helper.get_config_dir("RuGiVi")
		self.configParser = config_file_handler.ConfigFileHandler(
			os.path.join(self.configDir, "rugivi.conf")
		)

		self.configured = self.configParser.get_boolean("configuration", "configured")

		if not self.configured:
			print("Not configured")
			print("Please configure RuGiVi and save the settings with the RuGiVi Configurator before running it")
			sys.exit(0)


		self.worldDbFile = self.configParser.get_directory_path(
			"world", "worldDB", self.worldDbFile
		)

		self.cache_base_dir = self.configParser.get_directory_path(
			"cache", "cacherootdir", self.cache_base_dir
		)







		self.open_world_db(self.worldDbFile)

		self.generate_world_db_file_list()
		self.generate_cache_file_list()
		self.calculate_cache_size()

		print("World DB files:",len(self.worldDbFiles))
		print("Cache files   :",len(self.cache_files))
		print("Cache size:",int(self.cache_files_total_size/(1024*1024)),"MB")

		self.generate_orphant_file_list()

		print("Orphant files :",len(self.orphant_files))

		if len(self.orphant_files) > 0:
			if len(sys.argv) > 1 and sys.argv[1] == "-c":
				self.delete_orphant_files()
			else:
				print("NOTHING WAS CHANGED YET!")
				print("RUN THIS TOOL AGAIN with '-c' to move orphant files and clean up the cache!")
		else:
			print("No orphant files. Nothing to clean up. Cache is healthy.")

	def open_world_db(self,crawler_db_file):
		self.db = SqliteDict(crawler_db_file)
		


	def generate_world_db_file_list(self):

		print("Reading Chunks from Database:",end="",flush=True)

		for item in self.db.items(): # type: ignore
			if str(item[0]).startswith("(") and str(item[0]).endswith(")"):
				tupel = item[1]
				if tupel == None:
					continue

				print(".",end="",flush=True)
				chunk_save_object = ChunkSaveObject()
				chunk_save_object.from_tupel(tupel)

				for filepath in chunk_save_object.spots_filepath_list:
					if len(filepath) > 0:
						#print(filepath)
						self.worldDbFiles.append(filepath)
		print("done")



	def generate_cache_file_list(self):
		print("Scanning files of cache:",end="",flush=True)
		every = 5000
		for root, d_names, f_names in os.walk(self.cache_base_dir):
			if root.find("trash_") > -1:
				print("")
				print("Warning: There is already a trash folder present:",root)
				print("")
				continue
			for f_name in f_names:
				if f_name.endswith(".jpg"):
					file = os.path.join(root, f_name)
					#print(file)
					self.cache_files.append(file)
					every -= 1
					if every <= 0:
						print(".",end="",flush=True)
						every = 5000
		print("done")

	def calculate_cache_size(self):
		print("Gathering information on files in cache:",end="",flush=True)
		every = 5000
		self.cache_files_total_size = 0
		for file in self.cache_files:
			self.cache_files_total_size += os.path.getsize(file)
			every -= 1
			if every <= 0:
				print(".",end="",flush=True)
				every = 5000
		print("done")


	def generate_orphant_file_list(self):
		print("Finding orphant cache files:",end="",flush=True)
		every = 5000
		for file in self.cache_files:
			if file not in self.worldDbFiles:
				self.orphant_files.append(file)
				every -= 1
				if every <= 0:
					print(".",end="",flush=True)
					every = 5000
		print("done")


	def delete_orphant_files(self):

		foldername = "trash_" + time.strftime("%Y%m%d_%H%M%S")

		trashbase = os.path.abspath(os.path.join(self.cache_base_dir, foldername))

		pathlib.Path(trashbase).mkdir(parents=True, exist_ok=True)

		moved_files = 0

		for file in self.orphant_files:
			# Precaution: Check if file path lies within cache dir
			if os.path.exists(file) and file.startswith(self.cache_base_dir):
				filename = (os.path.basename(file))
				newname =  os.path.join(trashbase, filename)
				# Precaution: never overwrite
				if os.path.exists(newname):
					print("Panic: Destination file",newname,"already exists! Abort")
					sys.exit()
				os.rename(file,newname)
				moved_files += 1
			else:
				print("Panic: File",file,"not found or not in cache! Abort")
				sys.exit()

		print(moved_files, "file(s) moved to trash:",trashbase)
		print("Check these files if they are ok to be deleted and then delete the 'trash_*' folder manually.")

if __name__ == "__main__":
	app = ImageCacheMaintenance()
	app.run()


def main() -> NoReturn: # type: ignore
	app = ImageCacheMaintenance()
	app.run()
