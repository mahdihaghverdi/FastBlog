import hashlib
from datetime import datetime


def generate_hash():
    return hashlib.shake_256(str(datetime.utcnow()).encode("utf-8")).hexdigest(4)
