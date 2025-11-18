

def capitalize(s):
    if not s:
        return s
    
    result = []
    for i, char in enumerate(s):
        if i == 0:
            code = ord(char)
            if 97 <= code <= 122:
                result.append(chr(code - 32))
            else:
                result.append(char)
        else:
            code = ord(char)
            if 65 <= code <= 90:
                result.append(chr(code + 32))
            else:
                result.append(char)
    
    return ''.join(result)


def casefold(s):
    result = []
    for char in s:
        code = ord(char)
        if 65 <= code <= 90:
            result.append(chr(code + 32))
        elif 192 <= code <= 223:
            result.append(chr(code + 32))
        else:
            result.append(char)
    
    return ''.join(result)


def count(s, sub, start=0, end=None):
    if not sub:
        return len(s) + 1 if s else 0
    
    if end is None:
        end = len(s)
    
    if start < 0:
        start = 0
    if end > len(s):
        end = len(s)
    
    count_val = 0
    sub_len = len(sub)
    i = start
    
    while i <= end - sub_len:
        match = True
        for j in range(sub_len):
            if s[i + j] != sub[j]:
                match = False
                break
        
        if match:
            count_val += 1
            i += sub_len
        else:
            i += 1
    
    return count_val


def endswith(s, suffix, start=0, end=None):
    if end is None:
        end = len(s)
    
    if start < 0:
        start = 0
    if end > len(s):
        end = len(s)
    
    suffix_len = len(suffix)
    if suffix_len > (end - start):
        return False
    
    start_pos = end - suffix_len
    
    for i in range(suffix_len):
        if s[start_pos + i] != suffix[i]:
            return False
    
    return True


def find(s, sub, start=0, end=None):
    if not sub:
        return start if 0 <= start <= len(s) else -1
    
    if end is None:
        end = len(s)
    
    if start < 0:
        start = 0
    if end > len(s):
        end = len(s)
    
    sub_len = len(sub)
    max_start = end - sub_len
    
    for i in range(start, max_start + 1):
        match = True
        for j in range(sub_len):
            if s[i + j] != sub[j]:
                match = False
                break
        
        if match:
            return i
    
    return -1


def index(s, sub, start=0, end=None):
    result = find(s, sub, start, end)
    if result == -1:
        raise ValueError(f"substring not found")
    return result


def isdigit(s):
    if not s:
        return False
    
    for char in s:
        code = ord(char)
        if not (48 <= code <= 57):
            return False
    
    return True


def islower(s):
    has_cased = False
    
    for char in s:
        code = ord(char)
        if 65 <= code <= 90:
            return False
        elif 97 <= code <= 122:
            has_cased = True
    
    return has_cased


def isupper(s):
    has_cased = False
    
    for char in s:
        code = ord(char)
        if 97 <= code <= 122:
            return False
        elif 65 <= code <= 90:
            has_cased = True
    
    return has_cased


def _is_whitespace(char):
    code = ord(char)
    return code in (9, 10, 11, 12, 13, 32)


def strip(s, chars=None):
    if not s:
        return s
    
    if chars is None:
        start = 0
        end = len(s)
        
        while start < end and _is_whitespace(s[start]):
            start += 1
        
        while end > start and _is_whitespace(s[end - 1]):
            end -= 1
        
        return s[start:end]
    else:
        start = 0
        end = len(s)
        
        while start < end:
            found = False
            for c in chars:
                if s[start] == c:
                    found = True
                    break
            if not found:
                break
            start += 1
        
        while end > start:
            found = False
            for c in chars:
                if s[end - 1] == c:
                    found = True
                    break
            if not found:
                break
            end -= 1
        
        return s[start:end]


def lstrip(s, chars=None):
    if not s:
        return s
    
    if chars is None:
        start = 0
        while start < len(s) and _is_whitespace(s[start]):
            start += 1
        return s[start:]
    else:
        start = 0
        while start < len(s):
            found = False
            for c in chars:
                if s[start] == c:
                    found = True
                    break
            if not found:
                break
            start += 1
        return s[start:]


def rstrip(s, chars=None):
    if not s:
        return s
    
    if chars is None:
        end = len(s)
        while end > 0 and _is_whitespace(s[end - 1]):
            end -= 1
        return s[:end]
    else:
        end = len(s)
        while end > 0:
            found = False
            for c in chars:
                if s[end - 1] == c:
                    found = True
                    break
            if not found:
                break
            end -= 1
        return s[:end]


def replace(s, old, new, count=-1):
    if not old:
        return s
    
    if count == 0:
        return s
    
    result = []
    i = 0
    old_len = len(old)
    replacements = 0
    
    while i < len(s):
        if (count == -1 or replacements < count) and i + old_len <= len(s):
            match = True
            for j in range(old_len):
                if s[i + j] != old[j]:
                    match = False
                    break
            
            if match:
                result.append(new)
                i += old_len
                replacements += 1
                continue
        
        result.append(s[i])
        i += 1
    
    return ''.join(result)


def split(s, sep=None, maxsplit=-1):
    if sep is None:
        result = []
        current = []
        i = 0
        splits = 0
        
        while i < len(s):
            if _is_whitespace(s[i]):
                if current:
                    result.append(''.join(current))
                    current = []
                    splits += 1
                    if maxsplit != -1 and splits >= maxsplit:
                        remaining = []
                        i += 1
                        while i < len(s) and _is_whitespace(s[i]):
                            i += 1
                        while i < len(s):
                            remaining.append(s[i])
                            i += 1
                        if remaining:
                            result.append(''.join(remaining))
                        return result
            else:
                current.append(s[i])
            i += 1
        
        if current:
            result.append(''.join(current))
        
        return result
    else:
        if not sep:
            raise ValueError("empty separator")
        
        if maxsplit == 0:
            return [s]
        
        result = []
        current = []
        i = 0
        sep_len = len(sep)
        splits = 0
        
        while i < len(s):
            if (maxsplit == -1 or splits < maxsplit) and i + sep_len <= len(s):
                match = True
                for j in range(sep_len):
                    if s[i + j] != sep[j]:
                        match = False
                        break
                
                if match:
                    result.append(''.join(current))
                    current = []
                    i += sep_len
                    splits += 1
                    continue
            
            current.append(s[i])
            i += 1
        
        result.append(''.join(current))
        return result


def rsplit(s, sep=None, maxsplit=-1):
    if sep is None:
        result = []
        current = []
        i = len(s) - 1
        splits = 0
        
        while i >= 0:
            if maxsplit != -1 and splits >= maxsplit:
                remaining = []
                while i >= 0:
                    remaining.insert(0, s[i])
                    i -= 1
                if remaining:
                    result.insert(0, ''.join(remaining))
                return result
            
            if _is_whitespace(s[i]):
                if current:
                    result.insert(0, ''.join(reversed(current)))
                    current = []
                    splits += 1
            else:
                current.append(s[i])
            i -= 1
        
        if current:
            result.insert(0, ''.join(reversed(current)))
        
        return result
    else:
        if not sep:
            raise ValueError("empty separator")
        
        if maxsplit == 0:
            return [s]
        
        result = []
        current = []
        i = len(s) - 1
        sep_len = len(sep)
        splits = 0
        
        while i >= 0:
            if (maxsplit == -1 or splits < maxsplit) and i - sep_len + 1 >= 0:
                match = True
                for j in range(sep_len):
                    if s[i - sep_len + 1 + j] != sep[j]:
                        match = False
                        break
                
                if match:
                    result.insert(0, ''.join(reversed(current)))
                    current = []
                    i -= sep_len
                    splits += 1
                    continue
            
            current.append(s[i])
            i -= 1
        
        result.insert(0, ''.join(reversed(current)))
        return result


def swapcase(s):
    result = []
    for char in s:
        code = ord(char)
        if 65 <= code <= 90:
            result.append(chr(code + 32))
        elif 97 <= code <= 122:
            result.append(chr(code - 32))
        else:
            result.append(char)
    
    return ''.join(result)
