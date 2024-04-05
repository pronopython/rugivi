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

from setuptools import setup

setup(name='rugivi',
	version='0.5.0-alpha.post1',
	description='RuGiVi - Adult Media Landscape Browser',
	long_description='RuGiVi enables you to fly over your image and video collection and view thousands of images and video frames at once. Zoom in and out from one image to small thumbnails with your mousewheel in seconds. All images are grouped as you have them on your disk and arranged in a huge landscape. RuGiVi can work with hundred thousand of images at once.',
	url='https://github.com/pronopython/rugivi',
	author='pronopython',
	author_email='pronopython@proton.me',
	license='GNU GENERAL PUBLIC LICENSE V3',
	packages=['rugivi','rugivi.crawlers.first_organic','rugivi.fap_table','rugivi.image_database_service','rugivi.image_service','rugivi.world_database_service','rugivi.world_things','rugivi.exports'],
	package_data={'rugivi':['*']},
	include_package_data=True,
	zip_safe=False,
	install_requires=['pygame>=2.5.2','psutil>=5.9.8','numpy>=1.26.3','sqlitedict>=2.1.0','pyshortcuts>=1.9.0','Pillow>=9.0.1','opencv-python-headless>=4.9.0.80'],
	entry_points={
        'gui_scripts': [
            'rugivi_configurator=rugivi.rugivi_configurator:main'
		],
        'console_scripts': [
            'rugivi_printModuleDir=rugivi.print_module_dir:printModuleDir',
            'rugivi=rugivi.rugivi:main',
			'rugivi_image_cache_maintenance=rugivi.rugivi_image_cache_maintenance:main'
		]
    	}
    )

