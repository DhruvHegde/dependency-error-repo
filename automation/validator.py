DEPENDENCY_PATTERNS = [
    "No matching distribution found",
    "Could not find a version that satisfies the requirement",
    "ERROR: Could not find",
    "ResolutionImpossible",
    "Invalid requirement",
    "Ignored the following versions"
]


def validate_dependency_log(log_text):

    for pattern in DEPENDENCY_PATTERNS:

        if pattern.lower() in log_text.lower():

            return True, pattern

    return False, None