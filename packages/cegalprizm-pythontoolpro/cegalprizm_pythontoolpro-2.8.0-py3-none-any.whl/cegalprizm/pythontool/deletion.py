# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



from functools import wraps
from cegalprizm.pythontool.exceptions import PythonToolException

allow_deletion = False

def set_deletion_ok(b):
    global allow_deletion
    allow_deletion = b

def deletion_method(func):
    @wraps(func)
    def wrapped_func(*args, **kwargs):
        global allow_deletion
        if not allow_deletion:
            raise PythonToolException("Object deletion is not allowed")
        return func(*args, **kwargs)
    return wrapped_func
