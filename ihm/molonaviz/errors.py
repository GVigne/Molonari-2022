from datetime import timedelta

class EmptyFieldError(Exception):

    """
    classdoc
    """

    def __init__(self, message: str='Please do not leave any field blank'):
        self.message = message

    def __str__(self):
        return self.message

class TimeStepError(Exception):

    """
    classdoc
    """

    def __init__(self, timeStepTemp: timedelta, timeStepPress: timedelta):
        self.timeStepTemp = timeStepTemp
        self.timeStepPress = timeStepPress
    
    def __str__(self):
        return f"Time steps aren't matching : {self.timeStepTemp} in the pressures file, {self.timeStepPress} in the temperatures file"

class TextFileError(Exception):

    """
    classdoc
    """

    def __init__(self, filesNumber: int):
        self.filesNumber = filesNumber

    def __str__(self):
        if self.filesNumber == 0:
            message = 'No text file found in root directory'
        else : 
            message = f'Too many text files found in root directory ({self.filesNumber})'
        return message
    
    def getFilesNumber(self):
        return self.filesNumber

class LoadingError(Exception):

    """
    classdoc
    """

    def __init__(self, object: str):
        self.object = object

    def __str__(self):
        return f"Error : Couldn't load {self.object}"

class CustomError(Exception) :
    """
    classdoc
    """

    def __init__(self, message: str="Error"):
        self.message = message

    def __str__(self):
        return self.message



