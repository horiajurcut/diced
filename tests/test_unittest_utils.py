import unittest
import pytest

from api.utils import encode
from api.utils import decode


class UtilsTest(unittest.TestCase):
    def test_base62_encode_zero(self):
        n = 0
        encoded_digit = encode(n)

        assert "0" == encoded_digit

    def test_base62_encode_digit(self):
        n = 4
        encoded_digit = encode(n)

        assert str(n) == encoded_digit

    def test_base62_encode_small_number(self):
        n = 10
        encoded_n = encode(n)

        assert "a" == encoded_n

    def test_base62_encode_large_number(self):
        n = 3213213
        encoded_n = encode(n)

        assert "dtU1" == encoded_n

    def test_base62_decode_zero(self):
        decoded_digit = decode("0")

        assert 0 == decoded_digit

    def test_base62_decode_digit(self):
        decoded_digit = decode("4")

        assert 4 == decoded_digit

    def test_base62_decode_a(self):
        dencoded_n = decode("a")

        assert 10 == dencoded_n

    def test_base62_decode_large_number(self):
        decoded_n = decode("dtU1")

        assert 3213213 == decoded_n
