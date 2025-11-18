import pytest
from strio.core import (
    capitalize,
    casefold,
    count,
    endswith,
    find,
    index,
    isdigit,
    islower,
    isupper,
    strip,
    lstrip,
    rstrip,
    replace,
    split,
    rsplit,
    swapcase,
)


class TestCapitalize:
    
    def test_basic(self):
        assert capitalize("hello") == "Hello"
        assert capitalize("HELLO") == "Hello"
        assert capitalize("hELLO") == "Hello"
    
    def test_empty_string(self):
        assert capitalize("") == ""
    
    def test_single_char(self):
        assert capitalize("a") == "A"
        assert capitalize("A") == "A"
    
    def test_non_alphabetic(self):
        assert capitalize("123abc") == "123abc"
        assert capitalize(" hello") == " hello"


class TestCasefold:
    
    def test_basic(self):
        assert casefold("HELLO") == "hello"
        assert casefold("Hello") == "hello"
        assert casefold("hELLO") == "hello"
    
    def test_empty_string(self):
        assert casefold("") == ""
    
    def test_mixed_case(self):
        assert casefold("HeLLo WoRLd") == "hello world"


class TestCount:
    
    def test_basic(self):
        assert count("hello hello", "hello") == 2
        assert count("ababab", "ab") == 3
    
    def test_no_occurrences(self):
        assert count("hello", "xyz") == 0
    
    def test_empty_substring(self):
        assert count("hello", "") == 6
        assert count("", "") == 1
    
    def test_with_start_end(self):
        assert count("hello hello", "hello", 0, 5) == 1
        assert count("ababab", "ab", 2) == 2


class TestEndswith:
    
    def test_basic(self):
        assert endswith("hello", "lo") is True
        assert endswith("hello", "he") is False
    
    def test_empty_string(self):
        assert endswith("", "") is True
        assert endswith("hello", "") is True
    
    def test_with_start_end(self):
        assert endswith("hello", "lo", 0, 5) is True
        assert endswith("hello", "he", 0, 2) is True


class TestFind:
    
    def test_basic(self):
        assert find("hello", "ll") == 2
        assert find("hello", "lo") == 3
    
    def test_not_found(self):
        assert find("hello", "xyz") == -1
    
    def test_empty_substring(self):
        assert find("hello", "") == 0
    
    def test_with_start_end(self):
        assert find("hello hello", "hello", 1) == 6
        assert find("hello", "ll", 0, 3) == 2


class TestIndex:
    
    def test_basic(self):
        assert index("hello", "ll") == 2
        assert index("hello", "lo") == 3
    
    def test_not_found_raises(self):
        with pytest.raises(ValueError):
            index("hello", "xyz")
    
    def test_empty_substring(self):
        assert index("hello", "") == 0


class TestIsdigit:
    
    def test_basic(self):
        assert isdigit("123") is True
        assert isdigit("0") is True
    
    def test_contains_letters(self):
        assert isdigit("123a") is False
        assert isdigit("abc") is False
    
    def test_empty_string(self):
        assert isdigit("") is False
    
    def test_mixed(self):
        assert isdigit("12.34") is False


class TestIslower:
    
    def test_basic(self):
        assert islower("hello") is True
        assert islower("HELLO") is False
        assert islower("Hello") is False
    
    def test_empty_string(self):
        assert islower("") is False
    
    def test_no_cased_chars(self):
        assert islower("123") is False
        assert islower("!@#") is False
    
    def test_mixed(self):
        assert islower("hello123") is True


class TestIsupper:
    
    def test_basic(self):
        assert isupper("HELLO") is True
        assert isupper("hello") is False
        assert isupper("Hello") is False
    
    def test_empty_string(self):
        assert isupper("") is False
    
    def test_no_cased_chars(self):
        assert isupper("123") is False
    
    def test_mixed(self):
        assert isupper("HELLO123") is True


class TestStrip:
    
    def test_basic(self):
        assert strip("  hello  ") == "hello"
        assert strip("\t\nhello\r\n") == "hello"
    
    def test_no_whitespace(self):
        assert strip("hello") == "hello"
    
    def test_all_whitespace(self):
        assert strip("   ") == ""
    
    def test_empty_string(self):
        assert strip("") == ""
    
    def test_custom_chars(self):
        assert strip("xxxhelloxxx", "x") == "hello"
        assert strip("abc", "a") == "bc"


class TestLstrip:
    
    def test_basic(self):
        assert lstrip("  hello  ") == "hello  "
        assert lstrip("\t\nhello") == "hello"
    
    def test_no_leading_whitespace(self):
        assert lstrip("hello  ") == "hello  "
    
    def test_custom_chars(self):
        assert lstrip("xxxhello", "x") == "hello"


class TestRstrip:
    
    def test_basic(self):
        assert rstrip("  hello  ") == "  hello"
        assert rstrip("hello\n\r") == "hello"
    
    def test_no_trailing_whitespace(self):
        assert rstrip("  hello") == "  hello"
    
    def test_custom_chars(self):
        assert rstrip("helloxxx", "x") == "hello"


class TestReplace:
    
    def test_basic(self):
        assert replace("hello world", "world", "python") == "hello python"
        assert replace("ababab", "ab", "xy") == "xyxyxy"
    
    def test_no_occurrences(self):
        assert replace("hello", "xyz", "abc") == "hello"
    
    def test_empty_old(self):
        assert replace("hello", "", "x") == "hello"
    
    def test_with_count(self):
        assert replace("ababab", "ab", "xy", 2) == "xyxyab"
        assert replace("ababab", "ab", "xy", 0) == "ababab"


class TestSplit:
    
    def test_basic_whitespace(self):
        assert split("hello world") == ["hello", "world"]
        assert split("a b c") == ["a", "b", "c"]
    
    def test_multiple_whitespace(self):
        assert split("a  b   c") == ["a", "b", "c"]
        assert split("  hello  world  ") == ["hello", "world"]
    
    def test_with_separator(self):
        assert split("a,b,c", ",") == ["a", "b", "c"]
        assert split("hello", "l") == ["he", "", "o"]
    
    def test_with_maxsplit(self):
        assert split("a b c d", maxsplit=2) == ["a", "b", "c d"]
        assert split("a,b,c,d", ",", maxsplit=2) == ["a", "b", "c,d"]
    
    def test_empty_string(self):
        assert split("") == [""]
    
    def test_empty_separator_error(self):
        with pytest.raises(ValueError):
            split("hello", "")


class TestRsplit:
    
    def test_basic_whitespace(self):
        assert rsplit("hello world") == ["hello", "world"]
        assert rsplit("a b c") == ["a", "b", "c"]
    
    def test_with_separator(self):
        assert rsplit("a,b,c", ",") == ["a", "b", "c"]
    
    def test_with_maxsplit(self):
        assert rsplit("a b c d", maxsplit=2) == ["a b", "c", "d"]
        assert rsplit("a,b,c,d", ",", maxsplit=2) == ["a,b", "c", "d"]
    
    def test_empty_string(self):
        assert rsplit("") == [""]
    
    def test_empty_separator_error(self):
        with pytest.raises(ValueError):
            rsplit("hello", "")


class TestSwapcase:
    
    def test_basic(self):
        assert swapcase("Hello") == "hELLO"
        assert swapcase("HELLO") == "hello"
        assert swapcase("hello") == "HELLO"
    
    def test_mixed(self):
        assert swapcase("HeLLo WoRLd") == "hEllO wOrlD"
    
    def test_empty_string(self):
        assert swapcase("") == ""
    
    def test_non_alphabetic(self):
        assert swapcase("123!@#") == "123!@#"
