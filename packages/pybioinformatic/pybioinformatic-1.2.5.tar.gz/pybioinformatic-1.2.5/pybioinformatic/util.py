"""
File: util.py
Description: Util module.
CreateDate: 2024/5/12
Author: xuwenlin
E-mail: wenlinxu.njfu@outlook.com
"""
from io import TextIOWrapper
from typing import Callable
from natsort import natsort_key
from yaml import safe_load
from schema import Schema, SchemaError
from click import echo


def check_config(module_dict:dict, yaml_file: TextIOWrapper):
    echo('\033[36mCheck params.\033[0m', err=True)
    config_schema = Schema(module_dict)

    config = safe_load(yaml_file)
    try:
        config_schema.validate(config)
        echo("\033[32mConfiguration verification passed.\n\033[0m", err=True)
    except SchemaError as e:
        echo(f"\033[31mConfig error: {e}\033[0m", err=True)
        exit()
    else:
        return config


class FuncDict(dict):
    def sort_by_keys(self, key: Callable = natsort_key,  reverse: bool = False):
        sorted_dict = FuncDict({key: self[key] for key in sorted(self, key=key, reverse=reverse)})
        self.clear()
        self.update(sorted_dict)

    def __getitem__(self, key):
        """Returns the same value as the key when a non-existent key is accessed."""
        try:
            return super().__getitem__(key)
        except KeyError:
            return key

    def __add__(self, other):
        for k, v in other.items():
            if k in self:
                self[k] += v
            else:
                self[k] = v
