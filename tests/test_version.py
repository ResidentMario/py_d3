# -*- coding: utf-8 -*-

import sys
import io
from re import match
from contextlib import redirect_stdout

from py_d3 import D3Magics
d3magics = D3Magics()

f = io.StringIO()  # Buffer to save stdout

def assert_consistence(res):
    assert match(r"\d+\.\d+\.*\d*", res) or match(r"\d", res)

def assert_stdout(res, f):
    assert res == None

    out = f.getvalue()
    assert_consistence(out)

    # Clear buffer
    f.truncate(0)
    if sys.version_info >= (3,0):
        f.seek(0)

def test_version_command():
    with redirect_stdout(f):
        res = d3magics.d3(line="version")
    assert_stdout(res, f)

def test_version_property_before_init_src_attr():
    if d3magics.src:
        d3magics.src = None

    res = d3magics.version
    assert_consistence(res)

def test_version_property_after_init_src_attr():
    if not d3magics.src:
        d3magics.src = "d3.v5.min.js"

    res = d3magics.version
    assert_consistence(res)

def test_unknown_local_version():
    d3magics.src = "im_a_crazy_user.js"
    res = d3magics.version
    assert res == "unknown"
