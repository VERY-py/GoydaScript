from enum import Enum
class TokenType(Enum):
    FUNC = "FUNC"
    MAIN = "MAIN"
    INT = "INT"
    LIST = "LIST"
    ID = "ID"
    ASSIGN = "="
    SEMI = ";"
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    LBRACKET = "["
    RBRACKET = "]"
    IF = "IF"
    ELSE_IF = "ELSE_IF"
    ELSE = "ELSE"
    FOR = "FOR"
    IN = "IN"
    EQEQ = "=="
    PRINT = "PRINT"
    RANGE = "RANGE"
    NUMBER = "NUMBER"
    INPUT = "INPUT"
    STRING = "STRING"
    RETURN = "RETURN"
    COMMENT = "COMMENT"
    COMMA = ","
    DOT = "."

class Token:
    def __init__(self, type_: TokenType, value: str = ""):
        self.type = type_
        self.value = value