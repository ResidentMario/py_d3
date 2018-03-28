# -*- coding: utf-8 -*-

import sys
import io
from contextlib import redirect_stdout

from py_d3 import D3Magics
d3magics = D3Magics()

all_modules = d3magics.modules

f = io.StringIO()  # Buffer to save stdout


def test_modules_list():
    assert isinstance(all_modules, list)
    assert len(all_modules) > 0


def assert_stdout(f):
    _mods = eval(
        ",".join(f.getvalue().splitlines()).replace(",,", ",")
    )

    for mod in _mods:
        assert mod in all_modules

    # Clear buffer
    f.truncate(0)
    if sys.version_info >= (3,0):
        f.seek(0)

def test_modules_command():
    with redirect_stdout(f):
        d3magics.d3(line="modules")
    assert_stdout(f)
