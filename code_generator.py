import random

# Token types for syntax highlighting
TOKEN_KEYWORD = "keyword"
TOKEN_STRING = "string"
TOKEN_COMMENT = "comment"
TOKEN_NUMBER = "number"
TOKEN_OPERATOR = "operator"
TOKEN_DEFAULT = "default"

# Each template is a list of (text, token_type) tuples
TEMPLATES = [
    [("if", TOKEN_KEYWORD), (" (vibes == ", TOKEN_OPERATOR), ("good", TOKEN_DEFAULT),
     (")", TOKEN_OPERATOR), (" { ", TOKEN_OPERATOR), ("ship_it", TOKEN_DEFAULT),
     ("();", TOKEN_OPERATOR), (" }", TOKEN_OPERATOR)],

    [("const", TOKEN_KEYWORD), (" bugs = ", TOKEN_OPERATOR), ("0", TOKEN_NUMBER),
     (";", TOKEN_OPERATOR), (" // ", TOKEN_COMMENT), ("trust me bro", TOKEN_COMMENT)],

    [("function", TOKEN_KEYWORD), (" vibeCheck", TOKEN_DEFAULT), ("() {", TOKEN_OPERATOR),
     (" ", TOKEN_DEFAULT), ("return", TOKEN_KEYWORD), (" ", TOKEN_DEFAULT),
     ("true", TOKEN_KEYWORD), (";", TOKEN_OPERATOR), (" }", TOKEN_OPERATOR)],

    [("while", TOKEN_KEYWORD), (" (", TOKEN_OPERATOR), ("coffee", TOKEN_DEFAULT),
     (" > ", TOKEN_OPERATOR), ("0", TOKEN_NUMBER), (")", TOKEN_OPERATOR),
     (" { ", TOKEN_OPERATOR), ("code", TOKEN_DEFAULT), ("();", TOKEN_OPERATOR),
     (" }", TOKEN_OPERATOR)],

    [("// ", TOKEN_COMMENT), ("TODO: fix this later", TOKEN_COMMENT),
     (" (", TOKEN_COMMENT), ("written 3 years ago", TOKEN_COMMENT), (")", TOKEN_COMMENT)],

    [("console", TOKEN_DEFAULT), (".", TOKEN_OPERATOR), ("log", TOKEN_DEFAULT),
     ("(", TOKEN_OPERATOR), ("\"it works!\"", TOKEN_STRING), (")", TOKEN_OPERATOR),
     (";", TOKEN_OPERATOR)],

    [("let", TOKEN_KEYWORD), (" x = ", TOKEN_OPERATOR),
     ("Math", TOKEN_DEFAULT), (".", TOKEN_OPERATOR), ("random", TOKEN_DEFAULT),
     ("() * ", TOKEN_OPERATOR), ("42", TOKEN_NUMBER), (";", TOKEN_OPERATOR)],

    [("try", TOKEN_KEYWORD), (" { ", TOKEN_OPERATOR), ("deploy", TOKEN_DEFAULT),
     ("();", TOKEN_OPERATOR), (" } ", TOKEN_OPERATOR), ("catch", TOKEN_KEYWORD),
     (" { ", TOKEN_OPERATOR), ("pray", TOKEN_DEFAULT), ("();", TOKEN_OPERATOR),
     (" }", TOKEN_OPERATOR)],

    [("import", TOKEN_KEYWORD), (" { ", TOKEN_OPERATOR), ("useState", TOKEN_DEFAULT),
     (" } ", TOKEN_OPERATOR), ("from", TOKEN_KEYWORD), (" ", TOKEN_DEFAULT),
     ("\"react\"", TOKEN_STRING), (";", TOKEN_OPERATOR)],

    [("const", TOKEN_KEYWORD), (" arr = [", TOKEN_OPERATOR),
     ("1", TOKEN_NUMBER), (", ", TOKEN_OPERATOR), ("2", TOKEN_NUMBER),
     (", ", TOKEN_OPERATOR), ("3", TOKEN_NUMBER), ("].", TOKEN_OPERATOR),
     ("map", TOKEN_DEFAULT), ("(x => x * ", TOKEN_OPERATOR),
     ("2", TOKEN_NUMBER), (")", TOKEN_OPERATOR), (";", TOKEN_OPERATOR)],

    [("class", TOKEN_KEYWORD), (" Developer ", TOKEN_DEFAULT),
     ("extends", TOKEN_KEYWORD), (" Human ", TOKEN_DEFAULT),
     ("{ }", TOKEN_OPERATOR)],

    [("async", TOKEN_KEYWORD), (" ", TOKEN_DEFAULT), ("function", TOKEN_KEYWORD),
     (" fetchData", TOKEN_DEFAULT), ("() {", TOKEN_OPERATOR), (" ", TOKEN_DEFAULT),
     ("await", TOKEN_KEYWORD), (" ", TOKEN_DEFAULT), ("fetch", TOKEN_DEFAULT),
     ("(", TOKEN_OPERATOR), ("\"/api\"", TOKEN_STRING), (")", TOKEN_OPERATOR),
     (";", TOKEN_OPERATOR), (" }", TOKEN_OPERATOR)],

    [("for", TOKEN_KEYWORD), (" (", TOKEN_OPERATOR), ("let", TOKEN_KEYWORD),
     (" i=", TOKEN_OPERATOR), ("0", TOKEN_NUMBER), ("; i<", TOKEN_OPERATOR),
     ("100", TOKEN_NUMBER), ("; i++)", TOKEN_OPERATOR),
     (" { hack(); }", TOKEN_OPERATOR)],

    [("export", TOKEN_KEYWORD), (" ", TOKEN_DEFAULT), ("default", TOKEN_KEYWORD),
     (" ", TOKEN_DEFAULT), ("function", TOKEN_KEYWORD), (" App", TOKEN_DEFAULT),
     ("() {", TOKEN_OPERATOR), (" ", TOKEN_DEFAULT), ("return", TOKEN_KEYWORD),
     (" <", TOKEN_OPERATOR), ("div", TOKEN_DEFAULT), (" />", TOKEN_OPERATOR),
     ("; }", TOKEN_OPERATOR)],

    [("// ", TOKEN_COMMENT), ("HACK: this shouldn't work", TOKEN_COMMENT),
     (" but it does", TOKEN_COMMENT)],

    [("const", TOKEN_KEYWORD), (" PI = ", TOKEN_OPERATOR),
     ("3.14159", TOKEN_NUMBER), (";", TOKEN_OPERATOR),
     (" // ", TOKEN_COMMENT), ("close enough", TOKEN_COMMENT)],

    [("if", TOKEN_KEYWORD), (" (!", TOKEN_OPERATOR), ("bug", TOKEN_DEFAULT),
     (")", TOKEN_OPERATOR), (" { ", TOKEN_OPERATOR), ("return", TOKEN_KEYWORD),
     (" ", TOKEN_DEFAULT), ("\"feature\"", TOKEN_STRING),
     ("; }", TOKEN_OPERATOR)],

    [("switch", TOKEN_KEYWORD), (" (mood) { ", TOKEN_OPERATOR),
     ("case", TOKEN_KEYWORD), (" ", TOKEN_DEFAULT), ("\"tired\"", TOKEN_STRING),
     (": ", TOKEN_OPERATOR), ("break", TOKEN_KEYWORD), ("; }", TOKEN_OPERATOR)],

    [("npm", TOKEN_DEFAULT), (" install ", TOKEN_OPERATOR),
     ("left-pad", TOKEN_DEFAULT), (" --save", TOKEN_OPERATOR),
     (" // ", TOKEN_COMMENT), ("critical dep", TOKEN_COMMENT)],

    [("git", TOKEN_DEFAULT), (" push --force origin main", TOKEN_OPERATOR),
     (" // ", TOKEN_COMMENT), ("YOLO", TOKEN_COMMENT)],

    [("rm", TOKEN_DEFAULT), (" -rf node_modules && ", TOKEN_OPERATOR),
     ("npm", TOKEN_DEFAULT), (" install", TOKEN_OPERATOR),
     (" // ", TOKEN_COMMENT), ("fixes everything", TOKEN_COMMENT)],

    [("const", TOKEN_KEYWORD), (" sleep = ", TOKEN_OPERATOR),
     ("ms", TOKEN_DEFAULT), (" => ", TOKEN_OPERATOR), ("new", TOKEN_KEYWORD),
     (" Promise", TOKEN_DEFAULT), ("(r => ", TOKEN_OPERATOR),
     ("setTimeout", TOKEN_DEFAULT), ("(r, ms))", TOKEN_OPERATOR),
     (";", TOKEN_OPERATOR)],

    [("throw", TOKEN_KEYWORD), (" ", TOKEN_DEFAULT), ("new", TOKEN_KEYWORD),
     (" Error", TOKEN_DEFAULT), ("(", TOKEN_OPERATOR),
     ("\"not my fault\"", TOKEN_STRING), (")", TOKEN_OPERATOR),
     (";", TOKEN_OPERATOR)],

    [("document", TOKEN_DEFAULT), (".", TOKEN_OPERATOR),
     ("getElementById", TOKEN_DEFAULT), ("(", TOKEN_OPERATOR),
     ("\"app\"", TOKEN_STRING), (").", TOKEN_OPERATOR),
     ("innerHTML", TOKEN_DEFAULT), (" = ", TOKEN_OPERATOR),
     ("\"<h1>Hi</h1>\"", TOKEN_STRING), (";", TOKEN_OPERATOR)],

    [("Object", TOKEN_DEFAULT), (".", TOKEN_OPERATOR),
     ("keys", TOKEN_DEFAULT), ("(", TOKEN_OPERATOR),
     ("reality", TOKEN_DEFAULT), (").", TOKEN_OPERATOR),
     ("forEach", TOKEN_DEFAULT), ("(", TOKEN_OPERATOR),
     ("k => ", TOKEN_OPERATOR), ("delete", TOKEN_KEYWORD),
     (" reality[k]", TOKEN_DEFAULT), (")", TOKEN_OPERATOR),
     (";", TOKEN_OPERATOR)],

    [("return", TOKEN_KEYWORD), (" ", TOKEN_DEFAULT),
     ("JSON", TOKEN_DEFAULT), (".", TOKEN_OPERATOR),
     ("parse", TOKEN_DEFAULT), ("(", TOKEN_OPERATOR),
     ("JSON", TOKEN_DEFAULT), (".", TOKEN_OPERATOR),
     ("stringify", TOKEN_DEFAULT), ("(data))", TOKEN_OPERATOR),
     (";", TOKEN_OPERATOR), (" // ", TOKEN_COMMENT), ("deep clone", TOKEN_COMMENT)],

    [("var", TOKEN_KEYWORD), (" x = x || ", TOKEN_OPERATOR),
     ("42", TOKEN_NUMBER), (";", TOKEN_OPERATOR),
     (" // ", TOKEN_COMMENT), ("defaults are hard", TOKEN_COMMENT)],

    [("fetch", TOKEN_DEFAULT), ("(", TOKEN_OPERATOR),
     ("\"https://api.vibe/data\"", TOKEN_STRING), (")", TOKEN_OPERATOR),
     (".", TOKEN_OPERATOR), ("then", TOKEN_DEFAULT),
     ("(r => r.", TOKEN_OPERATOR), ("json", TOKEN_DEFAULT),
     ("())", TOKEN_OPERATOR), (";", TOKEN_OPERATOR)],

    [("setInterval", TOKEN_DEFAULT), ("(() => ", TOKEN_OPERATOR),
     ("console", TOKEN_DEFAULT), (".", TOKEN_OPERATOR),
     ("log", TOKEN_DEFAULT), ("(", TOKEN_OPERATOR),
     ("\"alive\"", TOKEN_STRING), ("), ", TOKEN_OPERATOR),
     ("1000", TOKEN_NUMBER), (")", TOKEN_OPERATOR), (";", TOKEN_OPERATOR)],

    [("// ", TOKEN_COMMENT), ("Dear future me: I'm sorry", TOKEN_COMMENT)],
]


class CodeGenerator:
    def __init__(self):
        self.current_template = None
        self.current_tokens = []  # flattened list of (char, token_type)
        self.char_index = 0
        self._pick_template()

    def _pick_template(self):
        self.current_template = random.choice(TEMPLATES)
        self.current_tokens = []
        for text, token_type in self.current_template:
            for ch in text:
                self.current_tokens.append((ch, token_type))
        self.char_index = 0

    def get_next_char(self):
        """Return the next expected character and its token type."""
        if self.char_index >= len(self.current_tokens):
            return None, None
        return self.current_tokens[self.char_index]

    def advance(self, count=1):
        """Advance by count characters. Returns (list of (char, token_type), lines_completed)."""
        result = []
        lines_completed = 0
        for _ in range(count):
            if self.char_index >= len(self.current_tokens):
                # Line complete, start new template
                lines_completed += 1
                self._pick_template()
            result.append(self.current_tokens[self.char_index])
            self.char_index += 1
        # Check if we just finished the current template
        if self.char_index >= len(self.current_tokens):
            lines_completed += 1
            self._pick_template()
        return result, lines_completed

    def get_remaining_chars(self):
        """Get all remaining chars in current template for display."""
        return self.current_tokens[self.char_index:]

    def get_full_line_text(self):
        """Get the full text of the current template."""
        return "".join(ch for ch, _ in self.current_tokens)

    def get_progress(self):
        """Return (current_pos, total_len) for current template."""
        return self.char_index, len(self.current_tokens)
