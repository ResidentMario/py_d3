# This code can be put in any Python module, it does not require IPython
# itself to be running already.  It only creates the magics subclass but
# doesn't instantiate it yet.
from __future__ import print_function
from IPython.core.magic import (Magics, magics_class, line_magic,
                                cell_magic)  # , line_cell_magic)
from IPython.display import HTML, display
import re


# The class MUST call this class decorator at creation time
@magics_class
class D3Magics(Magics):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.max_id = 0  # Used to ensure that the current group selection is unique.
        # self.initialized = True  # Used to ensure that d3.js is only imported once.

    @line_magic
    def block(self, line):
        user, gist_id = line.split("/")[-2:]
        # TODO: The rest.

    @cell_magic
    def d3(self, line, cell):
        src = line if line else "3.5.17"
        if src[0] == "3":
            s = """
<script src="//cdnjs.cloudflare.com/ajax/libs/d3/""" + src + """/d3.js"></script>

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
        else:
            s = """"""  # TODO: Implement for D3 v. 4.#.#.
        # for start_ind, end_ind in [m.span() for m in re.finditer('d3.select\((?!this)', cell)]:
        #     print(cell[start_ind:end_ind])
        #     fragment = "d3.select" + str(self.max_id) + "("
        #     print("Fragment: " + fragment)
        #     cell = cell[:start_ind] + fragment + cell[end_ind + 1:]
        # cell = cell.replace("d3.select(", "d3.select" + str(self.max_id) + "(")
        # cell = cell.replace("d3.selectAll(", "d3.selectAll" + str(self.max_id) + "(")
        cell = re.sub('d3.select\((?!this)', "d3.select" + str(self.max_id) + "(", cell)
        s += cell + "\n</g>"
        print(s)
        h = HTML(s)
        self.max_id += 1
        display(h)

    # @line_cell_magic
    # def lcmagic(self, line, cell=None):
    #     "Magic that works both as %lcmagic and as %%lcmagic"
    #     if cell is None:
    #         print("Called as line magic")
    #         return line
    #     else:
    #         print("Called as cell magic")
    #         return line, cell


# In order to actually use these magics, you must register them with a
# running IPython.  This code must be placed in a file that is loaded once
# IPython is up and running:
ip = get_ipython()
# You can register the class itself without instantiating it.  IPython will
# call the default constructor on it.
ip.register_magics(D3Magics)