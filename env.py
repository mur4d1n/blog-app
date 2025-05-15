from typing import Callable

from pathlib import Path


def parse_env_file(filename: str) -> dict:
    params = dict()

    path = Path(__file__).absolute().parent / filename

    with open(path, 'r') as file:
        param_str = file.readline().strip()

        while param_str:
            key, value = param_str.split('=', 1)

            value_type = get_value_type(value)

            params[key] = value_type(value)

            param_str = file.readline().strip()

    return params


def get_value_type(value: str) -> Callable:
    """
    Returns a callable value type to convert str value to an actual value.
    Currently, don't support floats, lists, and dicts

    :param value:
    :return:
    """

    if value.isdigit():
        return int
    elif value in ('True', 'False'):
        return as_bool
    else:
        return str


def as_bool(value: str) -> bool:
    if value == 'True':
        return True
    elif value == 'False':
        return False
    else:
        raise ValueError('Value is not a boolean convertible')
