from system.tokens import TokenType, Token

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

            if char == '"':
                self._parse_string()
                continue

            if char.isdigit():
                self._get_number()
                continue

            if char.isalpha():
                self._get_identifier()
                continue

            if self.pos + 1 < len(self.text) and self.text[self.pos:self.pos + 2] == "==":
                self.tokens.append(Token(TokenType.EQEQ, "=="))
                self.pos += 2
                continue

            if char in {'=', ';', '(', ')', '{', '}', ',', '[', ']', '.'}:
                token_type = {
                    '=': TokenType.ASSIGN,
                    ';': TokenType.SEMI,
                    '(': TokenType.LPAREN,
                    ')': TokenType.RPAREN,
                    '{': TokenType.LBRACE,
                    '}': TokenType.RBRACE,
                    ',': TokenType.COMMA,
                    '[': TokenType.LBRACKET,
                    ']': TokenType.RBRACKET,
                    '.': TokenType.DOT
                }[char]
                self.tokens.append(Token(token_type, char))
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
            'list': TokenType.LIST,
            'if': TokenType.IF,
            'else': TokenType.ELSE,
            'range': TokenType.RANGE,
            'for': TokenType.FOR,
            'in': TokenType.IN,
            'print': TokenType.PRINT,
            'input': TokenType.INPUT,
            'return': TokenType.RETURN
        }

        token_type = keywords.get(word, TokenType.ID)
        self.tokens.append(Token(token_type, word))

    def _get_word(self) -> str:
        start = self.pos
        end = start
        while end < len(self.text) and self.text[end].isalnum():
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
        while self.pos < len(self.text) and self.text[self.pos].isdigit():
            self.pos += 1
        number = self.text[start:self.pos]
        self.tokens.append(Token(TokenType.NUMBER, number))

    def _parse_string(self):
        self.pos += 1  # "
        start = self.pos
        while self.pos < len(self.text) and self.text[self.pos] != '"':
            self.pos += 1
        string_content = self.text[start:self.pos]
        self.tokens.append(Token(TokenType.STRING, string_content))
        if self.pos < len(self.text) and self.text[self.pos] == '"':
            self.pos += 1

    def get_tokens(self):
        return self.tokens