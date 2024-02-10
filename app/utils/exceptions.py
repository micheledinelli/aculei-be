class CustomException(Exception):
    def __init__(self, message):
        self.message = message

    def __init__(self, message, error_code):
        self.message = message
        self.error_code = error_code