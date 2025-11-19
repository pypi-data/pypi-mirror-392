"""
This module defines the metronome class, which represents the "business logic" of a metronome.

Exported Classes:
    Metronome -- Concrete implementation tkAppFrammework.Model for a metronome application.
    BeatType -- Enum representing the type of metronome beat (REST, NORMAL, STRESSED).

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# standard imports
from enum import Enum
import re as re

# local imports
import tkMetronomeApp.exceptions
from tkAppFramework.model import Model
import json


class BeatType(Enum):
    """
    An enumeration that represents the type of the metronome beat.
    """
    REST = 1
    NORMAL = 2
    STRESSED = 3


class Metronome(Model):
    """
    This class represents the "business logic" of a metronome, and is a Model in the MVC pattern.
        _tempo: The tempo of the metronome, in bpm (beats per minute), int
        _rhythm: A string representing the rhythm of the metronome beats, string
        _current_beat: Current location in the rhythm string, int
    """
    def __init__(self, tempo = 60, rhythm = 'Wwww'):
        """
        :parameter tempo: The tempo of the metronome, in bpm (beats per minute), int
        :parameter rhythm: A string representing the rhythm of the metronome beats, string
        """
        super().__init__()
        self.tempo = tempo
        self.rhythm = rhythm 
        self._current_beat = 0

    @property
    def tempo(self):
        return self._tempo

    @tempo.setter
    def tempo(self, value):
        assert(value > 0)
        self._tempo = value
        self.notify()

    @property
    def rhythm(self):
        return self._rhythm

    @rhythm.setter
    def rhythm(self, value):
        self._validate_rhythm(value)
        self._rhythm = value
        # Reset _current_beat to beginning of rhythm string
        self._current_beat=0
        self.notify()

    def next_beat(self):
        """
        Returns information about the next metronome beat, and advances _current beat.
        :return: (beat delay in seconds, stressed? (NORMAL/STRESSED)), as (float, BeatType Enum)
        Note: The beat delay is really the delay until the next beat, or the duration of the current beat.
              stressed is whether or not the current beat is a stressed beat.
        """
        beat_delay = 0
        beat_factor = 1
        stressed = BeatType.NORMAL
        beat_code = self.rhythm[self._current_beat]
        match beat_code:
            case 'W':
                stressed = BeatType.STRESSED
                beat_factor = 1 
            case 'w':
                stressed = BeatType.NORMAL
                beat_factor = 1.0
            case 'r':
                stressed = BeatType.REST
                beat_factor = 1.0 
            case 'H':
                stressed = BeatType.STRESSED
                beat_factor = 0.5 
            case 'h':
                stressed = BeatType.NORMAL
                beat_factor = 0.5
            case 'Q':
                stressed = BeatType.STRESSED
                beat_factor = 0.25 
            case 'q':
                stressed = BeatType.NORMAL
                beat_factor = 0.25
        beat_delay = beat_factor / (self.tempo / 60.)

        # Advance current beat
        self._current_beat += 1
        
        # Loop current beat back to beginning of rhythm string when necessary
        if self._current_beat >= len(self.rhythm):
            self._current_beat = 0

        return (beat_delay, stressed)

    def _validate_rhythm(self, rhythm_str):
        """
        Validate that rhythm_str is a valid specification for self.rhythm.
        :parameter rhythm_str: String to test as being a valid rhythm specification, string
        :return: None
        Raises InvalideRhythmSpecificationError if rhythm_str is an invalid rhythm specification.
        """
        match_result = re.match('[WwHhQqr]+', rhythm_str)
        # For rhythm_str to be valid, the match must be the same length as rhythm_str
        if  not match_result or len(rhythm_str) != len(match_result[0]):
            # TODO: Enhance error message to include which part(s) of the rhythm specification are invalid.
            # Hopefully functionality of regular expression matching can help with this.
            msg = 'Metronome rhythm specification is not valid.'
            msg += 'It must contain only characters from this set: WwHhQqr'
            raise tkMetronomeApp.exceptions.InvalidRhythmSpecificationError(error_msg = msg)
        return None

    def readModelFromFile(self, file, filetype) -> None:
        """
        Read the model data from a file-like object.
        :parameter file: A file-like object from which to read the model data.
        :parameter filetype: A string indicating the type of file (e.g., 'json', 'xml', etc.).
        :return: None
        """
        # Read the JSON string from the file-like object
        if filetype != '.json':
            raise ValueError('Metronome.readModelFromFile() only supports filetype ".json"')
        json_string = file.read()
        # Convert the JSON string to a dictionary
        data = json.loads(json_string)
        # Map the data dictionary to the model attributes
        self.tempo = data['tempo']
        self.rhythm = data['rhythm']
        # Inform observers that the model has changed
        self.notify()
        return None    

    def writeModelToFile(self, file, filetype) -> None:
        """
        Write the model data to a file-like object.
        :parameter file: A file-like object to which to write the model data.
        :parameter filetype: A string indicating the type of file (e.g., 'json', 'xml', etc.).
        :return: None
        """
        if filetype != '.json':
            raise ValueError('Metronome.writeModelToFile() only supports filetype ".json"')
        # Add the model data to a dictionary
        data = {'tempo': self.tempo, 'rhythm': self.rhythm}
        # Convert the dictionary to a JSON string
        json_string = json.dumps(data)
        # Write the JSON string to the file-like object
        file.write(json_string)
        return None






