#!/bin/bash
#
##############################################################################################
#
# RuGiVi - Adult Media Landscape Browser
# installi_ubuntu.sh is the installer script to copy all py files
#
# For updates see git-repo at
# https://github.com/pronopython/rugivi
#
##############################################################################################
#
VERSION=0.2.0
#
CONFIGDIR=~/.config
INSTALLDIR=""
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
# TODO comment header
# TODO clean out comments



##################################################################################


echo "RuGiVi installer v${VERSION}"
echo ""
echo "The installer now creates the program dirs and config files."
echo "Sudo is needed for some actions."
echo ""

#pip install .


if ! type "rugivi_printModuleDir" >/dev/null 2>&1; then
	echo "Installing RuGiVi module via pip"
	pip install .
	echo ""
fi


INSTALLDIR="$(rugivi_printModuleDir)"

echo "RuGiVi module installed in: ${INSTALLDIR}"
echo ""

echo "Copying config file..."
cp -i $INSTALLDIR/rugivi.conf $CONFIGDIR/rugivi.conf

echo "Creating Database dir..."

mkdir ~/.local/share/rugivi

echo "Changing permissions on installed module files"
sudo chmod 0755 $INSTALLDIR/*.py
#sudo chmod 0755 $INSTALLDIR/*.sh
sudo chmod 0644 $INSTALLDIR/*.conf


echo ""

echo "Creating start menu entries..."

DESKTOPFILE=~/.local/share/applications/RuGiVi.desktop

touch $DESKTOPFILE

echo "[Desktop Entry]" > $DESKTOPFILE
echo "Name=RuGiVi" >> $DESKTOPFILE
echo "Exec=rugivi" >> $DESKTOPFILE
echo "Terminal=false" >> $DESKTOPFILE
echo "Type=Application" >> $DESKTOPFILE
echo "Icon=${INSTALLDIR}/icon.png" >> $DESKTOPFILE


DESKTOPFILE=~/.local/share/applications/RuGiVi-Configurator.desktop

touch $DESKTOPFILE

echo "[Desktop Entry]" > $DESKTOPFILE
echo "Name=RuGiVi Configurator" >> $DESKTOPFILE
echo "Exec=rugivi_configurator" >> $DESKTOPFILE
echo "Terminal=false" >> $DESKTOPFILE
echo "Type=Application" >> $DESKTOPFILE
echo "Icon=${INSTALLDIR}/icon.png" >> $DESKTOPFILE





echo "done"

echo ""

echo "You can configure RuGiVi by running 'rugivi_configurator'"
echo "Start rugivi with 'rugivi'"
echo "You also find both within the start menu."

