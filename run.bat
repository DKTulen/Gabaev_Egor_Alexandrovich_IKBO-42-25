@echo off
setlocal
cd /d "%~dp0"
set "PY=python"
where py >nul 2>nul && set "PY=py -3"
if /I "%~1"=="test" goto :tests
set "CFG=%~1"
if "%CFG%"=="" set "CFG=config.yaml"
%PY% src\main.py "%CFG%"
exit /b %errorlevel%
:tests
%PY% -m unittest discover -s tests -t . -v
exit /b %errorlevel%
