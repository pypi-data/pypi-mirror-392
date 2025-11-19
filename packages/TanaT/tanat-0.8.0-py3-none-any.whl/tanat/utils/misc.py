#!/usr/bin/env python3
"""
Miscellaneous utility functions.
"""

import re


def chunks_from_generator(generator, chunk_size):
    """Create chunks from a generator without loading everything into memory."""
    iterator = iter(generator)
    while True:
        chunk = []
        try:
            for _ in range(chunk_size):
                chunk.append(next(iterator))
            yield tuple(chunk)
        except StopIteration:
            if chunk:
                yield tuple(chunk)
            break


def string_to_dict(s):
    """
    Convert a string of key=value pairs into a dictionary.

    Handles values enclosed in single or double quotes.

    Example:
        input: 'key1=value1, key2="value with spaces", key3=\'value3\''
        output: {'key1': 'value1', 'key2': 'value with spaces', 'key3': 'value3'}
    """
    result = {}
    pattern = r"(\w+)=([\"']?)(.+?)\2(?:,\s*|$)"

    for match in re.finditer(pattern, s):
        key = match.group(1)
        value = match.group(3)
        result[key] = value

    return result
