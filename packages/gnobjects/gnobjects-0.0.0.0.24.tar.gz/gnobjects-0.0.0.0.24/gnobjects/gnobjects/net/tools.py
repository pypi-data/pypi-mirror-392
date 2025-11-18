




class DomainMatcher:
    __slots__ = ("_cache",)

    LIT  = 0
    ONE  = 1    # *
    TAIL = 2    # **

    def __init__(self):
        self._cache = {}

    def compile(self, pattern: str):
        cached = self._cache.get(pattern)
        if cached is not None:
            return cached

        out = []
        i = 0
        n = len(pattern)

        while i < n:
            c = pattern[i]
            if c == "*":
                if i + 1 < n and pattern[i + 1] == "*":
                    out.append((self.TAIL, None))
                    self._cache[pattern] = out
                    return out
                else:
                    out.append((self.ONE, None))
                i += 1
            else:
                out.append((self.LIT, c))
                i += 1

        self._cache[pattern] = out
        return out

    def match_compiled(self, tokens, s: str) -> bool:
        i = 0
        n = len(s)
        m = len(tokens)

        tail = (m > 0 and tokens[-1][0] == self.TAIL)
        last = m - 1 if not tail else m - 1

        for t in tokens[:last]:
            ttype, val = t
            if ttype == self.LIT:
                if i >= n or s[i] != val:
                    return False
                i += 1

            elif ttype == self.ONE:
                if i >= n:
                    return False
                c = s[i]
                if c == '.' or c == '~':
                    return False
                i += 1

        if tail:
            return True

        if last < 0:
            return i == n

        ttype, val = tokens[last]
        if ttype == self.LIT:
            if i >= n or s[i] != val:
                return False
            i += 1
            return i == n

        elif ttype == self.ONE:
            if i >= n:
                return False
            c = s[i]
            if c == '.' or c == '~':
                return False
            i += 1
            return i == n

        return False


    def match(self, pattern: str, domain: str) -> bool:
        return self.match_compiled(self.compile(pattern), domain)


class DomainMatcherList:
    __slots__ = ("dm", "literal", "fixed_len", "tail_list")

    def __init__(self, patterns: list[str]):
        self.dm = DomainMatcher()

        self.literal = set()            # точные строки
        self.fixed_len = {}             # длина -> [compiled_tokens]
        self.tail_list = []             # patterns содержащие **

        for p in patterns:
            if "*" not in p:
                self.literal.add(p)
                continue

            tokens = self.dm.compile(p)

            if tokens and tokens[-1][0] == self.dm.TAIL:
                self.tail_list.append(tokens)
                continue

            length = len(p.replace("*", ""))  # минимум длины
            fixed = self.fixed_len.setdefault(length, [])
            fixed.append(tokens)

    def match_any(self, domain: str) -> bool:
        # 1. точное совпадение
        if domain in self.literal:
            return True

        L = len(domain)

        # 2. проверка фиксированных по длине (кроме tail)
        for need_len, token_list in self.fixed_len.items():
            if L < need_len:
                continue
            for tokens in token_list:
                if self.dm.match_compiled(tokens, domain):
                    return True

        # 3. проверка tail-паттернов (**)
        for tokens in self.tail_list:
            if self.dm.match_compiled(tokens, domain):
                return True

        return False


if __name__ == "__main__":
    dm = DomainMatcher()

    print(dm.match("*.a.com", "x.a.com"))             # True
    print(dm.match("ab**", "abzzz.zz"))               # True
    print(dm.match("a*b*c", "aXbYc"))                 # True
    print(dm.match("ab*", "ab."))                     # False
