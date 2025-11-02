def string_to_md5(text):
    import hashlib
    return hashlib.md5('text').hexdigest() if text else None


def string_to_md5(text):
    import hashlib
    x1 = hashlib.md5('text')
    x2 = x1.hexdigest()
    x3 = x2 if text else None
    return x3