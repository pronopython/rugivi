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

from threading import Lock


class ThreadSafeList():
	def __init__(self):
		self._list = list()
		self._lock = Lock()

	def append(self, value):
		with self._lock:
			self._list.append(value)

	def pop(self):
		with self._lock:
			return self._list.pop()

	def get(self, index):
		with self._lock:
			return self._list[index]

	def length(self):
		with self._lock:
			return len(self._list)

	def getCopyOfList(self):
		with self._lock:
			return self._list.copy()
