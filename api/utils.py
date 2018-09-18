BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


def encode(n, alphabet=BASE62):
    """Encode a positive number"""
    if n == 0:
        return alphabet[0]

    hash_arr = []
    base = len(alphabet)

    while n:
        # divmod returns the tuple (n // base, n % base)
        n, reminder = divmod(n, base)
        hash_arr.append(alphabet[reminder])
    hash_arr.reverse()

    return ''.join(hash_arr)


def decode(string, alphabet=BASE62):
    """Decode an encoded string into a positive number"""
    base = len(alphabet)
    str_length = len(string)

    n = 0
    i = 0

    for c in string:
        power = (str_length - (i + 1))
        n += alphabet.index(c) * (base ** power)
        i += 1

    return n
