@echo off
chcp 65001 > nul
setlocal
cd /d "%~dp0"
title MY SAJU - 사주 명리 분석실

echo.
echo  ==============================================
echo          MY SAJU  |  사주 명리 분석실
echo  ==============================================
echo.

if not exist .venv\Scripts\python.exe (
  echo [1/3] Python 실행 환경을 준비합니다.
  where py >nul 2>nul
  if not errorlevel 1 (
    py -3 -m venv .venv
  ) else (
    where python >nul 2>nul
    if errorlevel 1 goto no_python
    python -m venv .venv
  )
  if errorlevel 1 goto fail
)

.venv\Scripts\python.exe -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 goto old_python

echo [2/3] 필수 라이브러리를 확인합니다.
.venv\Scripts\python.exe -c "import flask, lunar_python" >nul 2>nul
if errorlevel 1 (
  echo 첫 실행입니다. 필요한 라이브러리를 설치합니다. 잠시 기다려 주세요.
  .venv\Scripts\python.exe -m pip install -r requirements.txt
  if errorlevel 1 goto install_fail
)

echo [3/3] 프로그램을 실행합니다.
echo 브라우저 주소: http://127.0.0.1:5000
echo 프로그램을 종료하려면 이 검은 창에서 Ctrl+C를 누르세요.
start "" http://127.0.0.1:5000
.venv\Scripts\python.exe app.py
if errorlevel 1 goto fail
goto end

:no_python
echo [오류] Python이 설치되어 있지 않거나 PATH에서 찾을 수 없습니다.
echo Python 3.10 이상을 설치하고 설치 화면에서 Add Python to PATH를 체크해 주세요.
start "" https://www.python.org/downloads/
goto end

:old_python
echo [오류] Python 3.10 이상이 필요합니다. 기존 가상환경을 삭제한 뒤 다시 실행해 주세요.
echo 삭제할 폴더: %CD%\.venv
pause
goto end

:install_fail
echo [오류] 라이브러리 설치에 실패했습니다. 인터넷 연결을 확인하고 다시 실행해 주세요.
pause
goto end

:fail
echo [오류] 프로그램 실행에 실패했습니다. 위의 오류 내용을 확인해 주세요.
pause
:end
endlocal
