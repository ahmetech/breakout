:: Filename: 		make_exe.bat
:: Description: 	Used to create a Python exe

@echo off

echo Removing the old 'build' folder...
	rd /S /Q build
echo Done

echo Removing the old 'dist' folder...
rd /S /Q dist
echo Done

echo Creating new executable based on setup.py
python setup.py py2exe --bundle 2 > py2exe.log
echo Done, check out the new 'py2exe.log' for details

pause

