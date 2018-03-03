# -*- coding: utf-8 -*-

import sys
import io
from contextlib import redirect_stdout

from py_d3 import D3Magics
d3magics = D3Magics()

f = io.StringIO()  # Buffer to save stdout

def assert_consistence(res):
    some_known_releases = [
        '4.13.0', '4.12.2', '4.12.1', '4.12.0', '4.11.0',
        '4.10.2', '4.10.1', '4.10.0', '4.9.1', '4.9.0'
    ]

    # Is retrieving all known releases?
    for rel in some_known_releases:
        assert rel in res

def assert_stdout(res, f):
    assert res == None

    out = f.getvalue().splitlines() # Stdout value
    assert_consistence(out)

    # Clear buffer
    f.truncate(0)
    if sys.version_info >= (3,0):
        f.seek(0)

def test_show_online_releases_implicit_command():
    with redirect_stdout(f):
        res = d3magics.d3()
    assert_stdout(res, f)

def test_show_online_releases_explicit_command():
    with redirect_stdout(f):
        res = d3magics.d3(line="releases")
    assert_stdout(res, f)

def test_online_releases_property():
    res = d3magics.online_releases
    assert_consistence(res)

def test_show_online_releases_method():
    with redirect_stdout(f):
        res = d3magics.show_online_releases()
    assert_stdout(res, f)
