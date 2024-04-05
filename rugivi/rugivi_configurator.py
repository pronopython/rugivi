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

import abc
import configparser
import pathlib
import platform

import sys
from tkinter import Checkbutton, IntVar, Tk
from tkinter import Label
from tkinter import Frame
from tkinter import Button
from tkinter import StringVar
from tkinter import Entry
from tkinter import N
from tkinter import E
from tkinter import S
from tkinter import W
from tkinter import LEFT
from tkinter import RIGHT
from tkinter import BOTH
from tkinter import YES
from tkinter import Listbox
from tkinter import Scrollbar

import tkinter as tk

# import tkinter.ttk as ttk
from tkinter import filedialog
import os
from typing import NoReturn

from rugivi import config_file_handler as config_file_handler
from rugivi import dir_helper as dir_helper

from pyshortcuts import make_shortcut


class SelectionSingleItem:
	__metaclass__ = abc.ABCMeta

	def __init__(
		self,
		configParser: config_file_handler.ConfigFileHandler,
		description,
		configGroup,
		configItem,
	) -> None:
		self.configParser: config_file_handler.ConfigFileHandler = configParser
		self.description = description
		self.configGroup = configGroup
		self.configItem = configItem

		self.initValue = None
		self.loadInitValue()

	@abc.abstractmethod
	def loadInitValue() -> None:
		pass


class SelectionFolder(SelectionSingleItem):
	def __init__(
		self,
		parent,
		configParser: config_file_handler.ConfigFileHandler,
		description,
		configGroup,
		configItem,
		fg="black",
	) -> None:
		super().__init__(configParser, description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1, weight=1)
		Label(self.frame, text=description,fg=fg).grid(column=0, row=0, sticky=W)
		self.dirText = StringVar(self.frame, self.initValue)
		self.dirText.trace_add("write", self.valueChanged)
		Entry(self.frame, textvariable=self.dirText).grid(column=1, row=0, sticky=W + E)
		Button(self.frame, text="Select", command=self.buttonClicked).grid(
			column=2, row=0, sticky=E
		)

	def loadInitValue(self) -> None:
		self.initValue = self.configParser.get_directory_path(
			self.configGroup, self.configItem, ""
		)

	def buttonClicked(self) -> None:
		selected_folder = filedialog.askdirectory()
		if selected_folder != "" and len(selected_folder) > 0:
			selected_folder = os.path.abspath(selected_folder)
			self.dirText.set(selected_folder)

	def valueChanged(self, *args) -> None:
		self.configParser.change_config()[self.configGroup][
			self.configItem
		] = self.dirText.get()

	def getFrame(self) -> Frame:
		return self.frame


class SelectionFile(SelectionSingleItem):
	def __init__(
		self, parent, configParser, description, configGroup, configItem, filetypes
	) -> None:
		super().__init__(configParser, description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1, weight=1)
		self.filetypes = filetypes
		Label(self.frame, text=description).grid(column=0, row=0, ipadx=5, sticky=W)
		self.dirText = StringVar(self.frame, self.initValue)
		self.dirText.trace_add("write", self.valueChanged)
		Entry(self.frame, textvariable=self.dirText).grid(
			column=1, row=0, ipadx=5, sticky=W + E
		)
		Button(self.frame, text="Select", command=self.buttonClicked).grid(
			column=2, row=0, ipadx=5, sticky=E
		)

	def loadInitValue(self) -> None:
		self.initValue = self.configParser.get_directory_path(
			self.configGroup, self.configItem, ""
		)

	def buttonClicked(self) -> None:
		filename = filedialog.askopenfilename(filetypes=self.filetypes)
		self.dirText.set(filename)
		self.configParser.change_config()[self.configGroup][self.configItem] = filename

	def valueChanged(self, *args) -> None:
		self.configParser.change_config()[self.configGroup][
			self.configItem
		] = self.dirText.get()

	def getFrame(self) -> Frame:
		return self.frame


class SelectionBoolean(SelectionSingleItem):
	def __init__(
		self, parent, configParser, description, configGroup, configItem, fg="black"
	) -> None:
		super().__init__(configParser, description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1, weight=1)
		Label(self.frame, text=description, fg=fg).grid(column=0, row=0, ipadx=5, sticky=W)
		self.button = Button(
			self.frame, text=str(self.initValue), command=self.buttonClicked
		)
		self.button.grid(column=2, row=0, ipadx=5, sticky=E)
		self.value = self.initValue

	def loadInitValue(self) -> None:
		self.initValue = self.configParser.get_boolean(
			self.configGroup, self.configItem
		)

	def buttonClicked(self) -> None:
		self.value = not self.value
		self.button.configure(text=str(self.value))
		self.configParser.change_config()[self.configGroup][self.configItem] = str(
			self.value
		)

	def getFrame(self) -> Frame:
		return self.frame


class SelectionInteger(SelectionSingleItem):
	def __init__(
		self, parent, configParser, description, configGroup, configItem
	) -> None:
		super().__init__(configParser, description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1, weight=1)
		Label(self.frame, text=description).grid(column=0, row=0, ipadx=5, sticky=W)
		self.dirText = StringVar(self.frame, str(self.initValue))
		self.dirText.trace_add("write", self.valueChanged)
		Entry(self.frame, textvariable=self.dirText).grid(
			column=1, row=0, ipadx=5, sticky=W + E
		)

	def loadInitValue(self) -> None:
		self.initValue = self.configParser.get_int(self.configGroup, self.configItem)

	def valueChanged(self, *args) -> None:
		self.configParser.change_config()[self.configGroup][
			self.configItem
		] = self.dirText.get()

	def getFrame(self) -> Frame:
		return self.frame


class SelectionMultiItem(SelectionSingleItem):
	def __init__(
		self, parent, configParser, description, configGroup, configItem
	) -> None:
		super().__init__(configParser, description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1, weight=1)

		Label(self.frame, text=description).grid(column=0, row=0, rowspan=2, sticky=W)

		listboxframe = Frame(self.frame)

		self.listbox = Listbox(listboxframe, height=5)
		self.listbox.pack(side=LEFT, fill=BOTH, expand=YES)
		# self.listbox.grid(column=1,row=0, rowspan=2,sticky=W+E)

		scrollbar = Scrollbar(listboxframe)
		scrollbar.pack(side=RIGHT, fill=BOTH)
		self.listbox.config(yscrollcommand=scrollbar.set)
		scrollbar.config(command=self.listbox.yview)

		listboxframe.grid(column=1, row=0, rowspan=2, sticky=W + E)

		Button(self.frame, text="+", command=self.buttonClickedAdd).grid(
			column=2, row=0, sticky=E
		)
		Button(self.frame, text="-", command=self.buttonClickedRemove).grid(
			column=2, row=1, sticky=E
		)

		for item in self.items:
			self.listbox.insert(tk.END, item)

	def loadInitValue(self) -> None:
		if len(self.configParser.items(self.configGroup)) > 0:
			keys, self.items = zip(*self.configParser.items(self.configGroup))
		else:
			self.items = []

	def buttonClickedAdd(self) -> None:
		pass

	def buttonClickedRemove(self) -> None:
		self.listbox.delete(tk.ANCHOR)
		self.valueChanged()

	def getFrame(self) -> Frame:
		return self.frame

	def valueChanged(self) -> None:
		self.configParser.change_config()[self.configGroup].clear()
		for pos, item in enumerate(self.listbox.get(0, tk.END)):
			self.configParser.change_config()[self.configGroup][
				self.configItem + str(pos)
			] = item


class SelectionMultiFolder(SelectionMultiItem):
	def __init__(
		self, parent, configParser, description, configGroup, configItem
	) -> None:
		super().__init__(parent, configParser, description, configGroup, configItem)

	def buttonClickedAdd(self) -> None:
		selected_folder = filedialog.askdirectory()
		if selected_folder != ():
			selected_folder = os.path.abspath(selected_folder)
			self.listbox.insert(tk.END, selected_folder)
			self.valueChanged()


class ConfigApp:
	def __init__(self, apply_and_start=False) -> None:

		print("RuGiVi Configurator")

		self.configDir = dir_helper.get_config_dir("RuGiVi")
		self.configParser: config_file_handler.ConfigFileHandler = (
			config_file_handler.ConfigFileHandler(
				os.path.join(self.configDir, "rugivi.conf"), create_if_missing=True
			)
		)

		self.config_migrated = False
		self.migrate_old_conf(self.configParser)

		self.root = Tk()
		self.root.geometry("800x650")
		self.root.title("RuGiVi Configurator")

		frm = Frame(self.root)
		frm.grid(sticky=N + S + W + E)
		frm.columnconfigure(0, weight=1)

		row = 0

		Label(frm, text="Crawler settings").grid(column=0, row=row, sticky=W)
		row += 1

		# ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
		itfo = SelectionFolder(
			frm, self.configParser, "Images & videos root directory", "world", "crawlerRootDir", fg="blue"
		)
		itfo.getFrame().grid(column=0, row=row, ipadx=10, padx=10, sticky=W + E)
		row += 1

		filetypes = (("SQLite files", "*.sqlite"), ("All files", "*.*"))
		itfo = SelectionFile(
			frm,
			self.configParser,
			"Crawler World DB File",
			"world",
			"worldDB",
			filetypes,
		)
		itfo.getFrame().grid(column=0, row=row, ipadx=10, padx=10, sticky=W + E)
		row += 1

		Label(
			frm,
			text="You must use a new World DB File or delete the old one when changing root directory",
			fg="black",
		).grid(column=0, row=row,ipadx=10, padx=10,sticky=W)
		row += 1

		Label(frm, text="Thumb Database settings").grid(column=0, row=row, sticky=W)
		row += 1

		itfo = SelectionFile(
			frm, self.configParser, "Thumb DB File", "thumbs", "thumbDB", filetypes
		)
		itfo.getFrame().grid(column=0, row=row, ipadx=10, padx=10, sticky=W + E)
		row += 1

		Label(frm, text="Video settings").grid(column=0, row=row, sticky=W)
		row += 1

		itfo = SelectionBoolean(
			frm, self.configParser, "Enable video crawling", "world", "crawlvideos", fg="blue"
		)
		itfo.getFrame().grid(column=0, row=row, ipadx=10, padx=10, sticky=W + E)
		row += 1

		itfo = SelectionFolder(
			frm,
			self.configParser,
			"Video still cache directory",
			"cache",
			"cacherootdir",
		)
		itfo.getFrame().grid(column=0, row=row, ipadx=10, padx=10, sticky=W + E)
		row += 1

		itfo = SelectionBoolean(
			frm, self.configParser, "Play video with VLC", "videoplayback", "vlcenabled"
		)
		itfo.getFrame().grid(column=0, row=row, ipadx=10, padx=10, sticky=W + E)
		row += 1

		Label(frm, text="GUI settings").grid(column=0, row=row, sticky=W)
		row += 1

		itfo = SelectionBoolean(
			frm,
			self.configParser,
			"Reverse Scroll Wheel Zoom",
			"control",
			"reversescrollwheelzoom",
		)
		itfo.getFrame().grid(column=0, row=row, ipadx=10, padx=10, sticky=W + E)
		row += 1

		itfo = SelectionInteger(
			frm, self.configParser, "Status font size", "fonts", "statusfontsize"
		)
		itfo.getFrame().grid(column=0, row=row, ipadx=10, padx=10, sticky=W + E)
		row += 1

		Label(frm, text="FapTables").grid(column=0, row=row, sticky=W)
		row += 1

		itfo = SelectionMultiFolder(
			frm, self.configParser, "FapTable parent dirs", "fapTableParentDirs", "dir"
		)
		itfo.getFrame().grid(column=0, row=row, ipadx=10, padx=9, sticky=W + E)
		row += 1

		itfo = SelectionMultiFolder(
			frm, self.configParser, "FapTable single dirs", "fapTableSingleDirs", "dir"
		)
		itfo.getFrame().grid(column=0, row=row, ipadx=10, padx=10, sticky=W + E)
		row += 1

		Label(
			frm,
			text="Getting started? Just change the blue entries to fit your setup!",
			fg="blue",
		).grid(column=0, row=row, sticky=E)
		row += 1

		if self.config_migrated and not apply_and_start:
			Label(
				frm,
				text="Config migrated & new items added. Make sure to apply the config!",
				fg="red",
			).grid(column=0, row=row, sticky=E)
			row += 1

		bframe = Frame(frm)

		self.start_menu_entry = IntVar(bframe,value=1)

		Checkbutton(
			bframe, text="create start menu entries", variable=self.start_menu_entry
		).grid(column=0, row=0, sticky=W)

		if apply_and_start:
			text_apply_and="Apply and start"
		else:
			text_apply_and="Apply and exit"
		Button(bframe, text=text_apply_and, command=self.actionSaveAndExit).grid(
			column=1, row=0, ipadx=5, sticky=E
		)
		Button(bframe, text="Cancel", command=self.actionExitWithoutSave).grid(
			column=2, row=0, ipadx=5, sticky=E
		)
		bframe.grid(column=0, row=row, sticky=E)
		row += 1

		Label(
			frm,
			text="'Apply' will also create necessary files and directories!",
			fg="black",
		).grid(column=0, row=row, sticky=E)
		row += 1

		frm.pack(expand=True, fill=BOTH)

	def run(self) -> None:
		self.root.mainloop()

	def actionSaveAndExit(self) -> NoReturn:
		self.configParser.change_config()["configuration"]["configured"] = "True"
		self.configParser.write_changed_config()
		self.create_directories()
		if self.start_menu_entry.get() == 1:
			self._create_start_menu_entries()
		self.root.quit()
		self.root.destroy()
		#exit()

	def actionExitWithoutSave(self) -> NoReturn:
		self.root.quit()
		self.root.destroy()
		#exit()

	def is_windows(self) -> bool:
		if platform.system() == "Windows":
			return True
		else:
			return False

	def _migrate_check_and_add_entry(self, configParser, group, key, initvalue):
		entry_present = True
		section_missing = False
		try:
			configParser.config_parser.get(group, key)
		except configparser.NoOptionError:
			entry_present = False
		except configparser.NoSectionError:
			entry_present = False
			section_missing = True
		if not entry_present:
			print(
				"Migrate old config to new one: adding [",
				group,
				"]",
				key,
				"=",
				initvalue,
			)
			if section_missing:
				self.configParser.change_config().add_section(group)
			self.configParser.change_config()[group][key] = initvalue
			self.config_migrated = True

	def migrate_old_conf(self, configParser):

		# empty or older => v0.4.0

		if self.is_windows():
			self._migrate_check_and_add_entry(
				configParser, "world", "crawlerRootDir", "~\\Pictures\\"
			)
		else:
			self._migrate_check_and_add_entry(
				configParser, "world", "crawlerRootDir", "~"
			)

		self._migrate_check_and_add_entry(
			configParser, "world", "crawlerExcludeDirList", ""
		)

		if self.is_windows():
			self._migrate_check_and_add_entry(
				configParser,
				"world",
				"worldDB",
				"~\\AppData\\Roaming\\RuGiVi\\chunks.sqlite",
			)
		else:
			self._migrate_check_and_add_entry(
				configParser, "world", "worldDB", "~/.local/share/rugivi/chunks.sqlite"
			)

		self._migrate_check_and_add_entry(configParser, "world", "crawlvideos", "False")

		self._migrate_check_and_add_entry(
			configParser, "world", "crossshapegrow", "False"
		)
		self._migrate_check_and_add_entry(
			configParser, "world", "nodiagonalgrow", "True"
		)
		self._migrate_check_and_add_entry(configParser, "world", "organicgrow", "True")
		self._migrate_check_and_add_entry(
			configParser, "world", "reachoutantmode", "True"
		)

		if self.is_windows():
			self._migrate_check_and_add_entry(
				configParser,
				"thumbs",
				"thumbDB",
				"~\\AppData\\Roaming\\RuGiVi\\thumbs.sqlite",
			)
		else:
			self._migrate_check_and_add_entry(
				configParser, "thumbs", "thumbDB", "~/.local/share/rugivi/thumbs.sqlite"
			)

		if self.is_windows():
			self._migrate_check_and_add_entry(
				configParser,
				"cache",
				"cacherootdir",
				"~\\AppData\\Roaming\\RuGiVi\\cache",
			)
		else:
			self._migrate_check_and_add_entry(
				configParser, "cache", "cacherootdir", "~/.local/share/rugivi/cache"
			)

		self._migrate_check_and_add_entry(
			configParser, "videoframe", "jpgquality", "65"
		)
		self._migrate_check_and_add_entry(
			configParser, "videoframe", "maxsizeenabled", "False"
		)
		self._migrate_check_and_add_entry(configParser, "videoframe", "maxsize", "800")
		self._migrate_check_and_add_entry(
			configParser, "videoframe", "removeletterbox", "True"
		)

		if self.is_windows():
			self._migrate_check_and_add_entry(
				configParser,
				"videoplayback",
				"vlcbinary",
				"C:/Program Files/VideoLAN/VLC/vlc.exe",
			)
		else:
			self._migrate_check_and_add_entry(
				configParser, "videoplayback", "vlcbinary", "vlc"
			)

		self._migrate_check_and_add_entry(
			configParser, "videoplayback", "vlcenabled", "False"
		)
		self._migrate_check_and_add_entry(
			configParser, "videoplayback", "vlcseekposition", "True"
		)

		self._migrate_check_and_add_entry(
			configParser, "control", "reverseScrollWheelZoom", "False"
		)

		if self.is_windows():
			self._migrate_check_and_add_entry(
				configParser, "control", "pythonexecutable", "python"
			)
		else:
			self._migrate_check_and_add_entry(
				configParser, "control", "pythonexecutable", "python3"
			)

		self._migrate_check_and_add_entry(configParser, "control", "showinfo", "0")

		if self.is_windows():
			self._migrate_check_and_add_entry(
				configParser,
				"fapTableParentDirs",
				"dir1",
				"~\\Documents\\fapelsystem\\Fapsets",
			)
			self._migrate_check_and_add_entry(
				configParser,
				"fapTableSingleDirs",
				"dir1",
				"~\\Documents\\fapelsystem\\Notice",
			)
		else:
			self._migrate_check_and_add_entry(
				configParser, "fapTableParentDirs", "dir1", "~/fapelsystem/Fapsets"
			)
			self._migrate_check_and_add_entry(
				configParser, "fapTableSingleDirs", "dir1", "~/fapelsystem/Notice"
			)

		self._migrate_check_and_add_entry(configParser, "fonts", "statusFontSize", "24")

		self._migrate_check_and_add_entry(
			configParser, "configuration", "configured", "False"
		)

		self._migrate_check_and_add_entry(configParser, "debug", "vlcverbose", "False")
		self._migrate_check_and_add_entry(configParser, "debug", "cv2verbose", "False")
		self._migrate_check_and_add_entry(
			configParser, "debug", "mockupimages", "False"
		)

	def _createDirTree(self, dir):
		dir = dir_helper.expand_home_dir(dir)
		print("Creating directory:", dir)
		pathlib.Path(dir).mkdir(parents=True, exist_ok=True)

	def create_directories(self):
		self._createDirTree(
			os.path.dirname(
				self.configParser.get_directory_path("world", "worldDB", "")
			)
		)
		self._createDirTree(
			self.configParser.get_directory_path("cache", "cacherootdir", "")
		)

	def _create_start_menu_entries(self):

		if self.is_windows():
			print("Creating app shortcut...")
			packagedir = os.path.dirname(os.path.realpath(__file__))
			sc_icon = os.path.join(packagedir, "icon.ico")
			
			# TODO future pyshortcuts versions > 1.9.0 might contain the feature that noexe=True can be used to directly call "rugivi" instead of rugivi.py
			make_shortcut(
				script=os.path.join(packagedir, "..\\..\\..\\Scripts\\rugivi.exe"),
				name="RuGiVi",
				icon=sc_icon,
				terminal=False,
				desktop=False,
				working_dir=None,
			)

			print("Creating configurator shortcut...")
			make_shortcut(
				script=os.path.join(packagedir, "..\\..\\..\\Scripts\\rugivi_configurator.exe"),
				name="RuGiVi Configurator",
				icon=sc_icon,
				terminal=False,
				desktop=False,
				working_dir=None,
			)

		else:
			print("Creating app shortcut...")
			packagedir = os.path.dirname(os.path.realpath(__file__))
			sc_icon = os.path.join(packagedir, "icon.png")

			# TODO future pyshortcuts versions > 1.9.0 might contain the feature that noexe=True can be used to directly call "rugivi" instead of rugivi.py
			make_shortcut(
				script=dir_helper.expand_home_dir("~/.local/bin/rugivi"),
				name="RuGiVi",
				icon=sc_icon,
				terminal=False,
				desktop=False,
				working_dir=None,
			)

			print("Creating configurator shortcut...")
			make_shortcut(
				script=dir_helper.expand_home_dir("~/.local/bin/rugivi_configurator"),
				name="RuGiVi Configurator",
				icon=sc_icon,
				terminal=False,
				desktop=False,
				working_dir=None,
			)


def main() -> None:
	app = ConfigApp()
	app.run()
