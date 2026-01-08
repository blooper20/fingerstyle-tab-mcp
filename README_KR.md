# 🎸 핑거스타일 타브 MCP 서버

AI를 활용하여 기타 연주 오디오를 고품질 핑거스타일 타브 악보로 변환해주는 MCP(Model Context Protocol) 서버입니다.

## ✨ 주요 기능

- **AI 전사(Transcription)**: Spotify의 Basic Pitch를 활용한 고정밀 음정 분석.
- **스마트 운지 매핑**: 익숙한 오픈 코드 형태(0-5 프렛 중심)를 우선순위에 둔 연주 가능한 매핑 로직.
- **코드 자동 인식**: 40여 종의 코드 템플릿(Major, Minor, 7th, sus4 등)을 활용한 마디별 코드 판별.
- **자동 BPM 감지**: Librosa를 통한 템포 분석 및 정확한 마디 정렬.
- **MCP 연동**: Claude Desktop에서 대화하며 악보를 생성하고 교정할 수 있는 인터페이스 제공.

## 🚀 시작하기

### 필수 조건
- Python 3.10 이상
- FFmpeg (오디오 처리용)

### 설치 방법
```bash
git clone https://github.com/your-repo/fingerstyle-tab-mcp.git
cd fingerstyle-tab-mcp
pip install -r requirements.txt
```

### 테스트 실행
```bash
python3 test_workflow.py "오디오_파일_경로.mp3"
```

## 🌍 다국어 지원 (I18n)
본 프로젝트는 `gettext`를 사용하여 다국어를 지원합니다. 새로운 언어를 추가하고 싶다면 `locales/` 디렉토리에 기여해 주세요.

## 🤝 기여하기
버그 리포트, 기능 제안 및 풀 리퀘스트(PR)는 언제나 환영합니다!

## 📜 라이선스
이 프로젝트는 [MIT 라이선스](./LICENSE)를 따릅니다.
