import gettext
import os
import logging
from typing import List, Dict, Tuple, Optional, Any
from music21 import pitch

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Internationalization Setup
localedir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../locales')
translate = gettext.translation('messages', localedir, fallback=True)
_ = translate.gettext

class TabGenerator:
    def __init__(self, tuning: List[str] = None, bpm: float = 75):
        """
        Initialize the TabGenerator.

        Args:
            tuning: List of string tunings (default: standard tuning E2-E4)
            bpm: Beats per minute (default: 75, range: 40-200)
        """
        if tuning is None:
            tuning = ['E2', 'A2', 'D3', 'G3', 'B3', 'E4']

        try:
            self.tuning = [pitch.Pitch(t).midi for t in tuning]
        except Exception as e:
            logger.error(_("Invalid tuning specification: {}").format(str(e)))
            raise ValueError(_("Invalid tuning: {}").format(tuning)) from e

        self.num_strings = len(self.tuning)
        self.bpm = max(40, min(bpm, 200))  # Realistic BPM limits
        self.bass_threshold = 50
        self.capo = 0

        logger.info(_("TabGenerator initialized - Tuning: {}, BPM: {:.1f}").format(
            tuning, self.bpm
        )) 

        # Precision Chord Templates based on reference charts
        self.chord_templates = {
            "C": {1: 3, 2: 2, 3: 0, 4: 1, 5: 0},
            "Cm": {1: 3, 2: 5, 3: 5, 4: 4, 5: 3},
            "C7": {1: 3, 2: 2, 3: 3, 4: 1, 5: 0},
            "CM7": {1: 3, 2: 2, 3: 0, 4: 0, 5: 0},
            "Cm7": {1: 3, 2: 5, 3: 3, 4: 4, 5: 3},
            "Csus4": {1: 3, 2: 3, 3: 0, 4: 1, 5: 1},
            "D": {2: 0, 3: 2, 4: 3, 5: 2},
            "Dm": {2: 0, 3: 2, 4: 3, 5: 1},
            "D7": {2: 0, 3: 2, 4: 1, 5: 2},
            "DM7": {2: 0, 3: 2, 4: 2, 5: 2},
            "Dm7": {2: 0, 3: 2, 4: 1, 5: 1},
            "Dsus4": {2: 0, 3: 2, 4: 3, 5: 3},
            "E": {0: 0, 1: 2, 2: 2, 3: 1, 4: 0, 5: 0},
            "Em": {0: 0, 1: 2, 2: 2, 3: 0, 4: 0, 5: 0},
            "E7": {0: 0, 1: 2, 2: 0, 3: 1, 4: 0, 5: 0},
            "EM7": {0: 0, 1: 2, 2: 1, 3: 1, 4: 0, 5: 0},
            "Em7": {0: 0, 1: 2, 2: 0, 3: 0, 4: 0, 5: 0},
            "Esus4": {0: 0, 1: 2, 2: 2, 3: 2, 4: 0, 5: 0},
            "F": {0: 1, 1: 3, 2: 3, 3: 2, 4: 1, 5: 1},
            "Fm": {0: 1, 1: 3, 2: 3, 3: 1, 4: 1, 5: 1},
            "F7": {0: 1, 1: 3, 2: 1, 3: 2, 4: 1, 5: 1},
            "FM7": {2: 3, 3: 2, 4: 1, 5: 0},
            "Fm7": {0: 1, 1: 3, 2: 1, 3: 1, 4: 1, 5: 1},
            "Fsus4": {0: 1, 1: 3, 2: 3, 3: 3, 4: 1, 5: 1},
            "G": {0: 3, 1: 2, 2: 0, 3: 0, 4: 0, 5: 3},
            "Gm": {0: 3, 1: 5, 2: 5, 3: 3, 4: 3, 5: 3},
            "G7": {0: 3, 1: 2, 2: 0, 3: 0, 4: 0, 5: 1},
            "GM7": {0: 3, 1: 2, 2: 0, 3: 0, 4: 0, 5: 2},
            "Gm7": {0: 3, 1: 5, 2: 3, 3: 3, 4: 3, 5: 3},
            "Gsus4": {0: 3, 1: 3, 2: 0, 3: 0, 4: 1, 5: 3},
            "A": {1: 0, 2: 2, 3: 2, 4: 2, 5: 0},
            "Am": {1: 0, 2: 2, 3: 2, 4: 1, 5: 0},
            "A7": {1: 0, 2: 2, 3: 0, 4: 2, 5: 0},
            "AM7": {1: 0, 2: 2, 3: 1, 4: 2, 5: 0},
            "Am7": {1: 0, 2: 2, 3: 0, 4: 1, 5: 0},
            "Asus4": {1: 0, 2: 2, 3: 2, 4: 3, 5: 0},
            "B": {1: 2, 2: 4, 3: 4, 4: 4, 5: 2},
            "Bm": {1: 2, 2: 4, 3: 4, 4: 3, 5: 2},
            "B7": {1: 2, 2: 1, 3: 2, 4: 0, 5: 2},
            "BM7": {1: 2, 2: 4, 3: 3, 4: 4, 5: 2},
            "Bm7": {1: 2, 2: 4, 3: 2, 4: 3, 5: 2},
            "Bsus4": {1: 2, 2: 4, 3: 4, 4: 5, 5: 2},
            "Fadd9": {1: 3, 2: 3, 3: 2, 4: 1, 5: 3},
        }

    def find_best_pos(self, midi_pitch: int, is_bass: bool = False,
                      chord_shape: Optional[Dict[int, int]] = None) -> Optional[Tuple[int, int]]:
        """
        Find the best string and fret position for a note, prioritizing playability.

        Args:
            midi_pitch: MIDI pitch number (0-127)
            is_bass: Whether this is a bass note
            chord_shape: Dictionary mapping string indices to fret positions

        Returns:
            Tuple of (string_index, fret_number) or None if no position found
        """
        best_cand = None
        max_score = -999999

        for octave_shift in [-24, -12, 0, 12]:
            shifted_pitch = midi_pitch + octave_shift
            for s_idx in range(self.num_strings):
                fret = shifted_pitch - self.tuning[s_idx]
                if 0 <= fret <= 15:
                    score = 0
                    # Prefer lower frets (0-5) for easier playability
                    if 0 <= fret <= 5:
                        score += 800
                        score += (5 - fret) * 15
                    else:
                        score -= (fret * 150)

                    # Bonus if note matches chord shape
                    if chord_shape and s_idx in chord_shape and chord_shape[s_idx] == fret:
                        score += 2000

                    # Bass notes prefer lower strings
                    if is_bass and s_idx <= 2:
                        score += 100
                    # Melody notes prefer higher strings
                    if not is_bass and s_idx >= 3:
                        score += 50

                    if score > max_score:
                        max_score = score
                        best_cand = (s_idx, fret)

        return best_cand

    def generate_ascii_tab(self, notes: List[Dict[str, Any]]) -> str:
        """
        Generate ASCII tablature from a list of notes.

        Args:
            notes: List of note dictionaries with 'start', 'end', 'pitch', 'velocity'

        Returns:
            ASCII tablature string

        Raises:
            ValueError: If notes list is empty or invalid
        """
        if not notes:
            logger.warning(_("No notes provided for tab generation"))
            return _("No notes detected.")

        try:
            slots_per_measure = 16
            sec_per_measure = (60 / self.bpm) * 4
            max_time = max(n['end'] for n in notes)
            num_measures = int(max_time / sec_per_measure) + 1

            logger.info(_("Generating tab: {} measures, {:.2f} sec/measure").format(
                num_measures, sec_per_measure
            ))

            # Initialize tab grid
            full_tab = [[["-" for _ in range(slots_per_measure)]
                         for _ in range(num_measures)]
                        for _ in range(self.num_strings)]
            measure_chords = ["N.C." for _ in range(num_measures)]

            # Detect chords for each measure
            for m_idx in range(num_measures):
                m_notes = [n for n in notes if int(n['start'] / sec_per_measure) == m_idx]
                measure_chords[m_idx] = self.detect_chord(m_notes)

            # Place notes on the tab
            for n in notes:
                m_idx = int(n['start'] / sec_per_measure)
                if m_idx >= num_measures:
                    continue

                chord_name = measure_chords[m_idx]
                current_shape = self.chord_templates.get(chord_name, {})

                is_bass = n['pitch'] <= self.bass_threshold
                pos = self.find_best_pos(n['pitch'], is_bass, current_shape)

                if pos:
                    s_idx, fret = pos
                    rel_time = n['start'] % sec_per_measure
                    slot_idx = int((rel_time / sec_per_measure) * slots_per_measure)
                    line_idx = self.num_strings - 1 - s_idx

                    fret_str = str(fret)
                    for i, c in enumerate(fret_str):
                        if slot_idx + i < slots_per_measure:
                            full_tab[line_idx][m_idx][slot_idx + i] = c

            logger.info(_("Tab generation completed successfully"))
            return self._render_layout(full_tab, measure_chords, num_measures, slots_per_measure)

        except KeyError as e:
            logger.error(_("Missing required note field: {}").format(str(e)))
            raise ValueError(_("Invalid note format: {}").format(str(e))) from e
        except Exception as e:
            logger.error(_("Tab generation failed: {}").format(str(e)))
            raise RuntimeError(_("Failed to generate tablature: {}").format(str(e))) from e

    def detect_chord(self, m_notes: List[Dict[str, Any]]) -> str:
        """
        Detect the most likely chord from notes in a measure.

        Args:
            m_notes: List of note dictionaries in the measure

        Returns:
            Chord name (e.g., 'C', 'Am', 'G7') or 'N.C.' (No Chord)
        """
        if not m_notes:
            return "N.C."

        pitches = [n['pitch'] % 12 for n in m_notes]
        scores = {}

        for name, shape in self.chord_templates.items():
            template_pitches = set([(self.tuning[s] + f) % 12 for s, f in shape.items()])
            scores[name] = sum(3 for p in pitches if p in template_pitches)

            # Root note bonus
            if shape:
                first_s = next(iter(shape))
                root_pitch = (self.tuning[first_s] + shape[first_s]) % 12
                if root_pitch in pitches:
                    scores[name] += 5

        best = max(scores, key=scores.get)
        detected = best if scores[best] > 5 else "N.C."

        if detected != "N.C.":
            logger.debug(_("Detected chord: {}").format(detected))

        return detected

    def _render_layout(self, full_tab, measure_chords, num_measures, slots_per_measure):
        measures_per_line = 4
        headers = ['e|', 'B|', 'G|', 'D|', 'A|', 'E|']
        header_text = _("🎸 Fingerstyle Precision Analysis")
        output = [f"{header_text} (BPM: {self.bpm:.1f})\n"]

        for start_m in range(0, num_measures, measures_per_line):
            end_m = min(start_m + measures_per_line, num_measures)
            chord_line = "  "
            for m_idx in range(start_m, end_m):
                chord_line += measure_chords[m_idx].ljust(slots_per_measure) + " "
            output.append(chord_line)

            for s_idx in range(self.num_strings):
                line = headers[s_idx]
                for m_idx in range(start_m, end_m):
                    line += "".join(full_tab[s_idx][m_idx]) + "|"
                output.append(line)
            output.append("")

        return "\n".join(output)

def create_tab(notes: List[Dict[str, Any]], bpm: float = 75) -> str:
    """
    Convenience function to create a tablature from notes.

    Args:
        notes: List of note dictionaries
        bpm: Beats per minute (default: 75)

    Returns:
        ASCII tablature string
    """
    generator = TabGenerator(bpm=bpm)
    return generator.generate_ascii_tab(notes)
