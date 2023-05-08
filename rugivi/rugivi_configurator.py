#!/usr/bin/env python3
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
VERSION = "0.1.0-alpha"
#
##############################################################################################
#
# Copyright (C) 2023 PronoPython
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

#macos:
#brew install python-tk

from tkinter import *
import tkinter as tk
#import tkinter.ttk as ttk
from tkinter import filedialog
import os

from rugivi import config_file_handler as config_file_handler
from rugivi import dir_helper as dir_helper


class SelectionSingleItem:

	def __init__(self,configParser,description,configGroup,configItem):
		self.configParser = configParser
		self.description = description
		self.configGroup = configGroup
		self.configItem = configItem

		self.initValue = None
		self.loadInitValue()

	def loadInitValue():
		pass



class SelectionFolder(SelectionSingleItem):

	def __init__(self,parent,configParser,description,configGroup, configItem):
		super().__init__(configParser,description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1,weight=1)
		Label(self.frame, text=description).grid(column=0, row=0,sticky=W)
		self.dirText = StringVar(self.frame,self.initValue)
		self.dirText.trace_add("write",self.valueChanged)
		Entry(self.frame,textvariable=self.dirText).grid(column=1, row=0,sticky=W+E)
		Button(self.frame, text="Select", command=self.buttonClicked).grid(column=2,row=0,sticky=E)

	def loadInitValue(self):
		self.initValue = self.configParser.getDir(self.configGroup,self.configItem, "")


	def buttonClicked(self):
		selected_folder = filedialog.askdirectory()
		if selected_folder != "":
			selected_folder = os.path.abspath(selected_folder)
			self.dirText.set(selected_folder)


	def valueChanged(self,*args):
		self.configParser.changeConfig()[self.configGroup][self.configItem] = self.dirText.get()



	def getFrame(self):
		return self.frame



class SelectionFile(SelectionSingleItem):

	def __init__(self,parent,configParser,description,configGroup, configItem,filetypes):
		super().__init__(configParser,description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1,weight=1)
		self.filetypes = filetypes
		Label(self.frame, text=description).grid(column=0, row=0,ipadx=5,sticky=W)
		self.dirText = StringVar(self.frame,self.initValue)
		self.dirText.trace_add("write",self.valueChanged)
		Entry(self.frame,textvariable=self.dirText).grid(column=1, row=0,ipadx=5,sticky=W+E)
		Button(self.frame, text="Select", command=self.buttonClicked).grid(column=2,row=0,ipadx=5,sticky=E)

	def loadInitValue(self):
		self.initValue = self.configParser.getDir(self.configGroup,self.configItem, "")

	def buttonClicked(self):
		filename = filedialog.askopenfilename(filetypes = self.filetypes)
		self.dirText.set(filename)
		self.configParser.changeConfig()[self.configGroup][self.configItem] = filename

	def valueChanged(self,*args):
		self.configParser.changeConfig()[self.configGroup][self.configItem] = self.dirText.get()

	def getFrame(self):
		return self.frame



class SelectionBoolean(SelectionSingleItem):

	def __init__(self,parent,configParser,description,configGroup, configItem):
		super().__init__(configParser,description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1,weight=1)
		Label(self.frame, text=description).grid(column=0, row=0,ipadx=5,sticky=W)
		self.button = Button(self.frame, text=str(self.initValue), command=self.buttonClicked)
		self.button.grid(column=2,row=0,ipadx=5,sticky=E)
		self.value = self.initValue

	def loadInitValue(self):
		self.initValue = self.configParser.getBoolean(self.configGroup,self.configItem)

	def buttonClicked(self):
		self.value = not self.value
		self.button.configure(text=str(self.value))
		self.configParser.changeConfig()[self.configGroup][self.configItem] = str(self.value)


	def getFrame(self):
		return self.frame



class SelectionInteger(SelectionSingleItem):

	def __init__(self,parent,configParser,description,configGroup, configItem):
		super().__init__(configParser,description, configGroup, configItem)

		self.frame = Frame(parent)
		self.frame.columnconfigure(1,weight=1)
		Label(self.frame, text=description).grid(column=0, row=0,ipadx=5,sticky=W)
		self.dirText = StringVar(self.frame,str(self.initValue))
		self.dirText.trace_add("write",self.valueChanged)
		Entry(self.frame,textvariable=self.dirText).grid(column=1, row=0,ipadx=5,sticky=W+E)

	def loadInitValue(self):
		self.initValue = self.configParser.getInt(self.configGroup,self.configItem)

	def valueChanged(self,*args):
		self.configParser.changeConfig()[self.configGroup][self.configItem] = self.dirText.get()

	def getFrame(self):
		return self.frame



class SelectionMultiItem(SelectionSingleItem):

	def __init__(self,parent,configParser,description,configGroup,configItem):
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

	def loadInitValue(self):
		if len(self.configParser.items(self.configGroup)) > 0:
			keys, self.items = zip(*self.configParser.items(self.configGroup))
		else:
			self.items = []

	def buttonClickedAdd(self):
		pass

	def buttonClickedRemove(self):
		self.listbox.delete(tk.ANCHOR)
		self.valueChanged()

	def getFrame(self):
		return self.frame

	def valueChanged(self):
		self.configParser.changeConfig()[self.configGroup].clear()
		for pos, item in enumerate(self.listbox.get(0,tk.END)):
			self.configParser.changeConfig()[self.configGroup][self.configItem+str(pos)] = item




class SelectionMultiFolder(SelectionMultiItem):


	def __init__(self,parent,configParser,description,configGroup,configItem):
		super().__init__(parent,configParser,description, configGroup, configItem)


	def buttonClickedAdd(self):
		selected_folder = filedialog.askdirectory()
		if selected_folder != "":
			selected_folder = os.path.abspath(selected_folder)
			self.listbox.insert(tk.END,selected_folder)
			self.valueChanged()

class ConfigApp:


	def __init__(self):

		print("RuGiVi Configurator")


		self.configDir = dir_helper.getConfigDir("RuGiVi")
		self.configParser = config_file_handler.FapelSystemConfigFile(os.path.join(self.configDir,"rugivi.conf"))


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

	def run(self):
		self.root.mainloop()

	def actionSaveAndExit(self):
		self.configParser.changeConfig()["configuration"]["configured"] = "True"
		self.configParser.writeChangedConfig()
		exit()

	def actionExitWithoutSave(self):
		exit()


def main():
	app = ConfigApp()
	app.run()

