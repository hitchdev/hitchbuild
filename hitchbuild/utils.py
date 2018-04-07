import hashlib
import json


def hash_json_struct(struct):
    return hashlib.md5(
        json.dumps(
            struct,
            sort_keys=True,
            separators=(",", ";"),
        ).encode('utf8')
    ).hexdigest()
