"""
This module defines the tkMetronomeViewManager class, which is a concrete implementation of tkViewManager for a metronome application.
Acts as Observer, and handles the interactions between the metronome app's widgets, which are also defined in this module.

Exported Classes:
    tkMetronomeViewManager -- Concrete implementation of tkViewManager for a metronome application.

Exported Exceptions:
    None    
 
Exported Functions:
    None
"""


# Standard imports
import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import showerror
import winsound
import logging

# Local imports
from tkAppFramework.tkViewManager import tkViewManager
from tkAppFramework.ObserverPatternBase import Subject
import tkMetronomeApp.metronome
import tkMetronomeApp.exceptions


class tkMetronomeViewManager(tkViewManager):
    """
    Concrete implementation of tkViewManager. Acts as Observer, and handles the interactions between metronome app's widgets.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: The parent widget of this widget, The MetronomeApp, which hereafter will be
        accessed as self.master.
        """
        tkViewManager.__init__(self, parent)
        
        self._beat_after_id = 0 # The id of each successive tkinter "after" event that controls the timing of the next beat.
        self._beacon_state = tkMetronomeApp.metronome.BeatType.REST
        
    def _CreateWidgets(self):
        """
        Implementation of tkViewManager._CreateWidgets.
        Sets up and registers the child widgets of the tkMetronomeViewManager widget.
        :return None:
        """
        self._bpm_widget = MetronomeBpmWidget(self, bpm=self.getModel().tempo)
        self.register_subject(self._bpm_widget, self.handle_bmp_widget_update)
        self._bpm_widget.attach(self)
        self._bpm_widget.grid(column=0, row=0, rowspan=3, sticky='NWES') # Grid-2
        self.columnconfigure(0, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2

        self._beacon_widget = MetronomeBeaconWidget(self)
        self._beacon_widget.grid(column=1, row=0, sticky='NWES') # Grid-2
        self.columnconfigure(1, weight=1) # Grid-2
        self.rowconfigure(0, weight=1) # Grid-2

        self._rhythm_widget = MetronomeRhythmWidget(self, rhythm=self.getModel().rhythm)
        self.register_subject(self._rhythm_widget, self.handle_rhythm_widget_update)
        self._rhythm_widget.attach(self)
        self._rhythm_widget.grid(column=1, row=1, sticky='NWES') # Grid-2
        self.columnconfigure(1, weight=1) # Grid-2
        self.rowconfigure(1, weight=1) # Grid-2

        self._start_stop_widget = MetronomeStartStopWidget(self)
        self.register_subject(self._start_stop_widget, self.handle_start_stop_widget_update)
        self._start_stop_widget.attach(self)
        self._start_stop_widget.grid(column=1, row=2, sticky='NWES') # Grid-2
        self.columnconfigure(1, weight=1) # Grid-2
        self.rowconfigure(2, weight=1) # Grid-2

        return None

    def handle_model_update(self):
        """
        Handle updates from the model.
        :return None:
        """
        model_bpm = self.getModel().tempo
        widget_bpm = self._bpm_widget.get_state()
        # For efficiency, only update the bpm widget if it's bpm value doesn't match the model value.
        if widget_bpm != model_bpm:
            self._bpm_widget._value_bpm.set(model_bpm)
        
        model_rhythm = self.getModel().rhythm
        (widget_rhythm, widget_rhythm_valid) = self._rhythm_widget.get_state()
        # For efficiency, only update the rhythm widget if it's rhythm value doesn't match the model value.
        if widget_rhythm != model_rhythm:
            self._rhythm_widget._value_rhythm.set(model_rhythm)
        
        return None
        
    def handle_start_stop_widget_update(self):
        """
        Handle updates from the start_stop_widget:
        :return None:
        """
        if self._start_stop_widget.get_state():
            # Metronome should be started.

            # Disable the rhythm widget. Can't change the rhythm while the metronome is started.
            self._rhythm_widget.disable_rhythm_entry(True)

            # Start the event loop calling beat(...)
            self.beat()
        else:
            # Metronome should be stopped.

            # Enable the rhythm widget. Can change the rhythm when the metronome is stopped.
            self._rhythm_widget.disable_rhythm_entry(False)

            # Cancel the beat after callback
            self.master.after_cancel(self._beat_after_id)
            # Reset the beat after id
            self._beat_after_id = 0
            # Turn off beacon light
            self._beacon_widget.set_state(tkMetronomeApp.metronome.BeatType.REST)

        return None

    def handle_bmp_widget_update(self):
        """
        Handle updates from bpm widget.
        :return None:
        """
        model_bpm = self.getModel().tempo
        widget_bpm = self._bpm_widget.get_state()
        # For efficiency, only update the model bpm value if it doesn't match the widget value.
        if model_bpm != widget_bpm:
            self.getModel().tempo = widget_bpm
        return None

    def handle_rhythm_widget_update(self):
        """
        Handle updates from the rhythm widget.
        :return None:
        """
        (rhythm_str, rhythm_valid) = self._rhythm_widget.get_state()
        if rhythm_valid:
            model_rhythm = self.getModel().rhythm
            # For efficiency, only update the model rhythm value if it doesn't match the widget value.
            if model_rhythm != rhythm_str:
                self.getModel().rhythm = rhythm_str
            # Enable start/stop button, since can run metronome with a valid rhythm
            self._start_stop_widget.disable(False)
        else:
            # Disable start/stop button, since can't run metronome with an invalid rhythm
            self._start_stop_widget.disable(True)
        return None

    def beat(self):
        """
        This is the function that is called to actually "tick" the metronome. Note that the timing of the beat is managed by the
        tkinter event loop.
        :return None:
        """
        # Note: It may seem a little odd that this function is part of the view manager, but:
        # (1) It is here, and not in the App, because the App shouldn't have to know about the details of the widgets.
        # (2) It is here, and not in the model, because the timing mechanism is part of the tkinter event loop.

        # Get the logger 'metronome_app_logger'
        logger = logging.getLogger('metronome_app_logger')

        # Determine beat delay, the time until the next beat (click) of the metronome in seconds
        (beat_delay, stressed) = self.getModel().next_beat()
        logger.debug(f"delay (s): {beat_delay}, stressed beat: {stressed}")
        
        # Turn off beacon, in case it was turned on by a previous beat
        self._beacon_widget.set_state(tkMetronomeApp.metronome.BeatType.REST)
        
        # TODO: Make the frequency and duration of the beep for stressed and normal beats configurable.

        # Beep (unless it is a rest beat)
        if stressed is not tkMetronomeApp.metronome.BeatType.REST:
            if stressed is tkMetronomeApp.metronome.BeatType.STRESSED:
                frequency = 2500  # Set Frequency To 2500 Hertz
                duration = 100  # Set Duration To 50 ms == 0.05 second (must be < 250, since maximum bpm is 240)
            elif stressed is tkMetronomeApp.metronome.BeatType.NORMAL:
                frequency = 2500  # Set Frequency To 2500 Hertz
                duration = 50  # Set Duration To 50 ms == 0.05 second (must be < 250, since maximum bpm is 240)
            winsound.Beep(frequency, duration)

        # Turn on beacon, to "flash" it as part of the beat, for either a normal or stressed beat
        self._beacon_widget.set_state(stressed)

        self._beat_after_id = self.master.after(int(1000.0*beat_delay), self.beat)

        return None


class MetronomeBpmWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which allow the beats per minute of the metronome to be set.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent, bpm=0) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget, in this case the tkMetronomeViewManager
        :parameter bpm: An initial beats per minute setting for this widget, int
        """
        ttk.Labelframe.__init__(self, parent, text="Beats Per Minute")
        Subject.__init__(self)

        self._scale_bpm = tk.Scale(self, orient=tk.VERTICAL, length='2i', from_=30, to=240, command=self.OnBpmChanged,
                                   tickinterval=30, takefocus=1)
        self._scale_bpm.grid(column=0, row=0) # Grid-3
        self.columnconfigure(0, weight=1) # Grid-3
        self.rowconfigure(0, weight=1) # Grid-3
        self._value_bpm=tk.IntVar()
        self._value_bpm.set(bpm)
        self._scale_bpm['variable']=self._value_bpm

    def OnBpmChanged(self, value):
        """
        Event handler for changes to bpm scale.
        :return None:
        """
        # Inform all observers of the change in beats per minute of the metronome.
        self.notify()
        return None

    def get_state(self):
        """
        Return the bpm value from the widget.
        """
        return self._value_bpm.get()


class MetronomeStartStopWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which will allow the metronome to be started and stopped.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget, in this case the tkMetronomeViewManager
        """
        ttk.Labelframe.__init__(self, parent, text='Start/Stop')
        Subject.__init__(self)
        
        self._btn_start_stop = ttk.Button(self, command=self.OnStartStopButtonClicked)
        self._btn_start_stop.grid(column=0, row=0) # Grid-3
        self.columnconfigure(0, weight=1) # Grid-3
        self.rowconfigure(0, weight=1) # Grid-3
        self._lbl_start_stop=tk.StringVar()
        self._lbl_start_stop.set('Start')
        self._btn_start_stop['textvariable']=self._lbl_start_stop
        self._is_started = False

    def get_state(self):
        """
        Return whether the widget's state is started or stopped. Returns this as a bool which is True if started,
        and False if NOT started (that is, stopped).
        :return isStarted: True if started, False if stopped, bool
        """
        return self._is_started
    
    def OnStartStopButtonClicked(self):
        """
        Event handler for start/stop button click.
        :return None:
        """
        # Flip the started state
        if self._is_started:
            # Metronome state is currently started, so change state to stopped
            self._is_started = False
            # Change button text to 'Start'
            self._lbl_start_stop.set('Start')
        else:
            # Metronome state is currently stopped, so change it's state to started
            self._is_started = True
            # Change button text to 'Stop'
            self._lbl_start_stop.set('Stop')

        # Notify observers
        self.notify()

        return None
    
    def disable(self, disabled=True):
        """
        Used to set if the widget is enabled or disabled.
        :parameter disabled: True if the widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if disabled:
            self._btn_start_stop.state(['disabled'])
        else:
            self._btn_start_stop.state(['!disabled'])
        return None


class MetronomeRhythmWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which allow the rhythm of the metronome to be set.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent, rhythm='') -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget, in this case the tkMetronomeViewManager
        :parameter rhythm: An initial rhythm pattern setting for this widget, string
        """
        ttk.Labelframe.__init__(self, parent, text='Rhythm')
        Subject.__init__(self)

        OnRhythmChangedCommand = self.register(self.OnRhythmChanged)
        OnInvalidRhythmChangeCommand = self.register(self.OnInvalidRhythmChange)
        self._entry_rhythm = ttk.Entry(self, validate='focusout', validatecommand=OnRhythmChangedCommand,
                                       invalidcommand=OnInvalidRhythmChangeCommand)
        self._entry_rhythm.grid(column=0, row=0) # Grid-3
        self.columnconfigure(0, weight=1) # Grid-3
        self.rowconfigure(0, weight=1) # Grid-3
        self._value_rhythm=tk.StringVar()
        self._value_rhythm.set(rhythm)
        self._entry_rhythm['textvariable']=self._value_rhythm
        self._rhythm_is_valid = True

    def OnRhythmChanged(self):
        """
        Event handler for changes to rhythm entry.
        :return True: if rhythm change is valid, False if invalid, boolean
        """
        # Inform all observers of the change in rhythm setting of the metronome.
        try:
            # Validity here is an assumption only. If it isn't a good assumption, exception will be raised
            # when notify() is called, and OnInvalidRhythmChange() will correct to False.
            self._rhythm_is_valid = True
            self.notify()
            return True
        except tkMetronomeApp.exceptions.InvalidRhythmSpecificationError as e:
            showerror(title='Metronome Rhythm Error', message=e.error_msg, parent=self)
            return False

    def OnInvalidRhythmChange(self):
        """
        Called when OnRhythmChanged returns False.
        :return None:
        """
        self._rhythm_is_valid = False
        self.notify()
        return None

    def get_state(self):
        """
        Return the rhythm value and validity from the widget, as tuple (value as str, valid as boolean)
        """
        return (self._entry_rhythm.get(), self._rhythm_is_valid)

    def disable_rhythm_entry(self, disabled=True):
        """
        Used to set if the widget will accept a rhythm entry or not.
        :parameter disabled: True if the rhythm entry widget should be disabled, False if it should be enabled, boolean
        :return None:
        """
        if disabled:
            self._entry_rhythm.state(['disabled'])
        else:
            self._entry_rhythm.state(['!disabled'])
        return None


class MetronomeBeaconWidget(ttk.Labelframe, Subject):
    """
    Class represents a tkinter label frame, the widget contents of which will be a visual indicator of the metronome's timing tick.
    Class is also a Subject in Observer design pattern.
    """
    def __init__(self, parent) -> None:
        """
        :parameter parent: tkinter widget that is the parent of this widget, in this case the tkMetronomeViewManager
        """
        ttk.Labelframe.__init__(self, parent, text='Beacon')
        Subject.__init__(self)
        
        self._btn_beacon=tk.Button(self)
        self._btn_beacon.grid(column=0, row=0) # Grid-3
        self.columnconfigure(0, weight=1) # Grid-3
        self.rowconfigure(0, weight=1) # Grid-3
        self._lbl_beacon=tk.StringVar()
        self._lbl_beacon.set('--')
        self._btn_beacon['textvariable']=self._lbl_beacon
        self._btn_beacon['height']=8
        self._btn_beacon['width']=10
        self._btn_beacon['background']='black'
        self._btn_beacon['state']=tk.DISABLED

    def set_state(self, state = tkMetronomeApp.metronome.BeatType.REST):
        """
        Maps argument state onto background color and sets it.
        :parameter state: What state should the beacon be set at, BeatType Enum
        :return None:
        """
        # TODO: Make the colors configurable, especially for color-blind users.
        match state:
            case tkMetronomeApp.metronome.BeatType.REST:
                self._btn_beacon['background']='black'
            case tkMetronomeApp.metronome.BeatType.NORMAL:
                self._btn_beacon['background']='green'
            case tkMetronomeApp.metronome.BeatType.STRESSED:
                self._btn_beacon['background']='red'
        self.master.update_idletasks()

        return None