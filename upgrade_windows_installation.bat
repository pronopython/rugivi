@echo off
REM ##############################################################################################
REM #
REM # RuGiVi - Adult Media Landscape Browser
REM #
REM # For updates see git-repo at
REM # https://github.com/pronopython/rugivi
REM #
REM ##############################################################################################
REM #
REM # Copyright (C) PronoPython
REM #
REM # Contact me at pronopython@proton.me
REM #
REM # This program is free software: you can redistribute it and/or modify it
REM # under the terms of the GNU General Public License as published by the
REM # Free Software Foundation, either version 3 of the License, or
REM # (at your option) any later version.
REM #
REM # This program is distributed in the hope that it will be useful,
REM # but WITHOUT ANY WARRANTY; without even the implied warranty of
REM # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
REM # GNU General Public License for more details.
REM #
REM # You should have received a copy of the GNU General Public License
REM # along with this program.  If not, see <https://www.gnu.org/licenses/>.
REM #
REM ##############################################################################################

echo Uninstalling RuGiVi

pip uninstall --yes rugivi

echo Installing new version

pip install .

pause
