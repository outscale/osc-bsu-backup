class Error(Exception):
    """Base class for exceptions in this module."""


class InputError(Error):
    def __init__(self, message: str):
        self.message = message
