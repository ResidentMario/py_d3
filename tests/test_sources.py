# -*- coding: utf-8 -*-

import os

import pytest

from py_d3 import D3Magics

cell_content = "<g></g>"
kwargs = dict(cell=cell_content)
local_fake_d3_library_path = os.path.join(os.path.dirname(__file__),
	                                      "fake_d3_library_v500.min.js")

def asserted_instance_init():
    d3magics = D3Magics()
    assert d3magics.src == None
    return d3magics

def test_explicit_init_source():
    d3magics = asserted_instance_init()
    version = "4.11.0"

    d3magics.d3(line=version, **kwargs)
    assert d3magics.version == version
    assert d3magics.src == d3magics._cdnjs_d3_source_template % d3magics.version

def test_implicit_init_source():
    d3magics = asserted_instance_init()

    d3magics.d3(**kwargs)
    assert d3magics.version == d3magics.last_release
    assert d3magics.src == d3magics._cdnjs_d3_source_template % d3magics.version

def test_invalid_init_source():
    d3magics = asserted_instance_init()

    source = "im_a_crazy_javascript_user.js"
    with pytest.raises(ValueError) as excinfo:
        d3magics.d3(line=source, **kwargs)
    assert "%s is not a valid cdnjs release" % source in str(excinfo)
