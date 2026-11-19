"""Wrappers util for holding various function wrappers."""

import os
from contextlib import contextmanager, redirect_stdout


@contextmanager
def suppress():
    with open(os.devnull, "w") as null, redirect_stdout(null):
        yield
