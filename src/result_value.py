
from enum import Enum
from abc import abstractmethod

from typing import Union, Optional, Tuple, List, Any, cast
from typing import Callable, TypeVar, Generic

class ResultValue(object):
    @abstractmethod
    def __init__(self, value:Union[Exception, Any])-> None :
        self._value = value
        self._in_error = True

    def __call__(self):
        return self._value

    def __str__(self)-> str :
        return "Is error: {e} - {t}".format(e=self._in_error, t=type(self._value))

    def is_in_error(self)-> bool :
        return self._in_error
    
    def is_ok(self)-> bool :
        return not self._in_error

    def value(self)-> Any :
        return self._value
        
class ResultOk(ResultValue):
    def __init__(self, value:Any)-> None :
        super(ResultOk, self).__init__(value)
        self._in_error = False

    def value(self)-> Any :
        return self._value

class ResultKo(ResultValue):
    def __init__(self, value:Exception)-> None :
        super(ResultKo, self).__init__(value)
        self._in_error = True

    def value(self)-> Exception :
        return self._value

