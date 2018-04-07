import hashlib


def hashstring(string):
    return hashlib.md5(string.encode('utf8')).hexdigest()
