# -*- coding: utf-8 -*-

import os
from re import search, sub
from json import loads

from IPython.display import Markdown, display

class Book():
    def __init__(self, notebooks=[]):
        if len(notebooks) < 1:
            self.notebooks = sorted(self._notebooks())
        else:
            self.notebooks = notebooks

    def _notebooks(self):
        for root, dirs, notebooks in os.walk(os.getcwd()):
            break
        response = []
        for nb_name in notebooks:
            if os.path.splitext(nb_name)[1] == ".ipynb":
                response.append(nb_name)
        return response

    def index(self, max_depth=3):
        """Build an index obatining all Markdown titles cells."""
        output = ""
        for subtitle, nb_name in self.pages_tree:
            depth = subtitle.count("#")
            if depth <= max_depth:
                try:    # Notebooks title
                    output += "\n" + "#"*(depth+1) + ' <a href="%s" style="text-decoration:none;">**%s**</a>' \
                        % (nb_name, search(r'-\s(.+)</center>', subtitle).group(1))
                except AttributeError:
                    if depth == 2:
                        _list_ind = "-"
                        sep = ""
                    else:
                        _list_ind = "+"
                        sep = "    "
                    subtitle_clean = subtitle.split("#")[-1].strip("\n").strip(" ")
                    output += "%s%s " % (sep, _list_ind) \
                           + "#"*(depth+1) + ' <a href="%s" style="text-decoration:none">%s</a>' \
                               % (nb_name + "#" + subtitle_clean.replace(" ", "-"),
                                  subtitle_clean)
                output += "\n"
        display(Markdown(output))

    @property
    def pages_tree(self):
        subtitles_nb = []  # subtitle and file where it is from
        for nb_name in self.notebooks:
            with open(nb_name, "r") as f:
                content = loads(f.read())
            for i, (cell) in enumerate(content["cells"]):
                if len(cell["source"]) > 0:
                    subtitle = search(r'#+', cell["source"][0])
                    if subtitle:
                        subtitles_nb.append( [cell["source"][0],
                                           nb_name] )
        return subtitles_nb

    def chapter_title(self, notebook):
        with open(notebook, "r") as f:
            content = loads(f.read())
        return search(
            r'-\s(.+)</center>',
            content["cells"][0]["source"][0]
        ).group(1)

    def footer(self, page_number):
        """Build a convenient markdown notebooks paginator and index.

        Args:
             page_number (int): Number of the page of the notebook
                 from you call the method. """
        current_page_number = "%03d" % page_number
        previous_page_number = "%03d" % (page_number - 1)
        next_page_number = "%03d" % (page_number + 1)

        output = "\n_________________________\n"
        pagination = "### <center>"
        index = "### **Index**:\n"

        IS_FIRST_PAGE = True
        for i, nb_name in enumerate(sorted(self.notebooks)):
            index += '%s. <a href="%s" style="text-decoration:none">**%s**</a>\n' \
                         % (
                    search(r'\d+', self.chapter_title(nb_name)).group(0),
                    nb_name,
                    sub(r'[\d\.]+', '', self.chapter_title(nb_name)).strip(" ")
                )
            if previous_page_number in nb_name:
                IS_FIRST_PAGE = False
                pagination += "[⬅ %s](%s)" % ( self.chapter_title(nb_name), nb_name )
            if current_page_number in nb_name:
                if not IS_FIRST_PAGE:
                    pagination += " | "
                pagination += "%s" % self.chapter_title(nb_name)
                if IS_FIRST_PAGE:
                    pagination += " | "
            if next_page_number in nb_name:
                if not IS_FIRST_PAGE:
                    pagination += " | "
                pagination += "[%s ➡](%s)" % ( self.chapter_title(nb_name), nb_name )

        pagination += "</center>"
        output += "%s\n\n%s" % (pagination, index)

        display(Markdown(output))