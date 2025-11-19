# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



class PythonToolException(Exception):
    def __init__(self, message):
        super(PythonToolException, self).__init__(message)


class UserErrorException(Exception):
    def __init__(self, message, stack_trace=None):
        super(UserErrorException, self).__init__(message)
        self.petrel_stack_trace = stack_trace


class UnexpectedErrorException(Exception):
    def __init__(self, message, stack_trace=None):
        super(UnexpectedErrorException, self).__init__(message)
        self.petrel_stack_trace = stack_trace
