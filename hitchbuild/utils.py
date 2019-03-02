import hashlib
import json


def hash_json_struct(struct):
    """
    Deterministic hash of combinations of dict, list,
    float, int and bool.
    """
    return hashlib.md5(
        json.dumps(
            struct,
            sort_keys=True,
            separators=(",", ";"),
        ).encode('utf8')
    ).hexdigest()
