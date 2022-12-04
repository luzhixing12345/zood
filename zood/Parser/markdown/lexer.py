
from enum import Enum

class TokenType(Enum):
    
    # page header keyword
    SORT        = 'sort'
    
    # markdown
    COLON       = ':'
    BAR         = '-'
    POINT       = '.'
    DELIMITER   = '---'
    