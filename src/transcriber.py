import numpy as np
from basic_pitch.inference import predict
from basic_pitch import ICASSP_2022_MODEL_PATH

def transcribe_audio(audio_path: str):
    """
    Basic Pitch를 사용하여 오디오 파일을 분석하고 노트 리스트를 반환합니다.
    반환값: 'pitch'(음정), 'start'(시작 시간), 'end'(종료 시간), 'velocity'(강도)를 포함한 딕셔너리 리스트.
    """
    # model_output: ICASSP 2022 모델 출력 결과
    # midi_data: pretty_midi 객체
    # note_events: 노트 이벤트 리스트 (음정, 시작, 종료, 강도)
    model_output, midi_data, note_events = predict(audio_path)
    
    notes = []
    for note in note_events:
        notes.append({
            'pitch': note.pitch,
            'start': note.start,
            'end': note.end,
            'velocity': note.velocity
        })
    
    # 시작 시간 순으로 정렬
    notes.sort(key=lambda x: x['start'])
    return notes
