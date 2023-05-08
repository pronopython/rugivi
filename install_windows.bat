@echo off
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
