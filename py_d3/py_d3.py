# This code can be put in any Python module, it does not require IPython
# itself to be running already.  It only creates the magics subclass but
# doesn't instantiate it yet.
from __future__ import print_function
import sys
from re import search, sub
from json import loads
try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:  # Python2
    from urllib import urlopen

from IPython.core.magic import (
    Magics,
    magics_class,
    line_cell_magic
)
from IPython.display import HTML, display

# import requests
# import zipfile
# import io

@magics_class
class D3Magics(Magics):

    def __init__(self, **kwargs):
        super(D3Magics, self).__init__(**kwargs)
        self.max_id = 0  # Used to ensure that the current group selection is unique.
        # self.initialized = True  # Used to ensure that d3.js is only imported once.

        self._cdnjs_api_url = "http://api.cdnjs.com/libraries/d3"

    @property
    def last_release(self):
        """Obtain last stable D3 release from cdnjs API.
        If is not possible, return last hardcoded release.
        """
        try:
            return self._last_release
        except AttributeError:
            try:
                res = urlopen(self._cdnjs_api_url).read()
                if sys.version_info >= (3,0):
                    res = res.decode()
                self._last_release = loads(res)["assets"][0]["version"]
                return self._last_release
            except Exception:
                pass
        return "4.13.0"

    def show_all_releases(self):
        """Print all releases hosted at d3 cdnjs page."""
        try:
            res = urlopen(self._cdnjs_api_url).read()
            if sys.version_info >= (3,0):
                res = res.decode()
        except Exception as e:
            pass
        else:
            for asset in loads(res)["assets"]:
                print(asset["version"])

    # # The necessary substitutions to get a block working are theoretically possible, but too quirky for the moment
    # to consider.
    # @line_magic
    # def block(self, line):
    #     user, gist_id = line.split("/")[-2:]
    #     r = requests.get("https://gist.github.com/{0}/{1}/download".format(user, gist_id))
    #     with zipfile.ZipFile(io.BytesIO(r.content)) as ar:
    #         ar.extractall(".blocks/{0}/".format(user, gist_id))
    #         # This creates e.g. ".blocks/mbostock/3885304-master" in the root directory.
    #         # The appended "-master" is due to the format of the zipped file.
    #         # It's a little unideal, but unsure about whether or not removing it would cause any issues I've kept it
    #         # for the time being (you could easily rename the folder).
    #     with open(".blocks/{0}/{1}-master/index.html".format(user, gist_id), "r") as f:
    #         source = f.read()
    #     # We need to perform a few substutions to make the figure work within a Jupyter Notebook file.
    #     # 1. <body> tags are not allowed within a D3 notebook (one has already been defined and HTML documents only
    #     #    allow one <body> and one <head>), but are probably the most common initial selector of all for defining
    #     #    the initial D3 frame. To fix:
    #     #    >>> <body>                 -->     <g>
    #     #    >>> d3.select("body")      -->     d3.select("g")
    #     #    >>> <body id="foo">        -->     ???
    #     #    >>> <body class="foo">     -->     ???
    #     source = source.replace('<body', '<g')
    #     source = source.replace("select('body", "select(g")
    #     source = source.replace('d3.tsv("', 'd3.tsv("./.blocks/{0}/{1}-master/'.format(user, gist_id))
    #     print(HTML(source).data)
    #     display(HTML(source))

    @line_cell_magic
    def d3(self, line="", cell=None):
        """D3 line and cell magics. Can be called as several ways:

        --------------------
        %d3
        This prints all avaiable releases hosted remotely at
        https://cdnjs.com/libraries/d3
        --------------------
        %%d3
        This cell loads the last available remote version of D3JS
        --------------------
        %%d3 "4.13.0"
        This cell loads a remote version (call '%d3' for see all available).
        --------------------
        %%d3 local="d3.v4.min.js"
        This cell loads a local file of the library
        --------------------
        %%d3 releases
        Same as line magics, print all available remote releases.
        --------------------
        """
        LOCAL_IMPORT = False

        if line == "":
            if cell != None:
                src = self.last_release
            else:
                return self.show_all_releases()
        else:
            if "releases" in line or "versions" in line:
                return self.show_all_releases()
            elif "local" in line:
                src = search(r'local="(.+)"\s*', line).group(1)
                LOCAL_IMPORT = True
            else:
                src = line

        if not LOCAL_IMPORT:
            src = "//cdnjs.cloudflare.com/ajax/libs/d3/%s/d3" % src

        s = """
<script>
requirejs.config({
    paths: {
        d3: '""" + src + """'
    }
});

require(['d3'], function(d3) {
    window.d3 = d3;
});
</script>
<script>
_select = d3.select;

d3.select""" + str(self.max_id) + """ = function(selection) {
    return _select("#d3-cell-""" + str(self.max_id) + """").select(selection);
}
d3.selectAll""" + str(self.max_id) + """ = function(selection) {
    return _select("#d3-cell-""" + str(self.max_id) + """").selectAll(selection);
}
</script>
<g id="d3-cell-""" + str(self.max_id) + """">
"""
        cell = sub('d3.select\((?!this)', "d3.select" + str(self.max_id) + "(", cell)
        cell = sub('d3.selectAll\((?!this)', "d3.selectAll" + str(self.max_id) + "(", cell)
        s += cell + "\n</g>"
        #print(s)  # Useful for debugging.
        h = HTML(s)
        self.max_id += 1
        display(h)


def load_ipython_extension(ipython):
    ip = ipython
    # ip = get_ipython()
    ip.register_magics(D3Magics)

if __name__ == "__main__":
    load_ipython_extension(get_ipython())
