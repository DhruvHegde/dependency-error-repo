import json
import os


def save_metadata(path, metadata):

    os.makedirs(os.path.dirname(path), exist_ok=True)

    with open(path, "w") as f:

        json.dump(
            metadata,
            f,
            indent=4
        )