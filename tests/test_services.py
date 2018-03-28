# -*- coding: utf-8 -*-

from urllib.request import urlopen

from py_d3 import D3Magics
d3magics = D3Magics()


def service_up(url):
    req = urlopen(url)
    return req.getcode() == 200


def test_cdnjs_api():
    assert service_up(d3magics._cdnjs_api_url)


# TODO: implement and test Blockbuilder API layer.
# def test_blockbuilder_api():
#     assert service_up(d3magics._blockbuilder_api_url)
