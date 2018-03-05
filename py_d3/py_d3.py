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
from base64 import b64encode
try:
    from urllib.request import urlopen
    from urllib.error import HTTPError
except ImportError:  # Python2
    from urllib import urlopen

# Standard IPython libraries
from IPython.core.magic import (
    Magics,
    magics_class,
    line_cell_magic
)
from IPython.display import (
    HTML, 
    Javascript, 
    Markdown,
    display
)
from IPython.utils.py3compat import str_to_bytes, bytes_to_str
from IPython import get_ipython

# External IPython libraries
try:
    from ipywidgets import widgets
except ImportEror:
    USE_IPYWIDGETS = False
else:
    USE_IPYWIDGETS = True


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


class Renderer:
    def __init__(self, source_files):
        self.source_files = source_files

    def process_file(self, source_file):
        downloadable_exts = [".csv", ".json", ".svg"]

        for ext in downloadable_exts:
            if ext in source_file["name"]:
                if os.path.exists(source_file["name"]):
                    msg = "The %s file was to be downloaded but a file with the same name already exists."
                    return print("WARNING: %s" % (msg % source_file["name"]))
                    # TODO: Rename files marking every render with a individual uuid
                with open(source_file["name"], "w") as f:
                    f.write(source_file["content"])  # TODO: .csv files appears with an ineccesary jumpline at the end?
                print("%s downloaded sucessfully." % source_file["name"])
                return None

        # If the execution continues, we have a valid .js or .html file

        #print(source_file["content"])   # Useful for debugging

        # Sustitutions
        content = source_file["content"].replace('<body>', '<g id="body">')
        content = content.replace('("body', '("#body')
        print("\n---------------\n", content)   # Useful for debugging

        response = []
        match_map = {
            "style": False,
            "script": False,
            "svg": False,
            "canvas": False
        }

        for line in content.split("\n"):
            # CSS
            if "<style>" in line or match_map["style"]:
                if "body" in line:
                    line = line.replace("body", "#body")
                response.append(line)
                match_map["style"] = True
                if "</style>" in line:
                    match_map["style"] = False

            # Other libraries beyond D3 (D3 modules included)
            if '<script src=' in line:
                if "d3" in line:
                    if not search(r'd3\.v\d\.[min]*\.js', line):
                        response.append(line)
                else:
                    response.append(line)

            # Javascript
            if "<script>" in line or match_map["script"]:
                if '"body"' in line or "'body'" in line:
                    line = line.replace('body', '#body')
                if ".#body" in line:
                    line = line.replace(".#body", '.getElementById("body")')
                response.append(line)
                match_map["script"] = True
                if "</script>" in line:
                    match_map["script"] = False

            # SVG
            if "<svg" in line or match_map["svg"]:
                response.append(line)
                match_map["svg"] = True
                if "</svg>" in line:
                    match_map["svg"] = False

            # Canvas
            if "<canvas" in line or match_map["canvas"]:
                response.append(line)
                match_map["canvas"] = True
                if "</canvas>" in line:
                    match_map["canvas"] = False

            # Replaceds bodies with groups
            if '<g id="body">' in line or "</g>" in line:
                response.append(line)

        return "\n".join(response)

    def render(self):
        output = ""
        for source_file in self.source_files:
            _out = self.process_file(source_file)
            if _out:
                output += _out
        return output


@magics_class
class D3Magics(Magics):

    def __init__(self, **kwargs):
        super(D3Magics, self).__init__(**kwargs)
        self.max_id = 0  # Used to ensure that the current group selection is unique.
        self.src = None  # D3 main library source path.
        self.deps = {}   # D3 dependencies names with paths.
        self.verbose = False   # Print rendered internal javascript at cell execution
                               # Useful for debugging

        self._cdnjs_d3_source_template = "//cdnjs.cloudflare.com/ajax/libs/d3/%s/d3"
        self._cdnjs_api_url = "http://api.cdnjs.com/libraries/d3"
        self._blockbuilder_api_url = "http://blockbuilder.org/api/search?"

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

    def create_code_cell(self, code='', where='below'):
        """Create a code cell in the IPython Notebook.

        Parameters
        code: unicode
            Code to fill the new code cell with.
        where: unicode
            Where to add the new code cell.
            Possible values include:
                at_bottom
                above
                below"""

        encoded_code = bytes_to_str(b64encode(str_to_bytes(code)))
        jscode = """
            var code = IPython.notebook.insert_cell_{0}('code')
            code.set_text(atob("{1}"));
        """.format(where, encoded_code)
        return display(Javascript(jscode))

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
        """Returns version actually in use in the page."""
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

        LOCAL_IMPORT = False
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
            elif "examples" in line:
                line = line.replace("examples", "")
                return self.examples(line)
            elif "modules" in line and not "modules=" in line:
                return pprint(self.modules)
            elif "doc" in line or "docs" in line:
                line = line.replace("docs", "").replace("doc", "")
                return self.doc(line.strip(" ").strip('"').strip("'"))
            else:
                if "deps=" in line:   # Handle d3 dependencies
                    _deps = search(r'deps=({.+})', line)
                    if _deps:
                        deps = _deps.group(1)
                        self.deps = eval(deps)
                    line = line.replace("deps=%s" % deps, "")
                lineargs = line.split(" ")
                if lineargs[0] not in ["generator", ""]: # "generator" is not first param
                    line = line.strip('"')    # so is the source
                    if os.path.exists(line): # Local load
                        LOCAL_IMPORT = True
                    else:
                        if line not in self.online_releases:
                            raise ValueError(
                                "%s is not a valid cdnjs release" % line \
                                + " and is not found as a local file."
                            )
                        else:
                            version = line
                else:
                    version = self.last_release

        if not LOCAL_IMPORT:
            _src = self._cdnjs_d3_source_template % version
        else:
            _src = line

        if self.src != None:
            if _src != self.src:
                msg = "The first source of D3 used in this notebook is %s." % self.src \
                    + " You can't use different versions of D3 library in the" \
                    + " same Notebook. Please restart the kernel and load" \
                    + " your desired version at first."
                raise EnvironmentError(msg)
        else:
            self.src = _src

        if "generator" in line:   # Call like this: %%d3 "3.5.17" generator
            line = line.replace("generator", "")
            return self.generator(line)

        code = self._build_output_code(cell)
        if self.verbose:
            print(code)  # Useful for debugging.
        _html = HTML(code)
        self.max_id += 1
        display(_html)

    def examples(self, line="", generator=False):
        args = {
            "version": int(self.last_release[0]),
            "size": 512,
            "sort": "desc",
            "user": "",
            "modules": None
        }

        if line != "":           # Arguments parser
            for arg in args:
                if arg == "modules":  # Modules are passed as list
                    data = search(r'modules=(.+)\s*', line)
                    if data:
                        args[arg] = eval(data.group(1))
                else:
                    data = search(r'%s="*([^"\s]+)["\s]*' % arg, line)
                    if data:
                        args[arg] = data.group(1)

        # Url builder
        url = "%sd3version=v%d&size=%d&sort_dir=%s&user=%s" \
                % (self._blockbuilder_api_url,
                   int(args["version"]),
                   args["size"],
                   args["sort"],
                   args["user"])
        if args["modules"]:
            for mod in args["modules"]:
                url += "&d3modules=%s" % mod

        res = GET(url)

        blocks = []
        for hit in loads(res)["hits"]["hits"]:
            user = hit["_source"]["userId"]
            _id = hit["_id"]
            _block = {
                "description": hit["_source"]["description"],
                "user": user,
                "online_view": "%s/%s/%s" % ("http://blockbuilder.org", user, _id),
                "thumbnail": "http://gist.githubusercontent.com/%s/%s/raw/thumbnail.png" % (user, _id),
            }
            if generator:
                _block["source"] = "https://api.github.com/gists/%s" % _id
            blocks.append(_block)
        if generator:
            self._examples_cache = blocks

        def _render_row(data):
            try:
                data["description"] = "%s..." % data["description"][:50] \
                    if len(data["description"]) > 50 else data["description"]
            except TypeError:
                data["description"] = ""
            return '<td><a target="_blank" href="%s">%s</a></td>' % (data["online_view"], data["description"]) \
                   + '<td><img src="%s" width="70px" height="25px" alt=" "></d>' % data["thumbnail"] \
                   + '<td><a href="%s">%s</a></td>' % ("http://github.com/" + data["user"], data["user"]) \
                   + '<td><a button'

        _title = "<h3>D3 v%s online examples</h3>" % args["version"]
        _table = "\n".join(["<tr>%s</tr>" % _render_row(block) for block in blocks])

        _html = _title + '<table style="width:100%"><tr><th>Name</th>' \
              + '<th>Thumbnail</th><th>User</th></tr>''' + _table + '''</table>'''

        if USE_IPYWIDGETS:
            return widgets.HTML(value= _html)
        else:
            return display(HTML(_html))

    def generator(self, line=""):
        """Generates two tabs, the first with a text input and a button,
        the second with the list of examples returned by self.examples.

        You can insert an example name, push the button and the code
        will be rendered in a new cell.
        """
        if not USE_IPYWIDGETS:
            raise EnvironmentError(
                "You need to install ipywidgets if you want to" \
                + " use the code generator: pip install ipywidgets"
            )

        # Code generator widgets
        self._generator_text_input = widgets.Text(
            placeholder='Insert a example name and it will be rendered in a new cell.',
            layout=widgets.Layout(width='50%', height='80px')
        )
        input_example_button = widgets.Button(
            description='Generate',
            disabled=False,
            button_style='success',
            icon='code',
            layout=widgets.Layout(width='20%')
        )
        input_example_button.on_click(self._renderer)
        _input_example_tab = [
            self._generator_text_input,
            input_example_button
        ]
        input_example_tab = widgets.Box(children=_input_example_tab,
                                        layout=widgets.Layout(height="40px"))

        # Accordion tabs
        items = [input_example_tab, self.examples(line, generator=True)]
        tab_names = ['Code generator', 'Examples']

        gui = widgets.Accordion(children=items)
        for i, name in enumerate(tab_names):
            gui.set_title(i, name)
        return gui

    def load_github_gist(self, url,
                          valid_extensions=[".js", ".html", ".csv", ".json", ".svg"]):
        """Load a github gist and returns all files with their content.
        Only returns that files with an extension provided by the parameter
        ``valid_extensions``.
        """
        res = GET(url)
        _files = []
        for filename, filedata in loads(res)["files"].items():
            # print(filename)     # Useful for debugging
            for ext in valid_extensions:
                if ext in filename:
                    _files.append({
                        "name": filename,
                        "content": filedata["content"]
                    })
                    break
        return _files

    def _renderer(self, trigger):
        """Internal method for render a example name from the examples list.
        This method is called as callback from self.generator
        """
        example_name = self._generator_text_input.value
        block_found = False
        for block in self._examples_cache:
            if block["description"] == example_name:
                block_found = True
                break

        if not block_found:    # Handle bad requests
            raise ValueError("Example %s not founded." % example_name)

        #self._examples_cache = None  # Clean cache  TODO: Add argument cache=False

        _files = self.load_github_gist(block["source"])
        renderer = Renderer(_files)
        _html = renderer.render() #self._build_output_code(renderer.render())
        #print(_html)  # Useful for debugging
        self.create_code_cell("%%%%d3\n%s" % _html)
        
    def doc(self, line):
        """Returns D3 API documentation reference or from one
        module passed as argument."""
        module = "d3" if line == "" else line
        document = "API" if line == "" else "README"

        content = GET("https://raw.githubusercontent.com/d3/%s/master/%s.md" \
                      % (module, document)
        )

        # Link to documentation in title            
        repo_readme_url = "https://github.com/d3/%s/blob/master/%s.md" \
                              % (module, document)
        readme_title = "D3 API Reference" if line == "" else line
        content = content.replace(readme_title, 
                                 "[%s](%s)" % (readme_title, repo_readme_url))

        # Local references replacements
        output = []
        for line in content.split("\n"):
            local_refs = findall(r'(\(#[\w-]+\))', line)
            if len(local_refs) > 0:
                for local_ref in local_refs:
                    line = line.replace(local_ref,
                                        "(%s%s)" % (repo_readme_url, local_ref[1:-1]))
            output.append(line)                

        display(Markdown("\n".join(output)))

def load_ipython_extension(ipython):
    ip = ipython
    ipython.register_magics(D3Magics)

if __name__ == '__main__':
    load_ipython_extension(get_ipython())
