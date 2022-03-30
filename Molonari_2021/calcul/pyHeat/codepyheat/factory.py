"""

    @author: Ralph Mueller
    @date: 21.02.2021

    class functions for setting config data for local classes
    - json files
    - json strings
    - dictionaries

"""
from abc import ABCMeta, abstractmethod
import json


class FactoryClass(metaclass=ABCMeta):

    @classmethod
    def fromDict(cls, a_dict):
        """
            instantiates from a dictionary, no validity tests here
        """
        return cls(a_dict)

    @classmethod
    def fromJsonString(cls, a_json_string):
        """
            instantiates from a json string, no validity tests here
        """
        try:
            a_dict = json.loads(a_json_string)
        except ValueError:
            # not a valid json string
            print('not a valid JSON string')
            return None
        return cls(a_dict)

    @classmethod
    def fromJsonFile(cls, a_filename):
        """
            instantiates from a json file

            exceptions:
            - file not found
            - value error

        """
        try:
            with open(a_filename) as json_file:
                a_dict = json.load(json_file)
        except FileNotFoundError as e:
            print(e)
            raise(e)
        except ValueError as e:
            # not a valid json string
            print(e)
            raise(e)
        return cls(a_dict)

    @abstractmethod
    def __init__(self, a_dict):
        return
