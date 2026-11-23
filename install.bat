@echo off
chcp 65001 >nul
setlocal
cd /d "%~dp0"
echo ============================================
echo   Install SuperStar dependencies
echo ============================================

set "PY=D:\Python3.13\python.exe"
if not exist "%PY%" set "PY=python"
set "PIPOPT=--isolated --no-input --disable-pip-version-check --timeout 10 --retries 1"

echo [1/3] Preparing virtual environment ...
set "USE_VENV=0"
if exist ".venv\Scripts\python.exe" (
    ".venv\Scripts\python.exe" -m pip --version >nul 2>&1
    if not errorlevel 1 set "USE_VENV=1"
)
if "%USE_VENV%"=="0" (
    if exist ".venv" rmdir /s /q ".venv"
    "%PY%" -m venv .venv
    if exist ".venv\Scripts\python.exe" (
        ".venv\Scripts\python.exe" -m pip --version >nul 2>&1
        if not errorlevel 1 set "USE_VENV=1"
    )
)

findstr /v /b /i "argparse" requirements.txt > requirements.local.txt

echo [2/3] Installing dependencies ...
if "%USE_VENV%"=="1" (
    echo        pip config:
    ".venv\Scripts\python.exe" -m pip config list
    ".venv\Scripts\python.exe" -m pip install -r requirements.local.txt %PIPOPT%
    if errorlevel 1 (
        echo        [retry 1] Aliyun mirror ...
        ".venv\Scripts\python.exe" -m pip install -r requirements.local.txt %PIPOPT% -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    )
    if errorlevel 1 (
        echo        [retry 2] Tsinghua mirror ...
        ".venv\Scripts\python.exe" -m pip install -r requirements.local.txt %PIPOPT% -i https://pypi.tuna.tsinghua.edu.cn/simple
    )
    if errorlevel 1 (
        echo        [retry 3] Official PyPI ...
        ".venv\Scripts\python.exe" -m pip install -r requirements.local.txt %PIPOPT% -i https://pypi.org/simple
    )
    echo [3/3] Verifying ...
    ".venv\Scripts\python.exe" -c "import requests, openai, bs4, lxml, fontTools, loguru, tqdm; print('DEPS OK')"
) else (
    echo        venv unavailable, target: user site-packages
    "%PY%" -m pip install --user -r requirements.local.txt %PIPOPT%
    if errorlevel 1 (
        echo        [retry 1] Aliyun mirror ...
        "%PY%" -m pip install --user -r requirements.local.txt %PIPOPT% -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
    )
    echo [3/3] Verifying ...
    "%PY%" -c "import requests, openai, bs4, lxml, fontTools, loguru, tqdm; print('DEPS OK')"
)

echo.
echo Done.
echo   1) edit config.ini and fill in your API key
echo   2) run: run.bat -u PHONE -p PASSWORD -l COURSE_ID
pause
