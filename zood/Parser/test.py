
from .config import _SHOULD_LOG_SCOPE

class A:
    
    def __init__(self) -> None:
        print("initial class A")
        
    def fun(self):
        print("called function!")
        print(_SHOULD_LOG_SCOPE)