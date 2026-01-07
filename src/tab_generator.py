from music21 import pitch

class TabGenerator:
    def __init__(self, tuning=['E2', 'A2', 'D3', 'G3', 'B3', 'E4']):
        """
        기본값으로 표준 튜닝(Standard Tuning)을 설정합니다.
        """
        self.tuning = [pitch.Pitch(t).midi for t in tuning]
        self.num_strings = len(self.tuning)
        # 베이스 음역대 임계값 (예: MIDI 50 이하는 베이스 줄 위주 배치)
        self.bass_threshold = 50 
        
    def find_best_string_fret(self, midi_pitch, is_bass=False):
        """
        음정을 기타 줄/프렛으로 변환합니다.
        is_bass: True인 경우 낮은 줄(4, 5, 6번줄)을 우선적으로 검색합니다.
        """
        if is_bass:
            # 베이스 음은 6번줄(인덱스 0)부터 4번줄(인덱스 2)까지 우선 확인
            search_order = [0, 1, 2, 3]
        else:
            # 멜로디 음은 1번줄(인덱스 5)부터 아래로 확인
            search_order = [5, 4, 3, 2, 1, 0]
            
        for string_idx in search_order:
            string_root = self.tuning[string_idx]
            fret = midi_pitch - string_root
            if 0 <= fret <= 15: # 핑거스타일 연주 편의를 위해 15프렛 이내로 제한
                return string_idx, fret
        
        # 우선 순위에서 못 찾은 경우 전체 줄 재검색
        for string_idx in range(self.num_strings):
            string_root = self.tuning[string_idx]
            fret = midi_pitch - string_root
            if 0 <= fret <= 22:
                return string_idx, fret
                
        return None, None

    def generate_ascii_tab(self, notes):
        """
        노트 이벤트를 분석하여 해머링 온(h), 풀 오프(p)가 포함된 ASCII 타브를 생성합니다.
        """
        if not notes:
            return "검출된 음이 없습니다."

        total_slots = 100
        tab_lines = [["-"] * total_slots for _ in range(self.num_strings)]
        
        max_time = max(n['end'] for n in notes) if notes else 10
        time_scale = (total_slots - 5) / max_time # 'h', 'p' 기호를 위한 여유 공간 확보
        
        # 줄별로 배정된 노트들을 저장 (주법 분석용)
        string_assignments = [[] for _ in range(self.num_strings)]
        
        for note in notes:
            # 음역대에 따라 베이스 여부 판단
            is_bass = note['pitch'] <= self.bass_threshold
            
            # 퍼커시브(X) 판단 로직:
            # 1. 속도(velocity)가 매우 높거나 (강한 타격)
            # 2. 아주 짧은 지속 시간을 가진 경우
            # (실제 환경에서는 음색 분석이 필요하지만 MVP 수준의 휴리스틱 적용)
            is_percussive = note.get('velocity', 0) > 100 and (note['end'] - note['start']) < 0.08

            string_idx, fret = self.find_best_string_fret(note['pitch'], is_bass=is_bass)
            
            if string_idx is not None:
                string_assignments[string_idx].append({
                    'fret': fret,
                    'start_time': note['start'],
                    'pos': int(note['start'] * time_scale),
                    'is_percussive': is_percussive
                })

        # 주법 분석 및 타브 배치
        for s_idx, assigned_notes in enumerate(string_assignments):
            line_idx = self.num_strings - 1 - s_idx
            assigned_notes.sort(key=lambda x: x['start_time'])
            
            for i in range(len(assigned_notes)):
                curr_n = assigned_notes[i]
                pos = curr_n['pos']
                
                # 퍼커시브인 경우 'x'로 표기, 아니면 프렛 번호
                if curr_n['is_percussive']:
                    fret_str = "x"
                else:
                    fret_str = str(curr_n['fret'])
                
                # 이전 노트와의 간격을 확인하여 h/p 결정 (퍼커시브가 아닐 때만)
                technique = ""
                if i > 0 and not curr_n['is_percussive'] and not assigned_notes[i-1]['is_percussive']:
                    prev_n = assigned_notes[i-1]
                    time_diff = curr_n['start_time'] - prev_n['start_time']
                    
                    if time_diff < 0.15:
                        if curr_n['fret'] > prev_n['fret']:
                            technique = "h"
                        elif curr_n['fret'] < prev_n['fret']:
                            technique = "p"

                # 타브에 기록
                if technique:
                    # 이전 위치와 현재 위치 사이에 기호 삽입
                    tech_pos = max(0, pos - 1)
                    tab_lines[line_idx][tech_pos] = technique
                
                # 프렛 번호 기록
                for j, char in enumerate(fret_str):
                    if pos + j < total_slots:
                        tab_lines[line_idx][pos + j] = char

        headers = ['e|', 'B|', 'G|', 'D|', 'A|', 'E|']
        output = []
        for i in range(self.num_strings):
            output.append(headers[i] + "".join(tab_lines[i]) + "|")
            
        return "\n".join(output)

def create_tab(notes):
    generator = TabGenerator()
    return generator.generate_ascii_tab(notes)
