from contextlib import redirect_stdout, contextmanager
import os


@contextmanager
def suppress():
    with open(os.devnull, "w") as null:
        with redirect_stdout(null):
            yield
