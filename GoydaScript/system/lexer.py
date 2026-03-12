from .tokens import TokenType, Token


class Lexer:
    def __init__(self, text: str):
        self.text = text
        self.pos = 0
        self.tokens = []
        self._tokenize()

    def _tokenize(self):
        MAX_ITER = 10000
        iter_count = 0

        while self.pos < len(self.text) and iter_count < MAX_ITER:
            iter_count += 1
            char = self.text[self.pos]

            if char.isspace():
                self.pos += 1
                continue

            if char == '#':
                self._skip_comment()
                continue

            if char == '"' or char == "'":
                self._parse_string(char)
                continue

            if char.isdigit() or (char == '.' and self.pos + 1 < len(self.text) and self.text[self.pos + 1].isdigit()):
                self._get_number()
                continue

            if char.isalpha() or char == '_':
                self._get_identifier()
                continue

            if self.pos + 2 < len(self.text):
                three_char = self.text[self.pos:self.pos + 3]
                if three_char == "**=":
                    self.tokens.append(Token(TokenType.POW_ASSIGN, "**="))
                    self.pos += 3
                    continue
                elif three_char == "//=":
                    self.tokens.append(Token(TokenType.FLOORDIV_ASSIGN, "//="))
                    self.pos += 3
                    continue

            if self.pos + 1 < len(self.text):
                two_char = self.text[self.pos:self.pos + 2]
                if two_char == "==":
                    self.tokens.append(Token(TokenType.EQEQ, "=="))
                    self.pos += 2
                    continue
                elif two_char == "!=":
                    self.tokens.append(Token(TokenType.NEQ, "!="))
                    self.pos += 2
                    continue
                elif two_char == ">=":
                    self.tokens.append(Token(TokenType.GTE, ">="))
                    self.pos += 2
                    continue
                elif two_char == "<=":
                    self.tokens.append(Token(TokenType.LTE, "<="))
                    self.pos += 2
                    continue
                elif two_char == "**":
                    self.tokens.append(Token(TokenType.POW, "**"))
                    self.pos += 2
                    continue
                elif two_char == "//":
                    self.tokens.append(Token(TokenType.FLOORDIV, "//"))
                    self.pos += 2
                    continue
                elif two_char == "+=":
                    self.tokens.append(Token(TokenType.PLUS_ASSIGN, "+="))
                    self.pos += 2
                    continue
                elif two_char == "-=":
                    self.tokens.append(Token(TokenType.MINUS_ASSIGN, "-="))
                    self.pos += 2
                    continue
                elif two_char == "*=":
                    self.tokens.append(Token(TokenType.MULT_ASSIGN, "*="))
                    self.pos += 2
                    continue
                elif two_char == "/=":
                    self.tokens.append(Token(TokenType.DIV_ASSIGN, "/="))
                    self.pos += 2
                    continue
                elif two_char == "%=":
                    self.tokens.append(Token(TokenType.MOD_ASSIGN, "%="))
                    self.pos += 2
                    continue

            if char in {'=', ';', '(', ')', '{', '}', ',', '[', ']', '.', ':', '+', '-', '*', '/', '%', '>', '<', '!'}:
                token_map = {
                    '=': TokenType.ASSIGN,
                    ';': TokenType.SEMI,
                    '(': TokenType.LPAREN,
                    ')': TokenType.RPAREN,
                    '{': TokenType.LBRACE,
                    '}': TokenType.RBRACE,
                    ',': TokenType.COMMA,
                    '[': TokenType.LBRACKET,
                    ']': TokenType.RBRACKET,
                    '.': TokenType.DOT,
                    ':': TokenType.COLON,
                    '+': TokenType.PLUS,
                    '-': TokenType.MINUS,
                    '*': TokenType.MULT,
                    '/': TokenType.DIV,
                    '%': TokenType.MOD,
                    '>': TokenType.GT,
                    '<': TokenType.LT,
                    '!': TokenType.NOT
                }
                self.tokens.append(Token(token_map[char], char))
                self.pos += 1
                continue

            self.pos += 1

    def _skip_comment(self):
        self.pos += 1
        while self.pos < len(self.text) and self.text[self.pos] != '\n':
            self.pos += 1

    def _process_keyword_or_id(self, word: str):
        keywords = {
            'func': TokenType.FUNC,
            'main': TokenType.MAIN,
            'int': TokenType.INT,
            'float': TokenType.FLOAT,
            'str': TokenType.STR,
            'bool': TokenType.BOOL,
            'list': TokenType.LIST,
            'tuple': TokenType.TUPLE,
            'dict': TokenType.DICT,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'while': TokenType.WHILE,
            'range': TokenType.RANGE,
            'for': TokenType.FOR,
            'in': TokenType.IN,
            'print': TokenType.PRINT,
            'input': TokenType.INPUT,
            'return': TokenType.RETURN,
            'True': TokenType.TRUE,
            'False': TokenType.FALSE,
            'and': TokenType.AND,
            'or': TokenType.OR,
            'not': TokenType.NOT,
            'is': TokenType.IS,
            'try': TokenType.TRY,
            'except': TokenType.EXCEPT,
            'as': TokenType.AS
        }
        token_type = keywords.get(word, TokenType.ID)
        self.tokens.append(Token(token_type, word))

    def _get_word(self) -> str:
        start = self.pos
        end = start
        while end < len(self.text) and (self.text[end].isalnum() or self.text[end] == '_'):
            end += 1
        if end > start:
            word = self.text[start:end]
            self.pos = end
            return word
        return ""

    def _get_identifier(self):
        word = self._get_word()
        if word:
            self._process_keyword_or_id(word)

    def _get_number(self):
        start = self.pos
        is_float = False

        while self.pos < len(self.text) and (self.text[self.pos].isdigit() or self.text[self.pos] == '.'):
            if self.text[self.pos] == '.':
                is_float = True
            self.pos += 1

        number = self.text[start:self.pos]

        if is_float:
            self.tokens.append(Token(TokenType.FLOAT_NUMBER, number))
        else:
            self.tokens.append(Token(TokenType.NUMBER, number))

    def _parse_string(self, quote_char):
        self.pos += 1
        start = self.pos

        while self.pos < len(self.text) and self.text[self.pos] != quote_char:
            if self.text[self.pos] == '\\' and self.pos + 1 < len(self.text):
                self.pos += 2
            else:
                self.pos += 1

        string_content = self.text[start:self.pos]
        self.tokens.append(Token(TokenType.STRING, string_content))

        if self.pos < len(self.text) and self.text[self.pos] == quote_char:
            self.pos += 1

    def get_tokens(self):
        return self.tokens