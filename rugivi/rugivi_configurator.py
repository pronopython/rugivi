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
#import tkinter.ttk as ttk
from tkinter import filedialog
import os
from typing import NoReturn

from rugivi import config_file_handler as config_file_handler
from rugivi import dir_helper as dir_helper


class SelectionSingleItem:
	__metaclass__ = abc.ABCMeta
	
	def __init__(self,configParser:config_file_handler.ConfigFileHandler,description,configGroup,configItem) -> None:
		self.configParser:config_file_handler.ConfigFileHandler = configParser
		self.description = description
		self.configGroup = configGroup
		self.configItem = configItem

		self.initValue = None
		self.loadInitValue()

	@abc.abstractmethod
	def loadInitValue() -> None:
		pass



class SelectionFolder(SelectionSingleItem):

	def __init__(self,parent,configParser:config_file_handler.ConfigFileHandler,description,configGroup, configItem) -> None:
		super().__init__(configParser,description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1,weight=1)
		Label(self.frame, text=description).grid(column=0, row=0,sticky=W)
		self.dirText = StringVar(self.frame,self.initValue)
		self.dirText.trace_add("write",self.valueChanged)
		Entry(self.frame,textvariable=self.dirText).grid(column=1, row=0,sticky=W+E)
		Button(self.frame, text="Select", command=self.buttonClicked).grid(column=2,row=0,sticky=E)

	def loadInitValue(self) -> None:
		self.initValue = self.configParser.get_directory_path(self.configGroup,self.configItem, "")


	def buttonClicked(self) -> None:
		selected_folder = filedialog.askdirectory()
		if selected_folder != "":
			selected_folder = os.path.abspath(selected_folder)
			self.dirText.set(selected_folder)


	def valueChanged(self,*args) -> None:
		self.configParser.change_config()[self.configGroup][self.configItem] = self.dirText.get()



	def getFrame(self) -> Frame:
		return self.frame



class SelectionFile(SelectionSingleItem):

	def __init__(self,parent,configParser,description,configGroup, configItem,filetypes) -> None:
		super().__init__(configParser,description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1,weight=1)
		self.filetypes = filetypes
		Label(self.frame, text=description).grid(column=0, row=0,ipadx=5,sticky=W)
		self.dirText = StringVar(self.frame,self.initValue)
		self.dirText.trace_add("write",self.valueChanged)
		Entry(self.frame,textvariable=self.dirText).grid(column=1, row=0,ipadx=5,sticky=W+E)
		Button(self.frame, text="Select", command=self.buttonClicked).grid(column=2,row=0,ipadx=5,sticky=E)

	def loadInitValue(self) -> None:
		self.initValue = self.configParser.get_directory_path(self.configGroup,self.configItem, "")

	def buttonClicked(self) -> None:
		filename = filedialog.askopenfilename(filetypes = self.filetypes)
		self.dirText.set(filename)
		self.configParser.change_config()[self.configGroup][self.configItem] = filename

	def valueChanged(self,*args) -> None:
		self.configParser.change_config()[self.configGroup][self.configItem] = self.dirText.get()

	def getFrame(self) -> Frame:
		return self.frame



class SelectionBoolean(SelectionSingleItem):

	def __init__(self,parent,configParser,description,configGroup, configItem) -> None:
		super().__init__(configParser,description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1,weight=1)
		Label(self.frame, text=description).grid(column=0, row=0,ipadx=5,sticky=W)
		self.button = Button(self.frame, text=str(self.initValue), command=self.buttonClicked)
		self.button.grid(column=2,row=0,ipadx=5,sticky=E)
		self.value = self.initValue

	def loadInitValue(self) -> None:
		self.initValue = self.configParser.get_boolean(self.configGroup,self.configItem)

	def buttonClicked(self) -> None:
		self.value = not self.value
		self.button.configure(text=str(self.value))
		self.configParser.change_config()[self.configGroup][self.configItem] = str(self.value)


	def getFrame(self) -> Frame:
		return self.frame



class SelectionInteger(SelectionSingleItem):

	def __init__(self,parent,configParser,description,configGroup, configItem) -> None:
		super().__init__(configParser,description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1,weight=1)
		Label(self.frame, text=description).grid(column=0, row=0,ipadx=5,sticky=W)
		self.dirText = StringVar(self.frame,str(self.initValue))
		self.dirText.trace_add("write",self.valueChanged)
		Entry(self.frame,textvariable=self.dirText).grid(column=1, row=0,ipadx=5,sticky=W+E)

	def loadInitValue(self) -> None:
		self.initValue = self.configParser.get_int(self.configGroup,self.configItem)

	def valueChanged(self,*args) -> None:
		self.configParser.change_config()[self.configGroup][self.configItem] = self.dirText.get()

	def getFrame(self) -> Frame:
		return self.frame



class SelectionMultiItem(SelectionSingleItem):

	def __init__(self,parent,configParser,description,configGroup,configItem) -> None:
		super().__init__(configParser,description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1,weight=1)

		Label(self.frame, text=description).grid(column=0, row=0,rowspan=2,sticky=W)

		listboxframe = Frame(self.frame)

		self.listbox = Listbox(listboxframe,height=5)
		self.listbox.pack(side=LEFT,fill=BOTH,expand=YES)
		#self.listbox.grid(column=1,row=0, rowspan=2,sticky=W+E)

		scrollbar = Scrollbar(listboxframe)
		scrollbar.pack(side=RIGHT,fill=BOTH)
		self.listbox.config(yscrollcommand = scrollbar.set)
		scrollbar.config(command = self.listbox.yview)

		listboxframe.grid(column=1,row=0, rowspan=2,sticky=W+E)
		
		Button(self.frame, text="+", command=self.buttonClickedAdd).grid(column=2,row=0,sticky=E)
		Button(self.frame, text="-", command=self.buttonClickedRemove).grid(column=2,row=1,sticky=E)

		for item in self.items:
			self.listbox.insert(tk.END,item)

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
		for pos, item in enumerate(self.listbox.get(0,tk.END)):
			self.configParser.change_config()[self.configGroup][self.configItem+str(pos)] = item




class SelectionMultiFolder(SelectionMultiItem):


	def __init__(self,parent,configParser,description,configGroup,configItem) -> None:
		super().__init__(parent,configParser,description, configGroup, configItem)


	def buttonClickedAdd(self) -> None:
		selected_folder = filedialog.askdirectory()
		if selected_folder != ():
			selected_folder = os.path.abspath(selected_folder)
			self.listbox.insert(tk.END,selected_folder)
			self.valueChanged()

class ConfigApp:


	def __init__(self) -> None:

		print("RuGiVi Configurator")


		self.configDir = dir_helper.get_config_dir("RuGiVi")
		self.configParser : config_file_handler.ConfigFileHandler = config_file_handler.ConfigFileHandler(os.path.join(self.configDir,"rugivi.conf"))


		self.root = Tk()
		self.root.geometry("800x460")
		self.root.title("RuGiVi Configurator")


		frm = Frame(self.root)
		frm.grid(sticky=N+S+W+E)
		frm.columnconfigure(0,weight =1) 

		Label(frm, text="Crawler settings").grid(column=0, row=0,sticky=W)

		#ttk.Button(frm, text="Quit", command=root.destroy).grid(column=1, row=0)
		itfo = SelectionFolder(frm,self.configParser,"Crawler root directory","world","crawlerRootDir")
		itfo.getFrame().grid(column=0,row=1,ipadx=10,padx=10,sticky=W+E)


		filetypes = (("SQLite files", "*.sqlite"),("All files", "*.*") )
		itfo = SelectionFile(frm,self.configParser,"Crawler World DB File","world","worldDB",filetypes)
		itfo.getFrame().grid(column=0,row=2,ipadx=10,padx=10,sticky=W+E)

		Label(frm, text="Thumb Database settings").grid(column=0, row=3,sticky=W)

		itfo = SelectionFile(frm,self.configParser,"Thumb DB File","thumbs","thumbDB",filetypes)
		itfo.getFrame().grid(column=0,row=4,ipadx=10,padx=10,sticky=W+E)


		Label(frm, text="GUI settings").grid(column=0, row=5,sticky=W)

		itfo = SelectionBoolean(frm,self.configParser,"Reverse Scroll Wheel Zoom","control","reversescrollwheelzoom")
		itfo.getFrame().grid(column=0,row=6,ipadx=10,padx=10,sticky=W+E)

		itfo = SelectionInteger(frm,self.configParser,"Status font size","fonts","statusfontsize")
		itfo.getFrame().grid(column=0,row=7,ipadx=10,padx=10,sticky=W+E)


		Label(frm, text="FapTables").grid(column=0, row=8,sticky=W)

		itfo = SelectionMultiFolder(frm,self.configParser,"FapTable parent dirs","fapTableParentDirs","dir")
		itfo.getFrame().grid(column=0,row=9,ipadx=10,padx=9,sticky=W+E)

		itfo = SelectionMultiFolder(frm,self.configParser,"FapTable single dirs","fapTableSingleDirs","dir")
		itfo.getFrame().grid(column=0,row=10,ipadx=10,padx=10,sticky=W+E)

		bframe = Frame(frm)
		Button(bframe, text="Save and exit", command=self.actionSaveAndExit).grid(column=0,row=0,ipadx=5,sticky=E)
		Button(bframe, text="Exit without save", command=self.actionExitWithoutSave).grid(column=1,row=0,ipadx=5,sticky=E)
		bframe.grid(column=0,row=11,sticky=E)



		frm.pack(expand=True, fill=BOTH)

	def run(self) -> None:
		self.root.mainloop()

	def actionSaveAndExit(self) -> NoReturn:
		self.configParser.change_config()["configuration"]["configured"] = "True"
		self.configParser.write_changed_config()
		exit()

	def actionExitWithoutSave(self) -> NoReturn:
		exit()


def main() -> None:
	app = ConfigApp()
	app.run()

