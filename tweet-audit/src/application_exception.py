#general exception module that handles exception for the application 

class BaseExceptionClass(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

class EnvironmentVariableError(BaseExceptionClass):
    pass 