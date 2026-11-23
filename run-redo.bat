@echo off
chcp 65001 >nul
set PYTHONUTF8=1
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

set "PYEXE="
if exist ".venv\Scripts\python.exe" set "PYEXE=.venv\Scripts\python.exe"
if not defined PYEXE if exist "D:\Python3.13\python.exe" set "PYEXE=D:\Python3.13\python.exe"
if not defined PYEXE set "PYEXE=python"

if exist "%~dp0libs" set "PYTHONPATH=%~dp0libs"

"%PYEXE%" main.py -s 2 -j 1 --redo-finished %*
