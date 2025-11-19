# Standard
import unittest
import tkinter as tk

# Local
import tkMetronomeApp.MetronomeApp
import tkMetronomeApp.metronome

# TODO: Do the two set_X tests below add any value, since app no longer has setters/getters for tempo and rhythm?
class Test_MetronomeApp(unittest.TestCase):
    def test_set_bpm_get_bpm(self):
        root = tk.Tk()
        myapp = tkMetronomeApp.MetronomeApp.MetronomeApp(root)
        myapp.getModel().tempo = 120
        exp_val = 120
        act_val = myapp.getModel().tempo
        self.assertEqual(exp_val, act_val)

    def test_get_next_beat(self):
        root = tk.Tk()
        myapp = tkMetronomeApp.MetronomeApp.MetronomeApp(root)
        exp_val = (0.5, tkMetronomeApp.metronome.BeatType.STRESSED)
        myapp.getModel().tempo = 120
        act_val = myapp.getModel().next_beat()
        self.assertTupleEqual(exp_val, act_val)

    def test_set_rhythm_get_rhythm(self):
        root = tk.Tk()
        myapp = tkMetronomeApp.MetronomeApp.MetronomeApp(root)
        myapp.getModel().rhythm = 'WrWw'
        exp_val = 'WrWw'
        act_val = myapp.getModel().rhythm
        self.assertEqual(exp_val, act_val)


if __name__ == '__main__':
    unittest.main()
