# MetronomeApp

Source code: [GitHub](https://github.com/KevinRGeurts/tkMetronomeApp)
---
MetronomeApp is a Python tkinter application that provides metronome functionality.
It allows users to set a tempo in beats per minute (BPM), to set a rhythm for the beats, and to start and stop the metronome.
Beats sound an audible beep and flash a visual indicator, with stressed and unstressed beats visually and audibly distinct.

## Requirements

- tkAppFramework>=0.9.0: [GitHub](https://github.com/KevinRGeurts/tkAppFramework), [PyPi](https://pypi.org/project/tkAppFramework/)

## Basic usage

The simplest way to run the app is:

```
python -m tkMetronomeApp.MetronomeApp 
```

This assumes that the tkMetronomeApp package is installed. To learn how to use the app, select Help | View Help... from the menu bar.

## Unittests

Unittests for the tkMetronomeApp are in the tests directory, with filenames starting with test_. To run the unittests,
type ```python -m unittest discover -s ..\..\tests -v``` in a terminal window in the src\tkMetronomeApp directory.

## License

MIT License. See the LICENSE file for details