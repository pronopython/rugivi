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
from tkinter import Tk
from tkinter import Label
from tkinter import Entry
import tkinter.simpledialog
import threading
from typing import Any
from tkinter import filedialog
import gc


class TkinterWrapper:
	__metaclass__ = abc.ABCMeta

	def __init__(self) -> None:
		self.result = None
		self.run()

	def showDialog(self) -> None:
		self.root = tkinter.Tk()
		self.root.withdraw()
		self.dialog = self.createDialogWindow()
		self.setResult()

		# The following code deletes all Tkinter objects
		# to avoid errors like
		# - Tcl_AsyncDelete: cannot find async handler
		# - Tcl_AsyncDelete: async handler deleted by the wrong thread
		#
		# destroy Tkinter main thread
		self.root.destroy()
		# delete all references to Tkinter ressources
		del self.root
		del self.dialog
		# call garbage collection to clear out all Tkinter objects
		gc.collect()

	def run(self):
		self.threadLoader = threading.Thread(target=self.showDialog, args=())
		self.threadLoader.start()

	@abc.abstractmethod
	def createDialogWindow(self) -> Any:
		pass

	@abc.abstractmethod
	def setResult(self) -> Any:
		pass


class Dialog_xy_tkwindow(tkinter.simpledialog.Dialog):
	def body(self, master) -> Any:

		Label(master, text="Spot X:").grid(row=0)
		Label(master, text="Spot Y:").grid(row=1)

		self.e1 = Entry(master)
		self.e2 = Entry(master)

		self.e1.grid(row=0, column=1)
		self.e2.grid(row=1, column=1)
		return self.e1  # initial focus

	def apply(self) -> None:
		first = self.e1.get()
		second = self.e2.get()
		self.result = (int(first), int(second))


class Dialog_xy(TkinterWrapper):
	def createDialogWindow(self) -> Dialog_xy_tkwindow:
		return Dialog_xy_tkwindow(self.root, "Go to spot")

	def setResult(self) -> Any:
		self.result = self.dialog.result  # type: ignore


class Dialog_save_file(TkinterWrapper):
	def createDialogWindow(self) -> str:
		fn = filedialog.asksaveasfilename(
			defaultextension=".png",
			filetypes=(("png image", "*.png"), ("All Files", "*.*")),
		)
		return fn

	def setResult(self) -> Any:
		result = self.dialog  # type: ignore
		if str(type(result)) == "<class 'tuple'>":
			result = ""
		if result == None:
			result = ""
		result = result.strip()
		# on linux, file dialog sometimes returns "()" when cancel is clicked...
		if str(result) == "()":
			result = ""
		self.result = result
