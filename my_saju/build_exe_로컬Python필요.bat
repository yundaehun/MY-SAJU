@echo off
chcp 65001 > nul
setlocal
cd /d "%~dp0"
title MY SAJU - Windows EXE Builder

echo.
echo  ==============================================
echo       MY SAJU  -  독립 실행 파일 만들기
echo  ==============================================
echo.

where py >nul 2>nul
if errorlevel 1 (
  echo [오류] EXE 제작 PC에 Python 3.10 이상이 필요합니다.
  echo Python 설치 시 Add Python to PATH를 체크해 주세요.
  pause
  exit /b 1
)
py -3 -c "import sys; raise SystemExit(0 if sys.version_info >= (3,10) else 1)"
if errorlevel 1 (
  echo [오류] Python 3.10 이상이 필요합니다.
  pause
  exit /b 1
)

echo [1/3] 빌드 도구 설치 중...
py -3 -m pip install --upgrade pip
py -3 -m pip install -r requirements-build.txt
if errorlevel 1 goto failed

echo [2/3] MY_SAJU.exe 제작 중...
py -3 -m PyInstaller --noconfirm --clean --onefile --noconsole --name MY_SAJU --add-data "templates;templates" --collect-all lunar_python app.py
if errorlevel 1 goto failed

echo [3/3] 완료!
if not exist "배포용" mkdir "배포용"
copy /Y "dist\MY_SAJU.exe" "배포용\MY_SAJU.exe" >nul
copy /Y "README_EXE_배포안내.txt" "배포용\사용방법.txt" >nul
echo.
echo 생성 위치: %CD%\배포용\MY_SAJU.exe
echo 이 EXE는 받는 사람 PC에 Python 설치가 필요하지 않습니다.
echo.
explorer "%CD%\배포용"
pause
exit /b 0

:failed
echo.
echo [실패] 위 오류 메시지를 확인해 주세요.
pause
exit /b 1
