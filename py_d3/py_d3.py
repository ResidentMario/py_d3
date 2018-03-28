# -*- coding: utf-8 -*-

# Standard Python libraries
from __future__ import print_function
import os
import sys
from re import (
    search,
    sub,
    findall
)
from json import loads
from pprint import pprint
try:
    from urllib.request import urlopen
except ImportError:  # Python2
    from urllib import urlopen

from IPython.core.magic import (
    Magics,
    magics_class,
    line_cell_magic
)
from IPython.display import (
    HTML,
    Markdown,
    display
)
from IPython import get_ipython


def GET(url):
    try:
        res = urlopen(url).read()
        if sys.version_info >= (3,0):
            res = res.decode()
    except Exception as e:
        print("Some error ocurred making HTTP request: %s" % str(e))
        print("URL: %s" % url)
        raise e
    else:
        return res


@magics_class
class D3Magics(Magics):

    def __init__(self, **kwargs):
        super(D3Magics, self).__init__(**kwargs)
        self.max_id = 0  # Used to ensure that the current group selection is unique.
        self.src = None  # D3 main library source path.
        self.verbose = False   # Print rendered internal javascript at cell execution
                               # Useful for debugging

        self._cdnjs_d3_source_template = "//cdnjs.cloudflare.com/ajax/libs/d3/%s/d3"
        self._cdnjs_api_url = "http://api.cdnjs.com/libraries/d3"

    def _build_output_code(self, cell):
        code_template = '''
<script>
requirejs.config({
    paths: {
        d3: "''' + self.src + '''"
    }
'''
        # TODO:
        # Dependencies injection. See:
        # https://stackoverflow.com/questions/39061334/whats-the-easy-way-to-load-d3-selection-multi-along-with-d3-v4-in-requirejs
        """
        if len(self.deps) > 0:
            for dep_name, pth in self.deps.items():
                code_template += ',\n        "%s": "%s"' % (dep_name, pth)
        code_template += "\n    }"

        if len(self.deps) > 0:
            code_template += ',\n    map: {\n        "*": {'
            for dep_name in self.deps:
                code_template += '\n            "%s": "d3",' % dep_name
            code_template = code_template[:-1]   # Last comma deleted
            code_template += "\n        }\n    }"
        """

        code_template += '''});

require(["d3"], function(d3) {
    window.d3 = d3;
});
</script>
<script>
_select = d3.select;

d3.select''' + str(self.max_id) + ''' = function(selection) {
    return _select("#d3-cell-''' + str(self.max_id) + '''").select(selection);
}
d3.selectAll''' + str(self.max_id) + ''' = function(selection) {
    return _select("#d3-cell-''' + str(self.max_id) + '''").selectAll(selection);
}
</script>

<g id="d3-cell-''' + str(self.max_id) + '''">
        '''
        cell = sub('d3.select\((?!this)', "d3.select" + str(self.max_id) + "(", cell)
        cell = sub('d3.selectAll\((?!this)', "d3.selectAll" + str(self.max_id) + "(", cell)
        return code_template + cell + "\n</g>"

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

    @property
    def online_releases(self):
        res = GET(self._cdnjs_api_url)
        return [asset["version"] for asset in loads(res)["assets"]]

    def show_online_releases(self):
        """Print all releases hosted at d3 cdnjs page."""
        for version in self.online_releases:
            print(version)

    @property
    def version(self):
        """Returns version actually in use in the current notebook."""
        if not self.src:
            return self.last_release
        else:
            response = search(r'(\d+\.\d+\.*\d*)', self.src)
            if not response:
                response = search(r'v(\d+)\.', self.src)
                if not response:
                    # If the user rename their local version
                    # with a strange name, returns unknown version
                    return "unknown"
                else:
                    return response.group(1)
            else:
                return response.group(1)

    @property
    def modules(self):
        """Return a list of D3 modules, used by examples filter."""
        try:
            return self._modules
        except AttributeError:
            res = GET("http://blockbuilder.org/api/aggregateD3Modules")
            self._modules =  [mod["key"] for mod in \
                loads(res)["aggregations"]["all_modules"]["buckets"]]
            return self._modules

    @line_cell_magic
    def d3(self, line="", cell=None):
        """D3 line and cell magics. Starting point for all commands."""

        LOCAL_IMPORT, INITIALIZED = (False, self.src != None)
        if "-v" in line or " -v" in line:
            self.verbose = True
            line = line.replace(" -v", "").replace("-v", "")
        else:
            self.verbose = False

        if line == "":
            if cell != None:
                version = self.last_release
            else:
                if "stable" in line:
                    return self.last_release   # Returns last stable version
                else:
                    return self.show_online_releases()
        else:
            if "releases" in line or "versions" in line:
                return self.show_online_releases()
            elif "version" in line and not "version=" in line:
                return print(self.version)
            elif "modules" in line and not "modules=" in line:
                return pprint(self.modules)
            elif "doc" in line or "docs" in line:
                line = line.replace("docs", "").replace("doc", "")
                return self.doc(line.strip(" ").strip('"').strip("'"))
            else:
                line = line.strip('"')
                if os.path.exists(line): # Local loading
                    LOCAL_IMPORT = True
                else:
                    if line not in self.online_releases:
                        raise ValueError(
                            "%s is not a valid cdnjs release" % line \
                            + " and is not found as a local file."
                        )
                    else:
                        version = line

        if not LOCAL_IMPORT:
            _src = self._cdnjs_d3_source_template % version
        else:
            _src = line

        if self.src != None:
            if _src != self.src and not INITIALIZED:
                msg = "The first source of D3 used in this notebook is %s." % self.src \
                    + " You can't use different versions of D3 library in the" \
                    + " same Notebook. Please restart the kernel and load" \
                    + " your desired version at first."
                raise EnvironmentError(msg)
        else:
            self.src = _src

        code = self._build_output_code(cell)
        if self.verbose:
            print(code)  # Useful for debugging.
        _html = HTML(code)
        self.max_id += 1
        display(_html)

    def doc(self, line):
        """Returns D3 general API documentation reference or
        from one D3 module passed as argument."""
        module = "d3" if line == "" else line
        document = "API" if line == "" else "README"

        content = GET("https://raw.githubusercontent.com/d3/%s/master/%s.md" \
                      % (module, document)
        )

        # Link to documentation in title
        repo_readme_url = "https://github.com/d3/%s/blob/master/%s.md" \
                              % (module, document)
        readme_title = "D3 API Reference" if line == "" else line

        content = content.splitlines()
        content[0] = content[0].replace(readme_title,
                                        "[%s](%s)" % (readme_title, repo_readme_url))

        # Local references replacements
        output = []
        for line in content:
            local_md_refs = findall(r'(\(#[^\s]+\))', line)  # Markdown links
            if len(local_md_refs) > 0:
                for local_ref in local_md_refs:
                    line = line.replace(local_ref,
                                        "(%s%s)" % (repo_readme_url, local_ref[1:-1]))
            local_html_refs = findall(r'("#[^\s]+")', line)  # HTML links
            if len(local_html_refs) > 0:
                for local_ref in local_html_refs:
                    line = line.replace(local_ref,
                                        '"%s%s"' % (repo_readme_url, local_ref[1:-1]))

            output.append(line)

        display(Markdown("\n".join(output)))


def load_ipython_extension(ipython):
    ip = ipython
    ip.register_magics(D3Magics)


if __name__ == "__main__":
    load_ipython_extension(get_ipython())
