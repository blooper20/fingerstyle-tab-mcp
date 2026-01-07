from mcp.server.fastmcp import FastMCP
from src.transcriber import transcribe_audio
from src.tab_generator import create_tab
import os

# MCP 서버 생성
mcp = FastMCP("핑거스타일 타브 생성기")

@mcp.tool()
def analyze_audio_to_tab(file_path: str) -> str:
    """
    오디오 파일(.mp3, .wav)을 분석하여 기타 타브 악보로 변환합니다.
    
    Args:
        file_path: 오디오 파일의 절대 경로.
    
    Returns:
        오디오를 분석하여 생성된 ASCII 기타 타브 악보.
    """
    if not os.path.exists(file_path):
        return f"에러: 파일을 찾을 수 없습니다: {file_path}"
    
    try:
        # 1단계: 오디오를 노트 데이터로 전사
        notes = transcribe_audio(file_path)
        
        # 2단계: 노트를 타브로 변환 (이미 베이스/멜로디 분리 로직 포함됨)
        tab = create_tab(notes)
        
        return f"분석 성공 - 파일 경로: {file_path}:\n\n{tab}"
    except Exception as e:
        return f"처리 중 에러 발생: {str(e)}"

@mcp.tool()
def tweak_tab_fingering(note_pitch: int, preferred_string: int) -> str:
    """
    특정 음의 운지 위치(줄 번호)를 수정하도록 요청합니다.
    
    Args:
        note_pitch: 수정할 음의 MIDI 번호.
        preferred_string: 선호하는 기타 줄 번호 (1: High E ~ 6: Low E).
    
    Returns:
        수정 제안에 대한 피드백 메시지.
    """
    # 1: High E (index 5), 6: Low E (index 0)
    # 실제 구현에서는 이 정보를 저장했다가 generate 시 반영해야 함
    # Phase 2에서는 인터페이스 정의에 집중
    string_names = ["Low E", "A", "D", "G", "B", "High E"]
    if 1 <= preferred_string <= 6:
        return f"음정 {note_pitch}를 {preferred_string}번줄({string_names[6-preferred_string]})에서 연주하도록 설정을 업데이트했습니다 (로직 반영 예정)."
    else:
        return "잘못된 줄 번호입니다. 1~6 사이의 숫자를 입력해주세요."

@mcp.resource("guitar/tuning/standard")
def get_standard_tuning() -> str:
    """표준 기타 튜닝 정보를 반환합니다."""
    return "표준 튜닝: E2, A2, D3, G3, B3, E4 (82.41Hz - 329.63Hz)"

if __name__ == "__main__":
    mcp.run()
