"""
Module that implements a decorator allowing a method of user-defined class instance to become a "checker".
Also creates a new associated error type.
"""

from functools import wraps


class ComputationOrderException(Exception):
    """Exception raised when a method with a needed tag is computed before the linked checker."""


def checker(checked_meth):
    """
    Transform a bound method of user-defined class instance to a "checker" method.
    Each method decorated with the .needed would raise a ComputationOrderException.
    It is also possible to reset the checker with .reset.

    Args:
        checked_meth (method): a bound method of user-defined class instance

    Returns:
            method: checker method
    """

    def reset(col):
        col.__dict__[check_name] = False

    def needed(meth):
        @wraps(meth)
        def new_meth(self, *args, **kargs):
            if (
                check_name in self.__dict__
                and self.__dict__[check_name]
            ):
                return meth(self, *args, **kargs)
            raise ComputationOrderException(
                f"{checked_meth.__name__} has to be computed before calling {meth.__name__}."
            )

        return new_meth

    @wraps(checked_meth)
    def wrapper(self, *args, **kwargs):
        self.__dict__[check_name] = True
        return checked_meth(self, *args, **kwargs)

    check_name = "_" + checked_meth.__name__
    wrapper.reset = reset
    wrapper.needed = needed
    return wrapper
