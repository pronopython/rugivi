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

from tkinter import *
import tkinter.simpledialog
import threading

class TkinterWrapper():

	def __init__(self):
		self.result = None
		self.run()

	def showDialog(self):
		self.root = tkinter.Tk()
		self.root.withdraw()
		self.dialog = self.createDialogWindow()
		#print(self.dialog.result)
		self.result = self.dialog.result


	def run(self):
		self.threadLoader = threading.Thread(target=self.showDialog, args=())
		#self.threadLoader.daemon = True # so these threads get killed when program exits
		self.threadLoader.start()

	def createDialogWindow(self):
		pass


class Dialog_xy_tkwindow(tkinter.simpledialog.Dialog):

	def body(self, master):

		Label(master, text="Spot X:").grid(row=0)
		Label(master, text="Spot Y:").grid(row=1)

		self.e1 = Entry(master)
		self.e2 = Entry(master)

		self.e1.grid(row=0, column=1)
		self.e2.grid(row=1, column=1)
		return self.e1 # initial focus

	def apply(self):
		first = self.e1.get()
		second = self.e2.get()
		#print( first, second )
		self.result = (int(first), int(second))


class Dialog_xy(TkinterWrapper):

	def createDialogWindow(self):
		return Dialog_xy_tkwindow(self.root,"Go to spot")






#tkwr = Dialog_xy()

#while True:
#	print("Result:",tkwr.result)





