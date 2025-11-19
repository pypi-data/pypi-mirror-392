"""
This module defines custom exception classes for the MetronomeApp project.

Exported Exceptions:
- MetronomeError: Base exception class for all custom exceptions specific to MetronomeApp project.
- InvalidRhythmSpecificationError: Custom exception to be raised when the user provides a value for rhythm member that does not validate as valid.
"""


class MetronomeError(Exception):
    """
    Base exception class for all custom exceptions specific to MetronomeApp project.
    """
    pass


class InvalidRhythmSpecificationError(MetronomeError):
    """
    Custom exception to be raised when the user provides a value for rhythm member that does not validate as valid.
    Arguments expected in **kwargs:
    """
    def __init__(self, *args, **kwargs):
        """
        Arguments expected in **kwargs:
            error_msg: A string describing why the rhythm specification is invalid, string
        """
        super().__init__(*args)
        self.error_msg = kwargs.get('error_msg')


