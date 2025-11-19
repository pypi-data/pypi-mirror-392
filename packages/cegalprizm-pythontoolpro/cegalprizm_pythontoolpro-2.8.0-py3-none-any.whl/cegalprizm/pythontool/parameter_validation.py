# Copyright 2025 Cegal AS
# All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.



import functools
import inspect
from typing import Callable, Any
from cegalprizm.pythontool import _utils

def validate_name(param_name: str = 'name', can_be_empty: bool = True) -> Callable:
    """Decorator to validate the 'name' argument in functions.

    This decorator checks if the 'name' argument is a string, is not empty or whitespace-only,
    and does not contain special whitespace characters such as line breaks or tabs.

    Args:
        param_name (str): The name of the parameter to validate. Defaults to 'name'.
        can_be_empty (bool): Whether the parameter can be empty. Defaults to True.

    Returns:
        Callable: The decorated function with name validation.
    """
    def decorator(func: Callable) -> Callable:
        sig = inspect.signature(func)
        param_names = list(sig.parameters.keys())
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            param_value, is_in_kwargs = _extract_param_value(param_names, param_name, args, kwargs)
            if param_value is None and can_be_empty:
                param_value = ""
            _validate_parameter_value(param_value, param_name, can_be_empty)
            updated_value = param_value.strip() if not param_value.strip() else param_value
            if is_in_kwargs:
                kwargs[param_name] = updated_value
            else:
                param_index = param_names.index(param_name)
                if len(args) > param_index:
                    args_list = list(args)
                    args_list[param_index] = updated_value
                    args = tuple(args_list)
                else:
                    kwargs[param_name] = updated_value
            return func(*args, **kwargs)
        return wrapper
    return decorator

def _extract_param_value(param_names: list, param_name: str, args: tuple, kwargs: dict) -> tuple:
    if param_name in kwargs:
        return kwargs[param_name], True
    if param_name not in param_names:
        raise ValueError(f"Parameter '{param_name}' not found in function signature")
    param_index = param_names.index(param_name)
    if len(args) > param_index:
        return args[param_index], False
    return "", False

def _validate_parameter_value(param_value: Any, param_name: str, can_be_empty: bool) -> None:
    if not isinstance(param_value, str):
        raise TypeError(f"{param_name} must be a string")
    
    if not can_be_empty and not param_value.strip():
        raise ValueError(f"{param_name} cannot be empty")
    
    if _utils.has_special_whitespace(param_value):
        raise ValueError(f"{param_name} cannot contain special whitespaces such as line breaks or tabs")