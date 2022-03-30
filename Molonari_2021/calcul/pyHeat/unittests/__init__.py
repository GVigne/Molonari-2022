"""

    @author: Nicolas Flipo
    @date: 14.02.2021

    Init file of the unitests package which contains files for testing
        the package codepyheat
    Defines the path towards the test*.py
    Defines the path towards the parent file for axessing
        the codepyheat package

"""
import pathlib

JSONTESTPATH = str(pathlib.Path(__file__).parent.absolute()) + '/json/'
CODEPATH = str(pathlib.Path(__file__).parent.absolute()) + '/../'


if __name__ == '__main__':
    print(CODEPATH)
