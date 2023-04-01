# RuGiVi - Adult media landscape browser

RuGiVi enables you to fly over your image collection and view thousands of images at once. Zoom in and out from one image to small thumbnails with your mousewheel in seconds. All images are grouped as you have them on your disk and arranged in a huge landscape. RuGiVi can work with hundred thousand of images at once.

RuGiVi integrates fully into the [Fapel-System](https://github.com/pronopython/fapel-system), so you can travel trough your collection and tag images as you fly over them!

Fly over thumbnails and zoom in on any image anytime in an instant!

> :eggplant: :sweat_drops: *Note: All sample images on this page are censored*

![](img/7.jpg)

Zoom in (screenshot is obviously censored ;-) )

![](img/0.jpg)

And zoom out

![](img/1.jpg)

Left doubleclick enables a peepy preview.
Every rectangle is one image which you can zoom into.
Images within one directory are always placed randomly next to each other in an organic fashion. You also clearly can see different image directories: Ones which contain a mix of different images (random colors) and ones with one photo set (uniform color).

![](img/5.png)

RuGiVi saves all generated thumbnails in a database and can load these on the fly at the next session.
Here you can see chunks (rectangular blocks of 32 x 32 pictures) being loaded from thumb database (on this system at around 800-1000 thumbs per second).
The pattern like structure between pictures and red empty spots on the right is RuGiVis dynamic screen update mechanism, which favors pattern like update and tearing over broken fps.

![](img/8.png)

# Benefits

* Works with hundreds of thousands of images **at the same time**
* Tested with around 700.000 images, that's a RuGiVi Pixel size of 4.600.000 x 4.400.000 pixels or 20.240.000 Megapixels or 10.120.000 Full HD Screens to be scrolled through
* Dynamic view rendering - screen is updated partially when drawing takes more time
* Thumbnails are cached in a database
* Works together with the [Fapel-System](https://github.com/pronopython/fapel-system)
* Uses PyGame to render everything
* With some tweaks it should work under Windows and MacOS (but was not tested)





# Installation


## Check Prerequisites

* Linux (was written on Ubuntu, should work on all big distros) Works probably on MacOS and Windows when tweaked
* 8 GB RAM or more
* Python 3
* PIP Python Package Manager


## Clone this repository

Currently there is no install script, so clone this repository into a writeable directory.
Make all .py files executeable.
RuGiVi will run inside this dir and also create its databases there.
The database can be up to a few GB in size.

## Install needed Python modules

Install TKinter for Python

`sudo apt-get install python3-tk`

- TKinter is used for some Dialogs

Install Python Modules

`pip install pygame psutil numpy sqlitedict`

- pygame draws the screen
- psutil is needed to show memory usage
- numpy to calculate some 2D Arrays
- sqlitedict for thumb and world database

## Edit config file

Edit `rugivi.conf`:

`crawlerRootDir=` is the root directory of all the pictures you want to explore within RuGiVi.


# Start RuGiVi

Open the installation directory in terminal and start RuGiVi:


`./rugivi.py`

(Start menu entries etc will follow in a later release ;-) )

You now want to maximise the window.

You can toggle the grey info box by pressing `i` repeatly.

Rugivi will now recursivly travel trough your directory tree and gather all images with all thumbs.

You can watch this process or start traveling through the images world.


# Commands


|Key/Button       |Action                                                                              |
|-----------------|------------------------------------------------------------------------------------|
|Left Click       |Select an Image                                                                     |
|Right Click      |Center clicked area                                                                 |
|Hold Left        |Move world                                                                          |
|Double Click Left|Open / Close Preview when zoomed out                                                |
|Wheel            |Zoom in / out                                                                       |
|Click Wheel      |Fapel Table Edit Mode on / off                                                      |
|i                |Toggle grey information box                                                         |
|1-7              |Zoom levels                                                                         |
|0                |Zoom fit                                                                            |
|j                |Jump randomly                                                                       |
|n                |Open image with system image viewer                                                 |
|t                |Call [Fapel-System](https://github.com/pronopython/fapel-system) Tagger on selection|
|s                |Call [Fapel-System](https://github.com/pronopython/fapel-system) Set on selection   |
|up / down        |Open and go through Fapel Table rows                                                |
|left / right     |Go through Fapel Tables of one row                                                  |
|g                |Open Dialog to go to a spot by coordinates x,y                                      |
|o                |Pause image server (troubleshooting)                                                |
|p                |Pause crawler (troubleshooting)                                                     |





# Quitting RuGiVi

Close RuGiVi by closing the main window ("x"). If it works and all databases and jobs can be successfully exited, the window closes after a few seconds and the commandline returns to the prompt.

Sometimes RuGiVi hangs up during shutdown (a known bug). If so, please go into the command line and kill RuGiVi with Ctrl+C.

# Troubleshooting



|Problem        |Solution                                                     |
|---------------|-------------------------------------------------------------|
|Screen is black|Probably Edit mode is enabled, press middle mousebutton again|
|               |                                                             |
|               |                                                             |
|               |                                                             |



# Tips

* Speed up loading thumbs and images from the Queue: The queue can easily reach 50000 pictures / thumbs at once when zooming out. Switching to FapelTable by pressing middle mousebutton stops the drawing of the world

# Known bugs
* Quit does not work everytime. The crawler then runs in an infinite loop.
* Sometimes the garbage collection is not run or runs too late and memory is depleted (rugivi can easily grab gigabytes of RAM of course). You then get an out-of-memory error.


# Technical Stuff

Every Image is placed into a Frame with Spot Size of 4096 x 4096 Pixels, which is Heigth = 1
A Frame is placed onto a spot.
Spots are grouped into chunks. Every Chunk contains 32 x 32 = 1024 Spots (and thus, a maximum of 1024 images)

RuGiVi has its own garbage collection which is called "housekeeping" which runs every 5 minutes.
