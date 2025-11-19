# Standard imports
import unittest

# Local imports
import tkMetronomeApp.metronome
import tkMetronomeApp.exceptions


class Test_metronome(unittest.TestCase):
    def test_next_beat_W(self):
        met = tkMetronomeApp.metronome.Metronome(tempo=60, rhythm='W')
        (delay, stressed) = met.next_beat()
        exp_val = (1.0, tkMetronomeApp.metronome.BeatType.STRESSED)
        act_val = (delay, stressed)
        self.assertTupleEqual(exp_val, act_val)

    def test_next_beat_w(self):
        met = tkMetronomeApp.metronome.Metronome(tempo=60, rhythm='w')
        (delay, stressed) = met.next_beat()
        exp_val = (1.0, tkMetronomeApp.metronome.BeatType.NORMAL)
        act_val = (delay, stressed)
        self.assertTupleEqual(exp_val, act_val)

    def test_next_beat_H(self):
        met = tkMetronomeApp.metronome.Metronome(tempo=60, rhythm='H')
        (delay, stressed) = met.next_beat()
        exp_val = (0.5, tkMetronomeApp.metronome.BeatType.STRESSED)
        act_val = (delay, stressed)
        self.assertTupleEqual(exp_val, act_val)

    def test_next_beat_h(self):
        met = tkMetronomeApp.metronome.Metronome(tempo=60, rhythm='h')
        (delay, stressed) = met.next_beat()
        exp_val = (0.5, tkMetronomeApp.metronome.BeatType.NORMAL)
        act_val = (delay, stressed)
        self.assertTupleEqual(exp_val, act_val)

    def test_next_beat_Q(self):
        met = tkMetronomeApp.metronome.Metronome(tempo=60, rhythm='Q')
        (delay, stressed) = met.next_beat()
        exp_val = (0.25, tkMetronomeApp.metronome.BeatType.STRESSED)
        act_val = (delay, stressed)
        self.assertTupleEqual(exp_val, act_val)

    def test_next_beat_q(self):
        met = tkMetronomeApp.metronome.Metronome(tempo=60, rhythm='q')
        (delay, stressed) = met.next_beat()
        exp_val = (0.25, tkMetronomeApp.metronome.BeatType.NORMAL)
        act_val = (delay, stressed)
        self.assertTupleEqual(exp_val, act_val)

    def test_next_beat_r(self):
        met = tkMetronomeApp.metronome.Metronome(tempo=60, rhythm='r')
        (delay, stressed) = met.next_beat()
        exp_val = (1.0, tkMetronomeApp.metronome.BeatType.REST)
        act_val = (delay, stressed)
        self.assertTupleEqual(exp_val, act_val)

    def test_next_beat_twice(self):
        met = tkMetronomeApp.metronome.Metronome(tempo=60, rhythm='Ww')
        met.next_beat()
        (delay, stressed) = met.next_beat()
        exp_val = (1.0, tkMetronomeApp.metronome.BeatType.NORMAL)
        act_val = (delay, stressed)
        self.assertTupleEqual(exp_val, act_val)

    def test_next_beat_loop(self):
        met = tkMetronomeApp.metronome.Metronome(tempo=60, rhythm='Ww')
        met.next_beat()
        met.next_beat()
        (delay, stressed) = met.next_beat()
        exp_val = (1.0, tkMetronomeApp.metronome.BeatType.STRESSED)
        act_val = (delay, stressed)
        self.assertTupleEqual(exp_val, act_val)

    def test_validate_rhythm_good(self):
        met = tkMetronomeApp.metronome.Metronome()
        exp_val = None
        act_val = met._validate_rhythm('Ww')
        self.assertEqual(exp_val, act_val)
        
    def test_validate_rhythm_empty(self):
        self.assertRaises(tkMetronomeApp.exceptions.InvalidRhythmSpecificationError, tkMetronomeApp.metronome.Metronome, rhythm='')

    def test_validate_rhythm_bad(self):
        self.assertRaises(tkMetronomeApp.exceptions.InvalidRhythmSpecificationError, tkMetronomeApp.metronome.Metronome, rhythm='Wx')

if __name__ == '__main__':
    unittest.main()
