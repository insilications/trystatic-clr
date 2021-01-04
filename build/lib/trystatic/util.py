#!/bin/true

import hashlib
import os
import re
import shlex
import subprocess
import sys
import typing
from typing import Any, TextIO, TypedDict, Dict, List, Tuple, Optional, IO
from io import TextIOWrapper

os_paths: Optional[List[str]]
os_paths = None


def call(command: str, logfile: Any = None, check=True, **kwargs: Dict[str, Any]) -> int:
    """Subprocess.call convenience wrapper."""
    returncode: int = 1
    full_args: Dict[str, Any]

    full_args = {
        "args": shlex.split(command),
        "universal_newlines": True,
    }

    #toy_story = Movie(name='Toy Story', year=1995)
    full_args.update(kwargs)

    if logfile:
        # full_args["stdout"]: TextIO
        full_args["stdout"] = open(logfile, "w")
        full_args["stderr"] = subprocess.STDOUT
        returncode = subprocess.call(**full_args)
        # full_args["stdout"].close()
    else:
        returncode = subprocess.call(**full_args)

    if check and returncode != 0:
        raise subprocess.CalledProcessError(returncode, full_args["args"], None)

    return returncode


def _file_write(self, s):
    s = s.strip()
    if not s.endswith("\n"):
        s += "\n"
    self.write(s)


def do_regex(patterns, re_str):
    """Find a match in multiple patterns."""
    for p in patterns:
        match = re.search(p, re_str)
        if match:
            return match


def get_contents(filename):
    """Get contents of filename."""
    with open(filename, "rb") as f:
        return f.read()
    return None


def get_sha1sum(filename):
    """Get sha1 sum of filename."""
    sh = hashlib.sha1()
    sh.update(get_contents(filename))
    return sh.hexdigest()


def _supports_color():
    # FIXME: check terminfo instead
    return sys.stdout.isatty()


def _print_message(message, level, color=None):
    prefix = level
    params = ""
    if color and _supports_color():
        # FIXME: use terminfo instead
        if color == 'red':
            params = '31;1'
        elif color == 'green':
            params = '32;1'
        elif color == 'yellow':
            params = '33;1'
        elif color == 'blue':
            params = '34;1'
        prefix = f'\033[{params}m{level}\033[0m'
    print(f'[{prefix}] {message}')


def print_error(message):
    """Print error, color coded for TTYs."""
    _print_message(message, 'ERROR', 'red')


def print_fatal(message):
    """Print fatal error, color coded for TTYs."""
    _print_message(message, 'FATAL', 'red')


def print_warning(message):
    """Print warning, color coded for TTYs."""
    _print_message(message, 'WARNING', 'red')


def print_info(message):
    """Print informational message, color coded for TTYs."""
    _print_message(message, 'INFO', 'yellow')


def print_success(message):
    """Print success message, color coded for TTYs."""
    _print_message(message, 'SUCCESS', 'green')


def binary_in_path(binary):
    """Determine if the given binary exists in the provided filesystem paths."""
    global os_paths
    if not os_paths:
        os_paths = os.getenv("PATH", default="/usr/bin:/bin").split(os.pathsep)

    for path in os_paths:
        if os.path.exists(os.path.join(path, binary)):
            return True
    return False


def write_out(filename: str, content: Any, mode: str = "w", buffering: int = -1) -> None:
    """File.write convenience wrapper."""
    with open_auto(filename, mode, buffering) as require_f:
        require_f.write(content)


def open_auto(filename: str, mode: str = "w", buffering: int = -1, **kwargs: Any) -> IO:
    """Open a file with UTF-8 encoding.

    Open file with UTF-8 encoding and "surrogate" escape characters that are
    not valid UTF-8 to avoid data corruption.
    """
    # 'encoding' and 'errors' are fourth and fifth positional arguments, so
    # restrict the args tuple to (file, mode, buffering) at most
    encoding: str
    errors: str
    assert 'encoding' not in kwargs
    assert 'errors' not in kwargs
    return open(file = filename, mode = mode, buffering = buffering, encoding="utf-8", errors="surrogateescape", **kwargs)
