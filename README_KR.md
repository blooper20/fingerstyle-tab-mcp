# 🎸 핑거스타일 타브 MCP 서버

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

AI 기술을 활용하여 기타 연주 오디오를 고품질 핑거스타일 타브 악보로 자동 변환해주는 MCP (Model Context Protocol) 서버입니다. 최신 딥러닝 모델로 기타 연주를 분석하고 정확하고 연주 가능한 타브 악보를 생성합니다.

[한국어 문서](./README_KR.md) | [English](./README.md)

## ✨ 주요 기능

- **🎵 AI 기반 음악 분석**: Spotify의 Basic Pitch 딥러닝 모델을 활용한 고정밀 음정 감지
- **⚡ 병렬 처리**: 45초 이상의 긴 오디오 파일을 멀티스레드 청크 처리로 1분 이내에 분석
- **🎯 스마트 운지 매핑**: 연주 가능한 오픈 코드 형태(0-5프렛 중심)를 우선하는 지능형 운지 로직
- **🎼 고급 코드 인식**: 40개 이상의 코드 형태 자동 인식 (메이저, 마이너, 7th, sus4, dim, aug 등)
- **⏱️ BPM 자동 감지**: Librosa를 통한 지능형 템포 분석 및 정확한 마디 정렬
- **💾 스마트 캐싱**: 동일한 파일 재처리 방지를 위한 결과 캐싱
- **🔍 퍼지 파일 매칭**: resource 디렉토리에서 지능형 파일 탐색
- **🤖 MCP 통합**: Claude Desktop과 완벽한 통합으로 대화형 타브 악보 개선
- **🌍 다국어 지원**: 완전한 다국어 지원 (한국어, 영어)
- **⚙️ 높은 설정 가능성**: YAML 기반 설정으로 모든 분석 옵션 커스터마이징
- **📊 상세한 로깅**: stderr 리다이렉션으로 디버깅을 위한 체계적 로깅

## 📋 목차

- [빠른 시작](#-빠른-시작)
- [설치 방법](#-설치-방법)
- [사용 방법](#-사용-방법)
  - [Claude Desktop 연동 (권장)](#claude-desktop-연동-권장)
  - [커맨드라인 사용](#커맨드라인-사용)
  - [Python API 사용](#python-api-사용)
- [주요 기능 상세](#-주요-기능-상세)
- [설정](#-설정)
- [MCP 도구 레퍼런스](#-mcp-도구-레퍼런스)
- [프로젝트 구조](#-프로젝트-구조)
- [사용 예시](#-사용-예시)
- [문제 해결](#-문제-해결)
- [기여하기](#-기여하기)
- [라이선스](#-라이선스)

## 🚀 빠른 시작

### 필수 조건

시작하기 전에 다음 프로그램이 설치되어 있는지 확인하세요:

- **Python 3.10 이상**: [Python 다운로드](https://www.python.org/downloads/)
- **FFmpeg**: 오디오 처리에 필요
  - **macOS**: `brew install ffmpeg`
  - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
  - **Windows**: [ffmpeg.org](https://ffmpeg.org/download.html)에서 다운로드

### 설치 방법

#### 옵션 1: 소스코드에서 설치 (권장)

```bash
# 저장소 클론
git clone https://github.com/blooper20/fingerstyle-tab-mcp.git
cd fingerstyle-tab-mcp

# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt

# 선택사항: 개발 모드로 설치
pip install -e .
```

#### 옵션 2: 패키지로 설치

```bash
pip install git+https://github.com/blooper20/fingerstyle-tab-mcp.git
```

## 📖 사용 방법

### Claude Desktop 연동 (권장)

이 방법이 Fingerstyle Tab MCP 서버를 사용하는 가장 강력한 방법입니다. Claude와 대화하면서 기타 타브 악보를 생성하고 개선하고 커스터마이징할 수 있습니다.

#### 1. 설정 방법

**Step 1: Claude Desktop 설치**
[claude.ai/download](https://claude.ai/download)에서 다운로드

**Step 2: MCP 서버 설정**

Claude Desktop 설정 파일에 다음 내용 추가:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
```json
{
  "mcpServers": {
    "fingerstyle-mcp": {
      "command": "/절대경로/fingerstyle-tab-mcp/venv/bin/python3",
      "args": ["/절대경로/fingerstyle-tab-mcp/mcp_server.py"],
      "env": {
        "PYTHONPATH": "/절대경로/fingerstyle-tab-mcp"
      }
    }
  }
}
```

**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`
```json
{
  "mcpServers": {
    "fingerstyle-mcp": {
      "command": "C:\\절대경로\\fingerstyle-tab-mcp\\venv\\Scripts\\python.exe",
      "args": ["C:\\절대경로\\fingerstyle-tab-mcp\\mcp_server.py"],
      "env": {
        "PYTHONPATH": "C:\\절대경로\\fingerstyle-tab-mcp"
      }
    }
  }
}
```

**Step 3: Claude Desktop 재시작**

Claude Desktop을 완전히 종료 (macOS는 Cmd+Q)하고 다시 시작합니다.

**Step 4: 설치 확인**

로그를 확인하여 서버가 성공적으로 시작되었는지 확인:

```bash
# macOS
tail -f ~/Library/Logs/Claude/mcp-server-fingerstyle-mcp.log

# 다음 메시지를 찾으세요:
# 🚀 FINGERSTYLE MCP SERVER IS NOW ONLINE AND READY
```

#### 2. Claude와 함께 사용하기

설정이 완료되면 자연어로 Claude와 대화할 수 있습니다:

**대화 예시:**

> **사용자**: "어떤 오디오 파일들을 사용할 수 있어?"
>
> **Claude**: *`list_available_audio_files` 도구 사용*
>
> resource/ 폴더에 있는 파일들:
> - Adelle-- someone like you-null.mp3
> - Falling Slowly - Once [legendado](MP3_70K)_1.mp3

---

> **사용자**: "'someone like you' 분석해서 기타 타브 만들어줘"
>
> **Claude**: *퍼지 매칭으로 `analyze_audio_to_tab` 도구 사용*
>
> 🎸 핑거스타일 정밀 분석 (BPM: 123.05)
>
> Dm              G               C               F
> e|----------------|----------------|----------------|----------------|
> B|3---3-------3---|0---0-------0---|1---1-------1---|1---1-------1---|
> G|2---2-------2---|0---0-------0---|0---0-------0---|2---2-------2---|
> D|0---0-------0---|0---0-------0---|2---2-------2---|3---3-------3---|
> A|----------------|2---2-------2---|3---3-------3---|3---3-------3---|
> E|----------------|3---3-------3---|----------------|1---1-------1---|

---

> **사용자**: "10초부터 시작해서 30초만 분석해줘"
>
> **Claude**: *`start_seconds=10.0, duration_seconds=30.0` 파라미터로 `analyze_audio_to_tab` 도구 사용*
>
> 분석 성공 (시작: 10.0초, 길이: 30.0초)...

---

> **사용자**: "음정 65번을 3번 줄에서 연주하고 싶어"
>
> **Claude**: *`tweak_tab_fingering` 도구 사용*
>
> 음정 65를 3번 줄 (D)에서 연주하도록 설정을 업데이트했습니다

#### 3. 사용 가능한 MCP 도구

서버는 Claude에게 다음 도구들을 제공합니다:

| 도구 | 설명 |
|------|------|
| `analyze_audio_to_tab` | 오디오 파일을 타브 악보로 변환하는 메인 도구 |
| `list_available_audio_files` | resource/ 디렉토리의 모든 오디오 파일 목록 |
| `tweak_tab_fingering` | 특정 음정의 운지 설정 조정 |
| `get_standard_tuning` | 표준 기타 튜닝 정보 조회 |

상세 문서는 [MCP 도구 레퍼런스](#-mcp-도구-레퍼런스)를 참조하세요.

### 커맨드라인 사용

빠른 테스트나 배치 처리를 위한 방법:

```bash
# 기본 사용법
python test_workflow.py path/to/your/audio.mp3

# resource/ 디렉토리의 파일 사용
python test_workflow.py "someone like you"  # 퍼지 매칭 작동!
```

**출력 예시:**
```
--- 'Adelle-- someone like you-null.mp3' 분석 시작 ---
1. 오디오 분석 중 (BPM 감지 및 Basic Pitch 실행)...
   템포 감지 중...
   감지된 BPM: 123.05
   병렬 분석: 1분 이내 완료를 위해 11개 청크로 분할
   분석 완료: 2554개의 음이 검출되었습니다. (감지된 BPM: 123.05)
2. 기타 타브로 변환 중 (코드 기반 운지 및 주법 분석)...

--- 생성된 타브 악보 ---
🎸 핑거스타일 정밀 분석 (BPM: 123.05)

  Dm              G               C               F
e|----------------|----------------|----------------|----------------|
B|3---3---3---3---|0---0---0---0---|1---1---1---1---|1---1---1---1---|
G|2---2---2---2---|0---0---0---0---|0---0---0---0---|2---2---2---2---|
D|0---0---0---0---|0---0---0---0---|2---2---2---2---|3---3---3---3---|
A|----------------|2---2---2---2---|3---3---3---3---|3---3---3---3---|
E|----------------|3---3---3---3---|----------------|1---1---1---1---|
```

### 지원하는 오디오 형식

- MP3 (`.mp3`)
- WAV (`.wav`)
- FLAC (`.flac`)
- OGG (`.ogg`)
- M4A (`.m4a`)
- AAC (`.aac`)

### Python API 사용

자신의 프로젝트에 통합하기:

```python
from src.transcriber import transcribe_audio
from src.tab_generator import create_tab

# Step 1: 오디오 분석 (옵션 파라미터 포함)
notes, detected_bpm = transcribe_audio(
    "path/to/audio.mp3",
    duration=30.0,        # 선택사항: 처음 30초만 분석
    start_offset=10.0     # 선택사항: 10초부터 시작
)

# Step 2: 타브 악보 생성
tab = create_tab(notes, bpm=detected_bpm)

print(tab)
```

#### 고급 API 사용법

```python
from src.tab_generator import TabGenerator

# 커스텀 설정
generator = TabGenerator(
    tuning=['D2', 'A2', 'D3', 'G3', 'B3', 'E4'],  # Drop D 튜닝
    bpm=140,
    slots_per_measure=16
)

# 커스텀 설정으로 타브 생성
tab = generator.generate_ascii_tab(notes)
```

## 🔥 주요 기능 상세

### 1. 병렬 처리

45초 이상의 오디오 파일에 대해 자동으로:
- 2초 겹침을 가진 30초 청크로 파일 분할
- 4개의 워커 스레드로 청크 병렬 처리
- 결과 병합 및 겹치는 음표 중복 제거
- **결과**: 3분 처리 시간을 1분 이하로 단축!

```python
# 긴 파일에 대한 자동 병렬 처리
notes, bpm = transcribe_audio("long_song.mp3")  # 45초 이상이면 자동 병렬화
```

### 2. 스마트 캐싱

재처리를 피하기 위한 결과 캐싱:

```python
# 첫 번째 호출: 오디오 처리
analyze_audio_to_tab("song.mp3")  # ~30초 소요

# 두 번째 호출: 캐시된 결과 반환
analyze_audio_to_tab("song.mp3")  # 즉시!

# 다른 파라미터: 새로운 처리
analyze_audio_to_tab("song.mp3", duration_seconds=30)  # ~5초 소요
```

### 3. 퍼지 파일 매칭

정확한 파일명 불필요:

```python
# 다음 모두 작동:
analyze_audio_to_tab("someone like you")
analyze_audio_to_tab("someonelikeyou.mp3")
analyze_audio_to_tab("Adelle-- someone like you-null.mp3")
```

서버가 파일명을 정규화하여 `resource/` 디렉토리에서 최적 매치를 찾습니다.

### 4. 지능형 코드 인식

40개 이상의 코드 타입 인식:
- **메이저**: C, G, F, D, A, E 등
- **마이너**: Am, Dm, Em 등
- **7th 코드**: C7, G7, Cmaj7, Dm7 등
- **Suspended**: Csus4, Gsus2 등
- **확장**: Cadd9, C6 등
- **변형**: Cdim, Caug 등

### 5. 스마트 운지 알고리즘

타브 생성기:
- 오픈 코드 형태 우선 (0-5 프렛 범위)
- 손 위치 변경 최소화
- 가능한 곳에서 음표를 코드 형태로 그룹화
- 베이스 음을 적절한 줄에 배치

## ⚙️ 설정

프로젝트 루트에 `config.yaml` 파일을 생성하여 동작 커스터마이징:

```bash
cp config.yaml.example config.yaml
```

### 설정 옵션

```yaml
# 오디오 처리
audio:
  default_bpm: 120.0
  min_bpm: 40
  max_bpm: 200
  parallel_threshold: 45.0  # 45초 이상 파일에 병렬 처리 활성화
  chunk_size: 30.0          # 청크 크기 (초)
  chunk_overlap: 2.0        # 청크 간 겹침

# 타브 악보 생성
tablature:
  standard_tuning: ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']
  bass_threshold: 50        # 베이스 감지를 위한 MIDI 음정 임계값
  slots_per_measure: 16     # 타브 그리드 세분성
  min_fret: 0
  max_fret: 12

# 로깅
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR
  format: '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
```

모든 사용 가능한 옵션은 [config.yaml.example](config.yaml.example)을 참조하세요.

## 🛠 MCP 도구 레퍼런스

### `analyze_audio_to_tab`

오디오-타브 변환을 위한 메인 도구.

**파라미터:**
- `file_path` (문자열, 필수): 오디오 파일 경로 또는 파일명만
  - 절대 경로 지원: `/Users/you/Music/song.mp3`
  - 상대 경로 지원: `~/Music/song.mp3`
  - 파일명만 지원: `song.mp3` (`resource/`에서 검색)
  - 퍼지 매칭 지원: `someone like you` → `Adelle-- someone like you-null.mp3` 찾음
- `duration_seconds` (실수, 선택): N초로 분석 제한 (기본값: 전체 파일 처리)
- `start_seconds` (실수, 선택): N초부터 분석 시작 (기본값: 0.0)

**반환값:**
- 코드 주석과 BPM 정보가 포함된 ASCII 기타 타브 악보

**예시:**
```python
# 전체 파일
analyze_audio_to_tab("song.mp3")

# 처음 30초
analyze_audio_to_tab("song.mp3", duration_seconds=30.0)

# 1분 지점부터 30초
analyze_audio_to_tab("song.mp3", start_seconds=60.0, duration_seconds=30.0)
```

### `list_available_audio_files`

`resource/` 디렉토리의 모든 오디오 파일 목록.

**파라미터:** 없음

**반환값:**
- 사용 가능한 오디오 파일 목록

**예시:**
```
resource/ 폴더에 있는 파일들:
- Adelle-- someone like you-null.mp3
- Falling Slowly - Once [legendado](MP3_70K)_1.mp3
```

### `tweak_tab_fingering`

특정 MIDI 음정에 대한 선호 줄 제안 (계획된 기능).

**파라미터:**
- `note_pitch` (정수, 필수): MIDI 음정 (0-127)
- `preferred_string` (정수, 필수): 목표 줄 번호 (1=높은 E, 6=낮은 E)

**반환값:**
- 확인 메시지

### `get_standard_tuning`

표준 기타 튜닝 참조 정보 조회.

**파라미터:** 없음

**반환값:**
```
표준 튜닝: E2, A2, D3, G3, B3, E4 (82.41Hz - 329.63Hz)
```

## 🛠 프로젝트 구조

```
fingerstyle-tab-mcp/
├── src/
│   ├── transcriber.py       # 오디오 분석 & 병렬 처리
│   │   ├── transcribe_audio()      # 메인 분석 함수
│   │   ├── get_model()             # 모델 캐싱
│   │   └── _transcribe_chunk()     # 청크 처리
│   ├── tab_generator.py     # 스마트 운지 & ASCII 타브 생성
│   │   ├── TabGenerator            # 메인 생성기 클래스
│   │   ├── create_tab()            # 고수준 API
│   │   └── CHORD_LIBRARY           # 40+ 코드 템플릿
│   └── config.py            # 설정 관리
├── locales/                 # 다국어 지원 파일
│   ├── en/LC_MESSAGES/      # 영어 번역
│   └── ko/LC_MESSAGES/      # 한국어 번역
├── resource/                # 예시 오디오 파일 (여기에 파일 배치)
├── mcp_server.py            # FastMCP 서버 구현
├── test_workflow.py         # 커맨드라인 테스트 도구
├── requirements.txt         # Python 의존성
├── setup.py                 # 패키지 설치 스크립트
├── config.yaml.example      # 예시 설정
├── README.md                # 영문 문서
├── README_KR.md             # 이 파일
└── LICENSE                  # MIT 라이선스
```

### 핵심 컴포넌트

- **`src/transcriber.py`**: 오디오 분석 엔진
  - 긴 파일(45초 이상)에 대한 병렬 처리
  - 재로딩 방지를 위한 전역 모델 캐싱
  - Librosa를 사용한 BPM 감지
  - Spotify의 Basic Pitch를 사용한 음표 추출
  - 청크 수준 에러 핸들링

- **`src/tab_generator.py`**: 타브 생성 엔진
  - 40개 이상의 코드 타입 인식
  - 스마트 운지 알고리즘 (오픈 코드 우선)
  - 코드 주석이 있는 ASCII 타브 렌더링
  - 마디 기반 포맷팅

- **`mcp_server.py`**: MCP 프로토콜 서버
  - 퍼지 매칭을 통한 스마트 파일 탐색
  - 성능을 위한 결과 캐싱
  - 포괄적인 에러 핸들링
  - stdout/stderr 깔끔한 분리
  - 다국어 지원

## 📚 사용 예시

### 예시 1: 기본 사용법

```bash
# resource/ 디렉토리에 기타 녹음 배치
cp ~/Music/my_song.mp3 resource/

# 분석 실행
python test_workflow.py "my_song"
```

### 예시 2: 특정 구간 분석

```python
from src.transcriber import transcribe_audio
from src.tab_generator import create_tab

# 후렴구만 분석 (1분 20초부터 30초간)
notes, bpm = transcribe_audio(
    "resource/song.mp3",
    start_offset=80.0,      # 1:20 = 80초
    duration=30.0
)

tab = create_tab(notes, bpm=bpm)
print(tab)
```

### 예시 3: 커스텀 튜닝

```python
from src.tab_generator import TabGenerator

# Drop D 튜닝 (DADGBE)
generator = TabGenerator(
    tuning=['D2', 'A2', 'D3', 'G3', 'B3', 'E4'],
    bpm=140
)

tab = generator.generate_ascii_tab(notes)
print(tab)
```

### 예시 4: 배치 처리

```python
import glob
import os
from src.transcriber import transcribe_audio
from src.tab_generator import create_tab

# 디렉토리의 모든 MP3 파일 처리
for audio_file in glob.glob("resource/*.mp3"):
    print(f"{audio_file} 처리 중...")

    try:
        # 분석
        notes, bpm = transcribe_audio(audio_file)

        # 타브 생성
        tab = create_tab(notes, bpm=bpm)

        # 텍스트 파일로 저장
        output_file = audio_file.replace('.mp3', '_tab.txt')
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(tab)

        print(f"✓ {output_file}에 저장됨")
    except Exception as e:
        print(f"✗ 실패: {e}")
```

### 예시 5: Claude Desktop과 함께 사용

Claude와의 대화형 사용에 대한 상세 예시는 [Claude Desktop 연동](#claude-desktop-연동-권장)을 참조하세요.

## 🌍 다국어 지원

이 프로젝트는 `gettext`를 사용하여 다국어를 지원합니다.

### 지원 언어

- **한국어** (ko) - 완전 지원
- **영어** (en) - 기본값

### 새로운 언어 추가하기

1. **번역 가능한 문자열 추출:**
```bash
xgettext -o locales/messages.pot src/*.py mcp_server.py
```

2. **언어별 번역 생성:**
```bash
# 'ja'를 언어 코드로 교체 (예: 'es'는 스페인어)
msginit -i locales/messages.pot -o locales/ja/LC_MESSAGES/messages.po -l ja
```

3. **`.po` 파일에서 문자열 번역**

4. **번역 컴파일:**
```bash
msgfmt locales/ja/LC_MESSAGES/messages.po -o locales/ja/LC_MESSAGES/messages.mo
```

5. **언어 환경 변수 설정:**
```bash
export LANG=ja_JP.UTF-8  # 일본어의 경우
python test_workflow.py "song.mp3"
```

## 🐛 문제 해결

### 일반적인 문제

#### 문제: MCP 서버가 Claude Desktop에 나타나지 않음

**해결 방법:**
1. 설정 파일 경로 확인:
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
2. 경로가 절대 경로인지 확인 (상대 경로 X)
3. Claude Desktop 완전히 재시작 (Cmd+Q, 창만 닫기 X)
4. 로그 확인: `tail -f ~/Library/Logs/Claude/mcp-server-fingerstyle-mcp.log`

#### 문제: 서버가 시작되지만 즉시 크래시

**해결 방법:**
1. 로그에서 시작 배너 확인:
   ```
   🚀 FINGERSTYLE MCP SERVER IS NOW ONLINE AND READY
   ```
2. import 에러가 보이면 모든 의존성 설치 확인:
   ```bash
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. 서버 수동 테스트:
   ```bash
   ./venv/bin/python3 -c "from src.transcriber import transcribe_audio"
   ```

#### 문제: `ModuleNotFoundError: No module named 'basic_pitch'`

**해결 방법:**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

#### 문제: `FileNotFoundError: Audio file not found`

**해결 방법:**
- 파일이 `resource/` 디렉토리에 있는지 확인
- `list_available_audio_files` 도구로 사용 가능한 파일 확인
- 파일명의 일부만으로 퍼지 매칭 시도

#### 문제: 병렬 처리가 "청크 에러"로 실패

**해결 방법:**
- 일반적으로 오디오 청크 중 하나를 처리하지 못했음을 의미
- 실패한 특정 청크에 대한 에러 로그 확인
- 짧은 duration으로 처리하여 문제 격리
- 오디오 파일이 손상되지 않았는지 확인

#### 문제: BPM 감지가 부정확

**해결 방법:**
- BPM 감지에 오디오의 처음 60초가 사용됨
- 파일 시작 부분에 명확한 리듬이 있는지 확인
- 코드에서 BPM을 수동으로 재정의:
  ```python
  notes, _ = transcribe_audio("song.mp3")
  tab = create_tab(notes, bpm=120)  # BPM을 120으로 강제
  ```

#### 문제: 음표가 감지되지 않거나 매우 적음

**해결 방법:**
- 믹스에서 기타가 두드러지는지 확인 (다른 악기에 묻히지 않도록)
- 오디오 파일의 볼륨을 높여보기
- 오디오 품질이 좋은지 확인 (과도하게 압축되지 않도록)
- 솔로 기타 녹음이 가장 잘 작동

#### 문제: 타브 악보가 연주 불가능하거나 이상한 운지 사용

**해결 방법:**
- 알고리즘이 오픈 코드 형태(0-5 프렛)를 우선함
- 특정 음표 조정을 위해 `tweak_tab_fingering` 도구 사용
- 원본 녹음이 다른 튜닝을 사용하는지 고려

### 도움 받기

- 📝 **버그 리포트**: [이슈 열기](https://github.com/blooper20/fingerstyle-tab-mcp/issues)
- 💬 **질문하기**: [토론 시작](https://github.com/blooper20/fingerstyle-tab-mcp/discussions)
- 📖 **문서 확인**: 영문 문서는 [English README](./README.md) 참조

### 디버그 모드

문제 해결을 위한 디버그 로깅 활성화:

```bash
# config.yaml에서
logging:
  level: DEBUG

# 또는 환경 변수 설정
export LOG_LEVEL=DEBUG
python test_workflow.py "song.mp3"
```

## 🧪 테스트

테스트 스위트 실행:

```bash
# 개발 의존성 설치
pip install -e ".[dev]"

# 테스트 실행
pytest

# 커버리지와 함께 실행
pytest --cov=src --cov-report=html

# 커버리지 리포트 보기
open htmlcov/index.html  # macOS
```

## 🤝 기여하기

기여를 환영합니다! 가이드라인은 [CONTRIBUTING.md](CONTRIBUTING.md)를 참조하세요.

### 개발 환경 설정

```bash
# 클론 및 설정
git clone https://github.com/blooper20/fingerstyle-tab-mcp.git
cd fingerstyle-tab-mcp

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate

# 개발 의존성과 함께 설치
pip install -e ".[dev]"

# 코드 포맷팅 실행
black src/ test/
isort src/ test/

# 린팅 실행
flake8 src/ test/
mypy src/
```

### 기여 영역

- 🎵 **정확도 개선**: 더 나은 코드 감지 및 운지 알고리즘
- 🎸 **기능 추가**: 대체 튜닝, 카포 위치 지원
- 🌍 **번역**: 더 많은 언어 지원 추가
- 📊 **시각화**: PDF 내보내기, 더 나은 ASCII 렌더링
- 🧪 **테스트**: 테스트 커버리지 증가
- 📖 **문서화**: 예시 및 튜토리얼 개선
- 🐛 **버그 수정**: 이슈 및 엣지 케이스 수정
- ⚡ **성능**: 처리 속도 최적화

### 커밋 메시지 가이드라인

conventional commits 사용:

```
feat: MIDI 내보내기 기능 추가
fix: suspended 코드에 대한 코드 감지 해결
docs: 설치 가이드 업데이트
style: black으로 코드 포맷팅
refactor: 타브 생성 로직 단순화
test: 병렬 처리에 대한 테스트 추가
chore: 의존성 업데이트
```

## 🙏 감사의 말

이 프로젝트는 다음 오픈소스 라이브러리를 사용합니다:

- [Basic Pitch](https://github.com/spotify/basic-pitch) by Spotify - 오디오-MIDI 변환
- [Librosa](https://librosa.org/) - 오디오 분석 및 BPM 감지
- [Music21](https://web.mit.edu/music21/) - 음악 이론 및 코드 감지
- [FastMCP](https://github.com/jlowin/fastmcp) - MCP 서버 프레임워크
- [NumPy](https://numpy.org/) - 수치 연산
- [SoundFile](https://github.com/bastibe/python-soundfile) - 오디오 I/O

이 프로젝트를 가능하게 해준 오픈소스 커뮤니티에 특별히 감사드립니다.

## 📜 라이선스

이 프로젝트는 [MIT 라이선스](./LICENSE)를 따릅니다.

상업적 사용을 포함한 모든 목적으로 이 소프트웨어를 자유롭게 사용, 수정, 배포할 수 있습니다.

## 🗺️ 로드맵

### 단기 (v1.1)
- [ ] MIDI 파일 내보내기
- [ ] 대체 튜닝 지원 (Drop D, DADGAD 등)
- [ ] 카포 위치 감지
- [ ] 개선된 운지 커스터마이징

### 중기 (v1.5)
- [ ] 악보가 포함된 PDF 타브 악보 내보내기
- [ ] 실시간 오디오 처리 (라이브 변환)
- [ ] Guitar Pro 형식 내보내기
- [ ] 비기술자를 위한 웹 인터페이스

### 장기 (v2.0)
- [ ] 모바일 앱 통합
- [ ] 여러 악기 지원 (베이스, 우쿨렐레)
- [ ] 협업 타브 편집
- [ ] 더 빠른 결과를 위한 클라우드 처리
- [ ] 커스텀 운지 선호도를 위한 머신러닝

## 📊 성능 벤치마크

MacBook Pro M1에서 테스트:

| 오디오 길이 | 순차 처리 | 병렬 처리 | 속도 향상 |
|-------------|----------|----------|----------|
| 30초        | ~8초     | ~8초     | 1배      |
| 60초        | ~25초    | ~12초    | 2.1배    |
| 120초       | ~95초    | ~22초    | 4.3배    |
| 180초       | ~170초   | ~35초    | 4.9배    |

*참고: 45초 이상 파일에서 자동으로 병렬 처리 활성화*

---

**오픈소스 커뮤니티가 ❤️를 담아 만들었습니다**

**유용하다면 이 레포에 스타** ⭐를 눌러주세요!
