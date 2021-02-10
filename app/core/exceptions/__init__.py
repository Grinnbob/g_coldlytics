
class AppErrors(Exception):
    """Base class for all App-related errors."""
    def __init__(self, message):
        self.message = message

class AppValidationError(AppErrors):
    def __init__(self, original, message):
        self.original = original
        self.message = message

class AppCredentialsChanged(AppErrors):
    def __init__(self, new_creds, original=None, message=None):
        self.original = original
        self.message = message
        self.new_creds = new_creds


