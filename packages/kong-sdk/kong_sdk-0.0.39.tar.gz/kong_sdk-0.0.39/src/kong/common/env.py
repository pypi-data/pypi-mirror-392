import os


def env_flag(name, default=False):
    value = os.getenv(name)
    if value is None:
        return default

    return value.lower() in ("true", "1", "t", "y", "yes")
