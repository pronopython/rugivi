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

REM pip install .

WHERE rugivi_printModuleDir
IF %ERRORLEVEL% NEQ 0 (
	ECHO installing RuGiVi module via pip
	REM ECHO pip install .
	pip install .
	REM pause
	REM exit 0
)

for /f %%i in ('rugivi_printModuleDir') do set INSTALLDIR=%%i
echo RuGiVi module installed in: %INSTALLDIR%

echo.
echo Installing config file...


set CONFIGDIR=%AppData%\RuGiVi
mkdir "%CONFIGDIR%"
copy /-Y "%INSTALLDIR%\rugivi_windows.conf" "%CONFIGDIR%\rugivi.conf"

echo.
echo Installing Start Menu shortcut

pyshortcut -n RuGiVi -i "%INSTALLDIR%\icon.ico"  "%INSTALLDIR%\..\..\..\Scripts\rugivi.exe"
pyshortcut -n "RuGiVi Configurator" -i "%INSTALLDIR%\icon.ico"  "%INSTALLDIR%\..\..\..\Scripts\rugivi_configurator.exe"

echo done


echo You can configure RuGiVi by running 'rugivi_configurator'
echo Start rugivi with 'rugivi'
echo You also find both within the start menu.

pause
