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

import gc
import math
import os
import time
import cv2
from threading import Lock

class VideoStillGenerator:

	def __init__(self, jpg_quality=75, max_dimension=(None, None), remove_letterbox=False) -> None:  # type: ignore
		self.jpg_quality = jpg_quality  # 0-100, default of cv2 = 90
		self.max_dimension = max_dimension
		self.remove_letterbox = remove_letterbox
		#self._lock = Lock()
		#self._lock2 = Lock()

		#self.vcs = {}
		#self.vcs_time = {}
		#self.vcs_queue = []

	'''
	def get_vc_for_videofile(self, videofile):
		with self._lock2:
			if videofile in self.vcs:
				self.vcs_queue.remove(videofile)
				self.vcs_queue.insert(0,videofile)
				self.vcs_time[videofile] = time.time()
				print("VC Cache:",len(self.vcs_queue),videofile)
				return self.vcs[videofile]
			else:
				if len(self.vcs_queue) >= 40:
					videofile_to_remove = self.vcs_queue.pop()
					the_vcs = self.vcs.pop(videofile_to_remove, None)
					the_vcs.release()
					videofile_to_remove.release()
					print("VC destr:",len(self.vcs_queue),videofile_to_remove)

				
				#to_be_removed = []
				#for vf, last_access in self.vcs_time:
				#	if last_access + 60*5 < time.time():
				#		to_be_removed.append(vf)
				#for vf in to_be_removed:
				#		the_vcs = self.vcs.pop(vf, None)
				#		the_vcs.release()
				#		self.vcs_time.pop(vf,None)
				#		self.vcs_queue.remove(vf)
				#		vf.release()
				#		print("VC destr:",len(self.vcs_queue),vf)
				

				new_vcs = cv2.VideoCapture(videofile)
				self.vcs_queue.insert(0,videofile)
				self.vcs[videofile] = new_vcs
				self.vcs_time[videofile] = time.time()
				print("VC New  :",len(self.vcs_queue),videofile)
				return new_vcs
	'''


	def __image_resize(
		self, image, width=None, height=None, inter=cv2.INTER_AREA, upscale=True
	):  # -> Any:
		dim = None
		(h, w) = image.shape[:2]
		if width is None and height is None:
			return image
		elif width is None:
			if h <= height:
				return image
			r = height / float(h) # type: ignore
			dim = (int(w * r), height)
		elif height is None:
			if w <= width:
				return image
			r = width / float(w) # type: ignore
			dim = (width, int(h * r))
		else:
			if w <= width and h <= height:
				return image
			aspect_source = h / w
			aspect_dest = height / width
			if aspect_source > aspect_dest:
				r = height / float(h)
				dim = (int(w * r), height)
			else:
				r = width / float(w)
				dim = (width, int(h * r))

		resized = cv2.resize(image, dim, interpolation=inter) # type: ignore
		return resized


	def analyze_and_get_positions(self, videofile):

		#print("Video:" + videofile)
		#with self._lock:
		try:
			#video = self.get_vc_for_videofile(videofile)
			video = cv2.VideoCapture(videofile)
			if not video.isOpened():
				#video.release # save some memory
				#del video
				#gc.collect()

				return []

			fps = video.get(cv2.CAP_PROP_FPS)
			frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
			duration = frame_count / fps

			#print("Duration:" + str(duration))

			positions = []


			FINAL_DISTANCE = 15  # seconds
			REACH_EXPONENT = -0.04  # to lim
			OVERALL_OFFSET = 0
			distance = FINAL_DISTANCE - FINAL_DISTANCE * math.exp(
				REACH_EXPONENT * (duration - OVERALL_OFFSET)
			)
			local_offset = distance / 2

			current_position = OVERALL_OFFSET + local_offset
			position_number = 0
			while current_position < duration:
				positions.append(float(current_position))
				current_position += distance
				position_number += 1

			#video.release
			#del video
			#gc.collect()
			return positions

		except cv2.error as e:
			#print("cv2.error:", e)
			return []
		except Exception as e:
			#print("Exception:", e)
			return []



	def create_and_write_still_image(self, videofile, position, output_file):


		video = None
		#buffer = None
		image = None
		#with self._lock:
		try:
			#print(videofile,"1",position,time.time())
			#video = self.get_vc_for_videofile(videofile)
			video = cv2.VideoCapture(videofile, apiPreference=cv2.CAP_FFMPEG) # TODO use ffmpeg faster? how to install?
			if not video.isOpened():
				video.release # save some memory
				#del video
				#gc.collect()
				#cv2.destroyAllWindows() 
				return []
			#print(videofile,"2",position,time.time())
			#fps = video.get(cv2.CAP_PROP_FPS)
			#print(videofile,"3a",position,time.time())
			#frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
			#print(videofile,"3b",position,time.time())
			#duration = frame_count / fps
			#print(videofile,"3c",position,time.time())
			video.set(cv2.CAP_PROP_POS_MSEC, position * 1000) # this is slow! (~2-3 sec)
			#print(videofile,"3d",position,time.time())
			hasFrames, image = video.read()
			#print(videofile,"4",position,time.time())
			if hasFrames:

				image_resized = self.__image_resize(
					image,
					width=self.max_dimension[0],
					height=self.max_dimension[1],
					upscale=False,
				)
				#del image
				image = image_resized

				if self.remove_letterbox:
					# remove black borders / letterbox
					gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
					_,thresh = cv2.threshold(gray,10,255,cv2.THRESH_BINARY)
					x,y,w,h = cv2.boundingRect(thresh)
					if w > 10 and h > 10: # prevent cropping of black images
						image = image[y:y+h,x:x+w]



				# using buffer and imencode to avoid naming the file ".jpg"
				#success, buffer = cv2.imencode(
				#	".jpg", image, [cv2.IMWRITE_JPEG_QUALITY, self.jpg_quality]
				#)

				# never overwrite!
				if not os.path.isfile(output_file):
					#buffer.tofile(output_file)

					# will fail to write when path does not exist!
					image_written = cv2.imwrite(output_file, image, [int(cv2.IMWRITE_JPEG_QUALITY), self.jpg_quality])
					#print("wrote",output_file, success,"from","'"+videofile+"'")
					#video.release # save some memory
					#image.release
					#cv2.destroyAllWindows() 
					#del video
					#del image
					#del buffer
					#gc.collect()
					#print(videofile,"5",position,time.time())
					return image_written
				else:
					print("Cache file exists! Panic!")

					
					#video.release # save some memory
					#image.release
					#del image
					#del video
					#del buffer
					#gc.collect()
					return False
			#video.release
			return False
		except cv2.error as e:
			#print("cv2.error:", e)

			#if video != None:
				#video.release # save some memory
			#if image != None:
			#	image.release
			#del video
			#del image
			#del buffer
			#gc.collect()


			return False
		except Exception as e:
			#print("Exception:", e)
			#if video != None:
			#	video.release # save some memory
			#if image != None:
			#	image.release
			#del video
			#del image
			#del buffer
			#gc.collect()
			return False

