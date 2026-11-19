MY SAJU - Windows EXE 제작 및 배포 안내
========================================

목표
- 받는 사람은 Python 설치나 회원가입 없이 MY_SAJU.exe 실행
- 제작자는 자신의 Windows PC에 Python을 설치하지 않고 클라우드 빌드 사용

[권장: 클라우드 빌드 - 제작 PC에 Python 설치 불필요]
1. 제작자 본인의 GitHub 계정으로 로그인합니다. 친구들은 GitHub 계정이 필요하지 않습니다.
2. 새 저장소(repository)를 만듭니다. 예: my-saju-build
3. 이 ZIP 안의 my_saju 폴더 안에 있는 모든 파일과 폴더를 저장소 최상위에 업로드합니다. 숨김 폴더 .github도 반드시 포함합니다.
4. 저장소의 Actions 탭에서 'Build MY SAJU Windows EXE'를 선택합니다.
5. Run workflow를 실행합니다.
6. 작업이 초록색 완료 상태가 되면 실행 기록을 열고 Artifacts의 MY_SAJU-Windows-EXE를 다운로드합니다.
7. ZIP을 풀어 MY_SAJU.exe를 확인합니다.

[중요: 계정과 설치 요구사항 구분]
- 제작자: GitHub 계정은 필요하지만, 제작자 PC에 Python 설치는 필요하지 않습니다. 빌드는 GitHub의 Windows 클라우드 컴퓨터에서 진행됩니다.
- 친구: GitHub 계정과 Python 설치 모두 필요하지 않습니다. EXE 파일을 받으면 됩니다.
- GitHub 계정도 전혀 사용하지 않으려면, 별도의 Windows 빌드 컴퓨터에서 빌드하거나 신뢰할 수 있는 빌드 서비스를 별도로 마련해야 합니다.

[로컬 빌드 대안]
- build_exe_로컬Python필요.bat은 제작 PC에 Python 3.10 이상이 설치된 경우에만 사용합니다.
- Python이 없는 PC에서는 이 파일을 실행하지 마세요.

[배포 전 확인]
- EXE는 실제 Windows PC에서 실행, 사주 계산, 인쇄/PDF 저장을 확인한 뒤 배포합니다.
- Windows SmartScreen 경고가 표시될 수 있습니다. 출처를 확인하지 않은 경고는 무시하지 마세요.
- 이 프로젝트는 Flask 로컬 서버를 127.0.0.1에서 실행합니다. 외부 네트워크에 공개하는 모바일 웹 서버로 그대로 배포하면 안 됩니다.
- 모바일 웹 공개 전에는 서버 공용 SQLite 인물 보관함을 제거하거나 사용자별 격리 저장으로 바꾸고, 개인정보 처리 및 보안 설정을 별도로 검증해야 합니다.

[검증 한계]
이 프로젝트 ZIP의 압축 무결성 확인은 악성코드 백신 검사나 실제 Windows 실행 테스트를 의미하지 않습니다.
